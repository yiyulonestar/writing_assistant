"""章节目标拆解提示词。

输入：全书简介 + 前文摘要 + 用户给定大纲（可选）
输出：结构化 JSON —— 本章大纲 / 涉及角色 / 涉及地点 / 涉及事件 / 情绪基调
"""
from __future__ import annotations

SYSTEM = (
    "你是一名资深网文 / 长篇小说的大纲策划。"
    "你的任务是把一章的写作目标拆解成可执行的结构化计划，供后续写作与设定检索使用。\n\n"
    "要求：\n"
    "1. 只输出一个 JSON 对象，不要输出任何解释、Markdown 代码块或多余文字。\n"
    "2. JSON 字段：\n"
    "   - outline：本章大纲（2~4 句，交代本章要发生什么、如何推进主线）\n"
    "   - characters：本章出场角色名列表（尽量用设定中已有的名字）\n"
    "   - locations：本章涉及的地点 / 场景列表\n"
    "   - events：本章发生的关键事件列表\n"
    "   - mood：本章情绪基调（如：热血 / 压抑 / 温馨 / 紧张 / 悲壮 / 幽默）\n"
    "3. 角色名、地名、事件尽量复用已有专有名词，不要凭空捏造新设定。"
)


def build_planning_messages(
    synopsis: str | None,
    previous_summary: str | None,
    user_outline: str | None = None,
    chapter_number: int | None = None,
) -> list[dict]:
    """组装拆解章节目标的请求消息。"""
    parts: list[str] = []
    if chapter_number is not None:
        parts.append(f"【章节】第 {chapter_number} 章")
    if synopsis:
        parts.append(f"【全书简介】\n{synopsis}")
    if previous_summary:
        parts.append(f"【前文摘要】\n{previous_summary}")
    if user_outline:
        parts.append(f"【用户给定的大纲 / 目标】\n{user_outline}")
    parts.append("请拆解本章的写作目标，按上述结构输出 JSON。")
    return [{"role": "user", "content": "\n\n".join(parts)}]
