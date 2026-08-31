"""前文摘要服务：为已完成章节生成滚动摘要，供 planner 使用。"""
from __future__ import annotations

from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.prompts import summary


async def generate_summary(
    synopsis: str | None,
    previous_summary: str | None,
    chapter_content: str,
) -> str:
    """生成更新后的前文摘要。"""
    messages = summary.build_summary_messages(synopsis, previous_summary, chapter_content)
    return await LLMClient(model=settings.generation_model).complete(
        messages, system=summary.SYSTEM, temperature=0.3, max_tokens=800
    )
