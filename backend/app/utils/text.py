"""文本 / 结构解析工具。"""
from __future__ import annotations

import json
import re

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> dict | list | None:
    """宽容地提取 JSON：去掉 ```json 围栏，取首尾大括号 / 中括号。"""
    text = (text or "").strip()
    fence = _FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    return None
