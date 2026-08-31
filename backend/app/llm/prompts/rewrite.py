"""章节局部重写提示词。

输入：待重写段落 + 前后文（供衔接）+ 修改指令（可选）
输出：重写后的段落正文（数量与原文一致，空行分隔）
"""
from __future__ import annotations

SYSTEM = (
    "你是一名网文编辑，负责按指令局部重写章节中的指定段落。\n\n"
    "要求：\n"
    "1. 保持与前后文的衔接，不改变人设、世界观和既有剧情。\n"
    "2. 严格按修改指令执行；若没有明确指令，就优化文笔、让段落更生动流畅。\n"
    "3. 只输出重写后的段落正文（数量与「待重写段落」一致，段落之间用空行分隔），不要输出任何解释或 Markdown。"
)


def build_rewrite_messages(
    target: str,
    before: str | None,
    after: str | None,
    instruction: str | None,
) -> list[dict]:
    """组装局部重写请求消息。"""
    parts: list[str] = []
    if instruction:
        parts.append(f"【修改指令】\n{instruction}")
    if before:
        parts.append(f"【前文（仅供衔接参考，不要修改）】\n{before}")
    parts.append(f"【待重写段落】\n{target}")
    if after:
        parts.append(f"【后文（仅供衔接参考，不要修改）】\n{after}")
    parts.append("请重写上述「待重写段落」，只输出重写后的正文：")
    return [{"role": "user", "content": "\n\n".join(parts)}]
