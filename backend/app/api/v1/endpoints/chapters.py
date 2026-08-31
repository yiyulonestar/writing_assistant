"""章节接口：CRUD + 草稿版本历史 + 局部重写 + 版本对比。"""
import difflib
import uuid

from fastapi import APIRouter, HTTPException, status

from app.models.chapter import Chapter, ChapterDraft
from app.schemas.chapter import (
    ChapterCreate,          # 创建章节请求模型
    ChapterRead,            # 读取章节响应模型
    ChapterUpdate,          # 更新章节请求模型
    DraftCreate,            # 创建草稿请求模型
    DraftDiff,              # 对比草稿版本请求模型
    DraftRead,              # 读取草稿版本响应模型
    RewriteRequest,         # 局部重写请求模型
)
from app.services.generation.rewriter import rewrite_paragraphs
from app.services.stats import basic_stats

router = APIRouter()

@router.get("", response_model=list[ChapterRead])
async def list_chapters(novel_id: uuid.UUID) -> list[ChapterRead]:
    rows = await Chapter.filter(novel_id=novel_id).order_by("number").values()
    return [ChapterRead(**r) for r in rows]


@router.post("", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
async def create_chapter(payload: ChapterCreate) -> ChapterRead:
    data = payload.model_dump()
    if data.get("content") and not data.get("word_count"):
        data["word_count"] = basic_stats(data["content"])["word_count"]
    chapter = await Chapter.create(**data)
    return ChapterRead.model_validate(chapter)


@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter(chapter_id: uuid.UUID) -> ChapterRead:
    chapter = await Chapter.get_or_none(id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterRead.model_validate(chapter)


@router.patch("/{chapter_id}", response_model=ChapterRead)
async def update_chapter(chapter_id: uuid.UUID, payload: ChapterUpdate) -> ChapterRead:
    chapter = await Chapter.get_or_none(id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    data = payload.model_dump(exclude_unset=True)
    if "content" in data and "word_count" not in data:
        data["word_count"] = basic_stats(data["content"])["word_count"]
    chapter.update_from_dict(data)
    await chapter.save()
    return ChapterRead.model_validate(chapter)


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(chapter_id: uuid.UUID) -> None:
    deleted = await Chapter.filter(id=chapter_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Chapter not found")

# ---- 草稿版本历史 ----
@router.get("/{chapter_id}/drafts", response_model=list[DraftRead])
async def list_drafts(chapter_id: uuid.UUID) -> list[DraftRead]:
    rows = await ChapterDraft.filter(chapter_id=chapter_id).order_by("version").values()
    return [DraftRead(**r) for r in rows]

@router.post("/{chapter_id}/drafts", response_model=DraftRead, status_code=status.HTTP_201_CREATED)
async def create_draft(chapter_id: uuid.UUID, payload: DraftCreate) -> DraftRead:
    chapter = await Chapter.get_or_none(id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    last = await ChapterDraft.filter(chapter_id=chapter_id).order_by("-version").first()
    next_version = (last.version + 1) if last else 1
    draft = await ChapterDraft.create(
        chapter_id=chapter_id, version=next_version, **payload.model_dump()
    )
    return DraftRead.model_validate(draft)

@router.get("/{chapter_id}/drafts/{version}", response_model=DraftRead)
async def get_draft(chapter_id: uuid.UUID, version: int) -> DraftRead:
    draft = await ChapterDraft.get_or_none(chapter_id=chapter_id, version=version)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return DraftRead.model_validate(draft)


@router.get("/{chapter_id}/drafts/{version}/diff", response_model=DraftDiff)
async def diff_drafts(chapter_id: uuid.UUID, version: int, base: int) -> DraftDiff:
    """对比两个草稿版本，返回 unified diff。"""
    target = await ChapterDraft.get_or_none(chapter_id=chapter_id, version=version)
    base_draft = await ChapterDraft.get_or_none(chapter_id=chapter_id, version=base)
    if target is None or base_draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    diff = list(
        difflib.unified_diff(
            base_draft.content.splitlines(),
            target.content.splitlines(),
            fromfile=f"v{base}",
            tofile=f"v{version}",
            lineterm="",
        )
    )
    return DraftDiff(from_version=base, to_version=version, diff=diff)


# ---- 局部重写 ----
@router.post("/{chapter_id}/rewrite", response_model=ChapterRead)
async def rewrite_chapter(chapter_id: uuid.UUID, payload: RewriteRequest) -> ChapterRead:
    chapter = await Chapter.get_or_none(id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if not chapter.content:
        raise HTTPException(status_code=400, detail="章节暂无正文")

    try:
        new_content = await rewrite_paragraphs(
            chapter.content, payload.start, payload.end, payload.instruction
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chapter.content = new_content
    chapter.word_count = basic_stats(new_content)["word_count"]
    await chapter.save()

    last = await ChapterDraft.filter(chapter_id=chapter_id).order_by("-version").first()
    version = (last.version + 1) if last else 1
    note = payload.instruction or f"局部重写 [{payload.start}-{payload.end}]"
    await ChapterDraft.create(
        chapter_id=chapter_id, version=version, content=new_content, note=note
    )
    return ChapterRead.model_validate(chapter)
