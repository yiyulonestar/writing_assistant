"""章节生成接口：接入 services/generation 流水线 + LangGraph 多 Agent。"""
import uuid

from fastapi import APIRouter, Depends

from app.agents.graph import graph
from app.api.deps import require_api_key
from app.schemas.generation import (
    GenerateChapterRequest,
    GenerateChapterResponse,
    GenerateChaptersRequest,
    ReviewReport,
)
from app.services.generation.pipeline import GenerationPipeline
from app.services.stats import basic_stats

router = APIRouter(dependencies=[Depends(require_api_key)])


def _to_response(result: dict) -> GenerateChapterResponse:
    review = result["review"]
    return GenerateChapterResponse(
        chapter_id=result["chapter_id"],
        content=result["content"],
        word_count=result["word_count"],
        review=ReviewReport(
            issues=review.get("issues", []),
            conflicts=review.get("conflicts", []),
            fixed=not review.get("conflicts"),
            summary=review.get("summary"),
        ),
    )


@router.post("/chapter", response_model=GenerateChapterResponse)
async def generate_chapter(payload: GenerateChapterRequest) -> GenerateChapterResponse:
    result = await GenerationPipeline().generate(
        novel_id=payload.novel_id,
        chapter_number=payload.chapter_number,
        outline=payload.outline,
        target_word_count=payload.target_word_count,
    )
    return _to_response(result)


@router.post("/agent", response_model=GenerateChapterResponse)
async def generate_chapter_agent(
    payload: GenerateChapterRequest, thread_id: str | None = None
) -> GenerateChapterResponse:
    """多 Agent 入口：走 LangGraph（可断点续跑，thread_id 用于隔离/恢复）。"""
    config = {
        "configurable": {
            "thread_id": thread_id or f"{payload.novel_id}-{payload.chapter_number}"
        }
    }
    result = await graph.ainvoke(
        {
            "novel_id": str(payload.novel_id),
            "chapter_number": payload.chapter_number,
            "outline": payload.outline,
            "target_word_count": payload.target_word_count,
        },
        config=config,
    )
    review = result.get("review") or {}
    return GenerateChapterResponse(
        chapter_id=uuid.UUID(result["chapter_id"]),
        content=result["draft"],
        word_count=basic_stats(result["draft"])["word_count"],
        review=ReviewReport(
            issues=review.get("issues", []),
            conflicts=review.get("conflicts", []),
            fixed=not review.get("conflicts"),
            summary=review.get("summary"),
        ),
    )


@router.post("/batch", response_model=list[GenerateChapterResponse])
async def generate_chapters(
    payload: GenerateChaptersRequest,
) -> list[GenerateChapterResponse]:
    """批量生成连续章节（串行，每章依次复用前文摘要）。"""
    results = await GenerationPipeline().generate_many(
        novel_id=payload.novel_id,
        start_chapter=payload.start_chapter,
        count=payload.count,
        target_word_count=payload.target_word_count,
        outlines=payload.outlines,
    )
    return [_to_response(r) for r in results]
