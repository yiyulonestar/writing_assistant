"""pytest 夹具：SQLite 内存库 + ASGI 客户端 + embedding 打桩。"""
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def _db():
    """每个测试用独立的内存 SQLite，避免数据串扰。"""
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["app.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture(autouse=True)
async def _mock_embedding(monkeypatch):
    """打桩 embedding 同步，CRUD 测试不依赖 sentence-transformers。"""
    from app.api.v1.endpoints import characters, timeline, world_settings

    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(characters, "sync_character_embedding", _noop)
    monkeypatch.setattr(timeline, "sync_timeline_event_embedding", _noop)
    monkeypatch.setattr(world_settings, "sync_world_setting_embedding", _noop)


@pytest_asyncio.fixture(autouse=True)
async def _mock_recall(monkeypatch):
    """打桩向量召回（SQLite 无 pgvector，避免触发本地 embedding 模型拖慢测试）。"""
    from app.services import settings as settings_service

    async def _no_recall(model, novel_id, query_text, top_k=5):
        return []

    monkeypatch.setattr(settings_service, "recall_by_embedding", _no_recall)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
