"""第 4 步：审稿 / 一致性检查。

输入：草稿 + 事实清单 + 前文上下文
输出：冲突列表（issues / conflicts / summary）

说明：用 review_model（qwen3.6-35b-a3b）；发现冲突后由 pipeline 回退 generator 修正。
"""
from __future__ import annotations

from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.prompts import review
from app.utils.text import extract_json


async def review_draft(
    draft: str,
    fact_sheet: str | None,
    previous_context: str | None = None,
) -> dict:
    """审稿，返回 {issues, conflicts, summary}。"""
    messages = review.build_review_messages(draft, fact_sheet, previous_context)
    raw = await LLMClient(model=settings.review_model).complete(
        messages, system=review.SYSTEM, temperature=0.2
    )
    rep = extract_json(raw)
    if not isinstance(rep, dict):
        # 解析失败按通过处理，避免流程卡死在审稿环节
        return {"issues": [], "conflicts": [], "summary": "审稿解析失败，按通过处理"}
    return {
        "issues": rep.get("issues") or [],
        "conflicts": rep.get("conflicts") or [],
        "summary": rep.get("summary") or "",
    }
