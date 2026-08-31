"""审稿 / 一致性检查提示词。

输入：草稿 + 事实清单 + 前文上下文
输出：结构化 JSON —— issues（一般问题）/ conflicts（设定违背）/ summary

说明：用更便宜的审稿模型；发现冲突后回退生成器修正（见阶段四 pipeline）。
"""
from __future__ import annotations

SYSTEM = (
    "你是一名严格的审稿编辑，负责核对章节草稿与「事实清单」的一致性。\n\n"
    "检查维度：\n"
    "1. 角色一致性：角色语气、性格、称谓是否与设定一致。\n"
    "2. 剧情逻辑：情节因果是否合理，有无明显漏洞或前后矛盾。\n"
    "3. 设定违背：是否违背了事实清单中的角色 / 世界观 / 时间线设定。\n"
    "4. 文笔问题：明显语病、重复、错别字。\n\n"
    "只输出一个 JSON 对象，字段如下：\n"
    "{\n"
    '  "issues": ["一般问题（文笔 / 逻辑 / 语气等），每条一句话"],\n'
    '  "conflicts": ["与设定 / 事实清单违背的冲突，每条一句话"],\n'
    '  "summary": "总体评价，一句话"\n'
    "}\n"
    "若没有问题，issues 和 conflicts 均为空数组，summary 写「通过」。"
)


def build_review_messages(
    draft: str,
    fact_sheet: str | None,
    previous_context: str | None = None,
) -> list[dict]:
    """组装审稿请求消息。"""
    parts: list[str] = []
    if fact_sheet:
        parts.append(f"【事实清单】\n{fact_sheet}")
    if previous_context:
        parts.append(f"【前文上下文】\n{previous_context}")
    parts.append(f"【待审草稿】\n{draft}")
    parts.append("请审稿并输出上述 JSON。")
    return [{"role": "user", "content": "\n\n".join(parts)}]
