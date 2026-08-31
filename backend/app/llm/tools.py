"""工具定义（供生成 / 审稿时按需调用）。

- text_stats：字数、段落、对话占比等本地确定性统计（见 app/services/stats.py）
- web_search：百科 / 词典检索（后续接 DashScope 插件或外部搜索 API）
"""
from __future__ import annotations

from app.services.stats import basic_stats

TEXT_STATS_TOOL = {
    "type": "function",
    "function": {
        "name": "text_stats",
        "description": "统计文本的字数（中文字符数）、段落数、对话行数、对话占比。",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要统计的文本"},
            },
            "required": ["text"],
        },
    },
}

WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "检索百科 / 词典补充背景知识。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词"},
            },
            "required": ["query"],
        },
    },
}

# 暴露给 LLM 的工具列表（注入 chat.completions 的 tools 参数）
TOOLS = [TEXT_STATS_TOOL, WEB_SEARCH_TOOL]


def call_tool(name: str, args: dict) -> dict:
    """本地工具分派。web_search 尚未接入，调用时抛 NotImplementedError。"""
    if name == "text_stats":
        return basic_stats(args.get("text", ""))
    if name == "web_search":
        raise NotImplementedError("百科检索尚未接入")
    raise ValueError(f"未知工具: {name}")
