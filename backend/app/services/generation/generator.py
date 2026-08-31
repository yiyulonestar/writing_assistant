"""第 3 步：生成草稿。

输入：大纲 + 事实清单 + 前文上下文 + 目标字数
输出：本章正文草稿

说明：使用 generation_model（qwen3.5-flash）。审稿回退时，把审稿意见作为追加
消息注入，让模型按冲突清单重写。
"""
from __future__ import annotations

from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.prompts import generation


def _format_revision_note(review: dict) -> str:
    lines: list[str] = []
    if review.get("conflicts"):
        lines.append("必须修正的设定冲突：")
        lines += [f"- {c}" for c in review["conflicts"]]
    if review.get("issues"):
        lines.append("建议修正的问题：")
        lines += [f"- {i}" for i in review["issues"]]
    return "\n".join(lines)


async def generate_draft(
    outline: str,
    fact_sheet: str | None,
    previous_context: str | None = None,
    target_word_count: int = 3000,
    review: dict | None = None,
) -> str:
    """携带事实清单生成草稿；review 非空时按审稿意见修正重写。"""
    messages = generation.build_generation_messages(
        outline, fact_sheet, previous_context, target_word_count
    )
    if review:
        note = _format_revision_note(review)
        if note:
            messages.append(
                {"role": "user", "content": f"上一版审稿发现以下问题，请在本次重写时修正：\n{note}"}
            )
    max_tokens = max(2048, target_word_count * 2)
    return await LLMClient(model=settings.generation_model).complete(
        messages, system=generation.SYSTEM, temperature=0.8, max_tokens=max_tokens
    )
