"""LangGraph 多 Agent 编排：planner → retriever → writer → reviewer（条件回退）→ 落库。

复用 services/generation 下的确定性组件作为节点，StateGraph 提供：
- 共享状态管理（novel_id / chapter_number / plan / facts / draft / review / round）
- 条件路由：审稿有冲突且未达轮次上限 → 回退 writer 修正；否则 → 落库
- checkpointer 断点续跑（按 thread_id 隔离，可恢复 / 回溯）
"""
from __future__ import annotations

import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.models.chapter import Chapter, ChapterDraft
from app.models.novel import Novel
from app.services.generation.generator import generate_draft
from app.services.generation.planner import plan_chapter
from app.services.generation.retriever import retrieve_facts
from app.services.generation.reviewer import review_draft
from app.services.stats import basic_stats
from app.services.summary import generate_summary

_PREVIOUS_CONTEXT_LIMIT = 3000


class AgentState(TypedDict, total=False):
    # 输入
    novel_id: str
    chapter_number: int
    outline: str | None
    target_word_count: int
    # 上下文
    synopsis: str | None
    previous_summary: str | None
    previous_context: str | None
    # 中间产物
    plan: dict
    facts: str
    draft: str
    review: dict
    round: int
    # 产出
    chapter_id: str | None


def _previous_context(previous: Chapter | None) -> str | None:
    if previous is None or not previous.content:
        return None
    return previous.content[-_PREVIOUS_CONTEXT_LIMIT:]


async def _load_context(state: AgentState) -> dict:
    novel = await Novel.get_or_none(id=uuid.UUID(state["novel_id"]))
    if novel is None:
        raise ValueError(f"Novel not found: {state['novel_id']}")
    previous = (
        await Chapter.filter(
            novel_id=novel.id, number__lt=state["chapter_number"]
        )
        .order_by("-number")
        .first()
    )
    return {
        "synopsis": novel.synopsis,
        "previous_summary": previous.summary if previous else None,
        "previous_context": _previous_context(previous),
    }


async def _planner(state: AgentState) -> dict:
    plan = await plan_chapter(
        state.get("synopsis"),
        state.get("previous_summary"),
        state.get("outline"),
        state["chapter_number"],
    )
    return {"plan": plan}


async def _retriever(state: AgentState) -> dict:
    facts = await retrieve_facts(uuid.UUID(state["novel_id"]), state["plan"])
    return {"facts": facts}


async def _writer(state: AgentState) -> dict:
    draft = await generate_draft(
        state["plan"]["outline"],
        state["facts"],
        state.get("previous_context"),
        state.get("target_word_count", 3000),
        review=state.get("review"),
    )
    return {"draft": draft}


async def _reviewer(state: AgentState) -> dict:
    review = await review_draft(state["draft"], state["facts"], state.get("previous_context"))
    return {"review": review, "round": state.get("round", 0) + 1}


async def _persist(state: AgentState) -> dict:
    novel_id = uuid.UUID(state["novel_id"])
    content = state["draft"]
    word_count = basic_stats(content)["word_count"]
    chapter = await Chapter.get_or_none(novel_id=novel_id, number=state["chapter_number"])
    if chapter is None:
        chapter = await Chapter.create(
            novel_id=novel_id,
            number=state["chapter_number"],
            outline=state["plan"].get("outline"),
            content=content,
            word_count=word_count,
            status="draft",
        )
    else:
        chapter.outline = state["plan"].get("outline")
        chapter.content = content
        chapter.word_count = word_count
        await chapter.save()

    last = await ChapterDraft.filter(chapter_id=chapter.id).order_by("-version").first()
    version = (last.version + 1) if last else 1
    await ChapterDraft.create(
        chapter_id=chapter.id, version=version, content=content, note="生成"
    )

    chapter.summary = await generate_summary(
        state.get("synopsis"), state.get("previous_summary"), content
    )
    await chapter.save()
    return {"chapter_id": str(chapter.id)}


def build_graph(max_review_rounds: int = 3, checkpointer=None):
    """构建并编译章节生成 Agent 图。"""
    builder = StateGraph(AgentState)

    def route_after_review(state: AgentState) -> str:
        review = state.get("review") or {}
        if review.get("conflicts") and state.get("round", 0) < max_review_rounds:
            return "writer"
        return "persist"

    builder.add_node("load_context", _load_context)
    builder.add_node("planner", _planner)
    builder.add_node("retriever", _retriever)
    builder.add_node("writer", _writer)
    builder.add_node("reviewer", _reviewer)
    builder.add_node("persist", _persist)

    builder.add_edge(START, "load_context")
    builder.add_edge("load_context", "planner")
    builder.add_edge("planner", "retriever")
    builder.add_edge("retriever", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_conditional_edges(
        "reviewer", route_after_review, {"writer": "writer", "persist": "persist"}
    )
    builder.add_edge("persist", END)

    return builder.compile(checkpointer=checkpointer)


# 默认图：内存 checkpointer，支持同进程内按 thread_id 断点续跑 / 回溯
graph = build_graph(checkpointer=MemorySaver())
