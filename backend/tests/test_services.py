"""纯函数 / 服务层单元测试（不依赖 LLM 与向量）。"""
import pytest
from fastapi import HTTPException

from app.services.settings import _vec_str
from app.services.stats import basic_stats, count_words
from app.utils.text import extract_json


def test_count_words():
    assert count_words("第一章正文") == 5
    assert count_words("hello 世界") == 2
    assert count_words("") == 0


def test_basic_stats():
    text = "第一段。\n\n第二段“对话”。"
    stats = basic_stats(text)
    assert stats["word_count"] > 0
    assert stats["paragraphs"] == 2
    assert stats["dialogue_lines"] == 1
    assert 0.0 <= stats["dialogue_ratio"] <= 1.0


def test_extract_json():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json("前缀 {\"b\": 2} 后缀") == {"b": 2}
    assert extract_json("[1, 2, 3]") == [1, 2, 3]
    assert extract_json("无 JSON") is None


def test_vec_str():
    assert _vec_str([0.12345678, -0.987654321]) == "[0.123457,-0.987654]"


@pytest.mark.asyncio
async def test_require_api_key(monkeypatch):
    from app.api.deps import require_api_key
    from app.core.config import settings

    # 未配置 API Key → 放行（单用户本地工具）
    monkeypatch.setattr(settings, "api_key", None)
    await require_api_key(None)

    # 配置后 → 校验
    monkeypatch.setattr(settings, "api_key", "secret")
    await require_api_key("secret")
    with pytest.raises(HTTPException) as exc:
        await require_api_key("wrong")
    assert exc.value.status_code == 401
