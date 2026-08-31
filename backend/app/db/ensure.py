"""确保 pgvector 扩展存在（容器启动 / aerich 迁移前执行）。

用法：python -m app.db.ensure
"""
import asyncio

from app.db.tortoise import close_db, ensure_vector_extension, init_db


async def main() -> None:
    await init_db()
    await ensure_vector_extension()
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
