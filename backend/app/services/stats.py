"""文本统计工具（确定性计算，不调用 LLM）。

统计：字数（中文字符数）、段落数、对话行数、章节节奏等。
生成/审稿时作为工具按需调用。
"""
from __future__ import annotations

import re

_CJK = re.compile(r"[一-鿿]")


def count_words(text: str) -> int:
    """中文字符数（网文按字符计字）。"""
    return len(_CJK.findall(text or ""))


def basic_stats(text: str) -> dict:
    """基础统计：总字符数、字数、段落数、对话行数、对话占比。"""
    text = text or ""
    paragraphs = [p for p in text.splitlines() if p.strip()]
    dialogue_lines = [p for p in paragraphs if re.search(r"[“”「」]", p)]
    return {
        "chars": len(text),
        "word_count": count_words(text),
        "paragraphs": len(paragraphs),
        "dialogue_lines": len(dialogue_lines),
        "dialogue_ratio": round(len(dialogue_lines) / len(paragraphs), 4) if paragraphs else 0.0,
    }
