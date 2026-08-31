"""章节正文生成提示词。

输入：大纲 + 事实清单 + 前文上下文 + 目标字数
输出：本章正文草稿

说明：事实清单作为「必须遵守的事实」注入，用于一致性约束。
"""
from __future__ import annotations

SYSTEM = (
    "你是一名网文 / 长篇小说作者，负责根据大纲和「事实清单」撰写一章正文。\n\n"
    "写作规则：\n"
    "1. 「事实清单」是必须遵守的事实：角色性格、称谓、世界观、时间线等都必须与之保持一致，不得违背或擅自改动。\n"
    "2. 严格围绕本章大纲推进剧情，不要偏离目标，也不要引入事实清单之外的重大新设定。\n"
    "3. 语言流畅有画面感，符合网文节奏；对话、动作、心理描写自然，避免啰嗦和重复。\n"
    "4. 只输出正文正文，不要输出任何解释、章节标题、序号或 Markdown 标记。"
)


def build_generation_messages(
    outline: str,
    fact_sheet: str | None,
    previous_context: str | None = None,
    target_word_count: int | None = None,
) -> list[dict]:
    """组装正文生成的请求消息。"""
    parts: list[str] = [f"【本章大纲】\n{outline}"]
    if fact_sheet:
        parts.append(f"【事实清单（必须遵守）】\n{fact_sheet}")
    if previous_context:
        parts.append(f"【前文上下文】\n{previous_context}")
    if target_word_count:
        parts.append(f"【目标字数】约 {target_word_count} 字")
    parts.append("请开始撰写本章正文：")
    return [{"role": "user", "content": "\n\n".join(parts)}]
