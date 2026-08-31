"""第 2 步：检索相关设定。

输入：planner 产出的「涉及项」（角色 / 地点 / 事件）
输出：事实清单（结构化 + 向量召回的设定，渲染为紧凑文本）
"""
from __future__ import annotations

from app.services.settings import build_fact_sheet


async def retrieve_facts(novel_id, plan: dict) -> str:
    """根据 planner 产出检索设定，组装事实清单。"""
    return await build_fact_sheet(
        novel_id=novel_id,
        character_names=plan.get("characters") or None,
        world_keywords=plan.get("locations") or None,
        timeline_keywords=plan.get("events") or None,
        query_text=plan.get("outline"),
    )
