"""章节局部重写服务：按段落范围重写，保持前后文衔接。"""
from __future__ import annotations

from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.prompts import rewrite

_CONTEXT_PARAGRAPHS = 1  # 前后文各取的段落数（供衔接参考）


def _split_paragraphs(content: str) -> list[str]:
    """按空行拆分为段落（保留段内换行），过滤空段。"""
    return [p.strip() for p in content.split("\n\n") if p.strip()]


async def rewrite_paragraphs(
    content: str,
    start: int,
    end: int,
    instruction: str | None = None,
) -> str:
    """重写 [start, end] 段落（含边界，0 起，按空行分段），返回新的完整正文。"""
    paragraphs = _split_paragraphs(content)
    if start < 0 or end < start or end >= len(paragraphs):
        raise ValueError(f"段落范围越界：start={start} end={end}，共 {len(paragraphs)} 段")

    target = "\n\n".join(paragraphs[start : end + 1])
    before = "\n\n".join(paragraphs[max(0, start - _CONTEXT_PARAGRAPHS) : start]) or None
    after = "\n\n".join(paragraphs[end + 1 : end + 1 + _CONTEXT_PARAGRAPHS]) or None

    messages = rewrite.build_rewrite_messages(target, before, after, instruction)
    rewritten = await LLMClient(model=settings.generation_model).complete(
        messages, system=rewrite.SYSTEM, temperature=0.7
    )

    new_paragraphs = (
        paragraphs[:start] + _split_paragraphs(rewritten) + paragraphs[end + 1 :]
    )
    return "\n\n".join(new_paragraphs)
