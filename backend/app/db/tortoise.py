"""Tortoise ORM 配置与初始化。"""
from tortoise import Tortoise

from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "timezone": "UTC",
}


async def init_db() -> None:
    """初始化 Tortoise（应用 lifespan / 迁移前调用）。

    _enable_global_fallback=True 使 TortoiseContext 在 ASGI lifespan
    与请求处理器分属不同 asyncio task 时仍可被找到（Tortoise v0.24+ 行为变更）。
    """
    await Tortoise.init(config=TORTOISE_ORM, _enable_global_fallback=True)


async def ensure_vector_extension() -> None:
    """确保 pgvector 扩展存在（建表 / 迁移前调用）。"""
    from tortoise import connections

    conn = connections.get("default")
    await conn.execute_script("CREATE EXTENSION IF NOT EXISTS vector")


async def generate_schemas() -> None:
    """开发环境自动建表；生产环境请用 Tortoise.generate_schemas。"""
    await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    await Tortoise.close_connections()