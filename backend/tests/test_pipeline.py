"""生成流水线 / Agent 图测试（LLM 用 mock）。"""
import pytest

from app.agents.graph import build_graph
from app.llm.client import LLMClient
from app.models import Chapter, ChapterDraft, Character, Novel
from app.services.generation.pipeline import GenerationPipeline


async def _fake_complete(self, messages, system=None, **kwargs):
    """按系统提示词返回对应的 mock 结果。"""
    if system and "大纲策划" in system:
        return '{"outline": "测试大纲", "characters": ["林辰"], "locations": [], "events": [], "mood": "热血"}'
    if system and "审稿编辑" in system:
        return '{"issues": [], "conflicts": [], "summary": "通过"}'
    if system and "摘要" in system:
        return "前文摘要：林辰崛起。"
    return "这是测试生成的正文内容。" * 30


@pytest.fixture
def mock_llm(monkeypatch):
    monkeypatch.setattr(LLMClient, "complete", _fake_complete)


async def _prepare_novel():
    novel = await Novel.create(title="测试", synopsis="少年修仙。")
    await Character.create(name="林辰", role="主角", personality="坚韧", novel_id=novel.id)
    return novel


@pytest.mark.asyncio
async def test_pipeline_generate(mock_llm):
    novel = await _prepare_novel()
    result = await GenerationPipeline().generate(
        novel_id=novel.id, chapter_number=1, target_word_count=100
    )
    assert result["chapter_id"] is not None
    assert result["content"]
    assert result["review"]["conflicts"] == []

    chapter = await Chapter.get(id=result["chapter_id"])
    assert chapter.summary  # 摘要已自动生成
    assert chapter.word_count > 0
    drafts = await ChapterDraft.filter(chapter_id=chapter.id).count()
    assert drafts >= 1


@pytest.mark.asyncio
async def test_pipeline_revise_on_conflict(monkeypatch):
    """审稿首次返回冲突 → 回退重写 → 二次通过。"""
    novel = await _prepare_novel()
    calls = {"review": 0}

    async def _review_with_conflict(self, messages, system=None, **kwargs):
        if system and "审稿编辑" in system:
            calls["review"] += 1
            if calls["review"] == 1:
                return '{"issues": [], "conflicts": ["设定违背：角色语气不符"], "summary": "需修改"}'
            return '{"issues": [], "conflicts": [], "summary": "通过"}'
        return await _fake_complete(self, messages, system=system, **kwargs)

    monkeypatch.setattr(LLMClient, "complete", _review_with_conflict)
    result = await GenerationPipeline().generate(
        novel_id=novel.id, chapter_number=1, target_word_count=100
    )
    assert calls["review"] == 2  # 发生了回退
    assert result["review"]["conflicts"] == []


@pytest.mark.asyncio
async def test_agent_graph(mock_llm):
    novel = await _prepare_novel()
    g = build_graph()
    result = await g.ainvoke(
        {
            "novel_id": str(novel.id),
            "chapter_number": 1,
            "outline": "测试大纲",
            "target_word_count": 100,
        },
        config={"configurable": {"thread_id": "t-1"}},
    )
    assert result.get("chapter_id")
    assert result.get("draft")
