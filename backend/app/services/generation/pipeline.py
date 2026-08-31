"""章节生成流水线（核心编排）。

流程（确定性流水线，模型只在需要语言能力的环节介入）：
  1. planner    —— 拆解章节目标 → 大纲 + 涉及角色 / 地点 / 事件
  2. retriever  —— 根据涉及项检索设定 → 事实清单
  3. generator  —— 携带事实清单生成草稿
  4. reviewer   —— 审稿：核对角色语气、剧情逻辑，输出冲突
  5. 有冲突则回退 generator 修正（循环上限 max_review_rounds），最终落库
  6. 生成章节摘要（供下一章 planner 使用）
"""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import HTTPException

from app.models.chapter import Chapter, ChapterDraft
from app.models.novel import Novel
from app.services.generation.generator import generate_draft
from app.services.generation.planner import plan_chapter
from app.services.generation.retriever import retrieve_facts
from app.services.generation.reviewer import review_draft
from app.services.stats import basic_stats
from app.services.summary import generate_summary

_PREVIOUS_CONTEXT_LIMIT = 3000  # 前文注入的最大字符数（避免 token 爆炸）

Progress = Callable[[dict], Awaitable[None]]


def _previous_context(previous: Chapter | None) -> str | None:
    if previous is None or not previous.content:
        return None
    return previous.content[-_PREVIOUS_CONTEXT_LIMIT:]


class GenerationPipeline:
    def __init__(self, max_review_rounds: int = 3) -> None:
        self.max_review_rounds = max_review_rounds

    async def _progress(self, on_progress: Progress | None, stage: str, **data) -> None:
        if on_progress is not None:
            await on_progress({"stage": stage, **data})

    async def generate(
        self,
        novel_id: uuid.UUID,
        chapter_number: int,
        outline: str | None = None,
        target_word_count: int = 3000,
        on_progress: Progress | None = None,
    ) -> dict:
        novel = await Novel.get_or_none(id=novel_id)
        if novel is None:
            raise HTTPException(status_code=404, detail="Novel not found")

        previous = (
            await Chapter.filter(novel_id=novel_id, number__lt=chapter_number)
            .order_by("-number")
            .first()
        )
        previous_context = _previous_context(previous)
        previous_summary = previous.summary if previous else None

        # 1. 拆解
        await self._progress(on_progress, "planning", chapter=chapter_number)
        plan = await plan_chapter(novel.synopsis, previous_summary, outline, chapter_number)

        # 2. 检索事实清单
        await self._progress(on_progress, "retrieving", chapter=chapter_number)
        fact_sheet = await retrieve_facts(novel_id, plan)

        # 3. 生成草稿
        await self._progress(on_progress, "generating", chapter=chapter_number)
        draft = await generate_draft(
            plan["outline"], fact_sheet, previous_context, target_word_count
        )

        # 4. 审稿 + 回退修正
        review: dict = {"issues": [], "conflicts": [], "summary": ""}
        for round_no in range(self.max_review_rounds):
            await self._progress(on_progress, "reviewing", chapter=chapter_number, round=round_no + 1)
            review = await review_draft(draft, fact_sheet, previous_context)
            if not review.get("conflicts"):
                break
            await self._progress(on_progress, "revising", chapter=chapter_number, round=round_no + 1)
            draft = await generate_draft(
                plan["outline"], fact_sheet, previous_context, target_word_count, review=review
            )

        # 5. 落库
        await self._progress(on_progress, "persisting", chapter=chapter_number)
        chapter = await self._persist(novel_id, chapter_number, plan, draft)

        # 6. 生成章节摘要（供下一章 planner 使用）
        await self._progress(on_progress, "summarizing", chapter=chapter_number)
        chapter.summary = await generate_summary(novel.synopsis, previous_summary, draft)
        await chapter.save()

        await self._progress(
            on_progress, "done", chapter=chapter_number, chapter_id=str(chapter.id)
        )
        return {
            "chapter_id": chapter.id,
            "content": draft,
            "word_count": chapter.word_count,
            "review": review,
        }

    async def generate_many(
        self,
        novel_id: uuid.UUID,
        start_chapter: int,
        count: int,
        target_word_count: int = 3000,
        outlines: list[str] | None = None,
        on_progress: Progress | None = None,
    ) -> list[dict]:
        """批量生成连续章节（每章串行，依次复用前文摘要）。"""
        results: list[dict] = []
        for i in range(count):
            number = start_chapter + i
            outline = outlines[i] if outlines and i < len(outlines) else None
            results.append(
                await self.generate(
                    novel_id, number, outline, target_word_count, on_progress
                )
            )
        return results

    async def _persist(
        self, novel_id: uuid.UUID, chapter_number: int, plan: dict, content: str
    ) -> Chapter:
        word_count = basic_stats(content)["word_count"]
        chapter = await Chapter.get_or_none(novel_id=novel_id, number=chapter_number)
        if chapter is None:
            chapter = await Chapter.create(
                novel_id=novel_id,
                number=chapter_number,
                outline=plan.get("outline"),
                content=content,
                word_count=word_count,
                status="draft",
            )
        else:
            chapter.outline = plan.get("outline")
            chapter.content = content
            chapter.word_count = word_count
            await chapter.save()

        # 草稿版本历史
        last = await ChapterDraft.filter(chapter_id=chapter.id).order_by("-version").first()
        version = (last.version + 1) if last else 1
        await ChapterDraft.create(
            chapter_id=chapter.id, version=version, content=content, note="生成"
        )
        return chapter
