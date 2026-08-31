"""小说接口 —— 完整 CRUD 竖切示例，其余模块照此模式补全。"""
import uuid

from fastapi import APIRouter, HTTPException, status

from app.models.novel import Novel
from app.schemas.novel import NovelCreate, NovelRead, NovelUpdate

router = APIRouter()


@router.post("", response_model=NovelRead, status_code=status.HTTP_201_CREATED)
async def create_novel(payload: NovelCreate) -> NovelRead:
    novel = await Novel.create(**payload.model_dump())
    return NovelRead.model_validate(novel)


@router.get("", response_model=list[NovelRead])
async def list_novels() -> list[NovelRead]:
    rows = await Novel.all().order_by("-created_at").values()
    return [NovelRead(**r) for r in rows]


@router.get("/{novel_id}", response_model=NovelRead)
async def get_novel(novel_id: uuid.UUID) -> NovelRead:
    novel = await Novel.get_or_none(id=novel_id)
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    return NovelRead.model_validate(novel)


@router.patch("/{novel_id}", response_model=NovelRead)
async def update_novel(novel_id: uuid.UUID, payload: NovelUpdate) -> NovelRead:
    novel = await Novel.get_or_none(id=novel_id)
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    novel.update_from_dict(payload.model_dump(exclude_unset=True))
    await novel.save()
    return NovelRead.model_validate(novel)


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(novel_id: uuid.UUID) -> None:
    deleted = await Novel.filter(id=novel_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Novel not found")
