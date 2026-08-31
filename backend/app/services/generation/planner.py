"""第 1 步：拆解章节目标。

输入：全书简介 + 前文摘要 + 用户给定大纲（可选）
输出：本章大纲、涉及角色、涉及地点 / 事件、情绪基调
"""
from __future__ import annotations

from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.prompts import planning
from app.utils.text import extract_json


async def plan_chapter(
    synopsis: str | None,
    previous_summary: str | None,
    user_outline: str | None = None,
    chapter_number: int | None = None,
) -> dict:
    """调用 LLM 拆解章节目标，返回结构化结果（outline/characters/locations/events/mood）。"""
    messages = planning.build_planning_messages(
        synopsis, previous_summary, user_outline, chapter_number
    )
    raw = await LLMClient(model=settings.generation_model).complete(
        messages, system=planning.SYSTEM, temperature=0.4
    )
    plan = extract_json(raw)
    if not isinstance(plan, dict):
        # 解析失败时降级：用用户大纲兜底，避免流程中断
        return {
            "outline": user_outline or "按前文自然推进本章剧情",
            "characters": [],
            "locations": [],
            "events": [],
            "mood": "",
        }
    return plan
