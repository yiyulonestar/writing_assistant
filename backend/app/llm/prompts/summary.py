"""前文摘要提示词。

输入：全书简介 + 此前摘要（可选）+ 本章正文
输出：更新后的前文摘要（供后续章节 planner 使用）
"""
from __future__ import annotations

SYSTEM = (
    "你是一名网文编辑，负责为已完成章节生成简明的前文摘要，供后续章节创作时参考。\n\n"
    "要求：\n"
    "1. 突出主线进展、关键事件、角色状态变化。\n"
    "2. 控制在 200 字以内，用第三人称叙述。\n"
    "3. 只输出摘要正文，不要任何解释或 Markdown。"
)


def build_summary_messages(
    synopsis: str | None,
    previous_summary: str | None,
    chapter_content: str,
) -> list[dict]:
    """组装前文摘要请求消息。"""
    parts: list[str] = []
    if synopsis:
        parts.append(f"【全书简介】\n{synopsis}")
    if previous_summary:
        parts.append(f"【此前摘要】\n{previous_summary}")
    parts.append(f"【本章正文】\n{chapter_content}")
    parts.append("请生成本章更新后的前文摘要：")
    return [{"role": "user", "content": "\n\n".join(parts)}]
