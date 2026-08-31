"""嵌入编码客户端（中文向量检索）。

支持两种 provider：
- huggingface：本地 sentence-transformers 加载 bge-small-zh-v1.5（512 维）
- openai：远程 DashScope embedding（OpenAI 兼容接口，无需本地权重）

依赖 sentence-transformers（含 torch）体积大，仅 huggingface provider 需要，按需安装：
    uv sync --extra embeddings
"""
from __future__ import annotations

import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# bge 系列检索时的 query 指令前缀
_QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："

class EmbeddingClient:
    def __init__(self, provider: str | None = None, model_name: str | None = None) -> None:
        self.provider = provider or settings.embedding_provider
        self.model_name = model_name or settings.embedding_model
        self._model = None  # huggingface 本地模型
        self._remote = None  # openai 远程客户端

    def _load(self):
        """懒加载本地 sentence-transformers 模型。"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _load_remote(self):
        """懒加载远程 OpenAI 兼容客户端（DashScope）。"""
        if self._remote is None:
            from openai import AsyncOpenAI

            self._remote = AsyncOpenAI(
                api_key=settings.dashscope_api_key, base_url=settings.llm_base_url
            )
        return self._remote

    def encode(self, texts: list[str]) -> list[list[float]]:
        """本地同步编码（阻塞，内部用）。业务代码请用 aencode。"""
        return self._load().encode(texts, normalize_embeddings=True).tolist()

    async def aencode(self, texts: list[str]) -> list[list[float]]:
        """异步编码，避免阻塞事件循环；支持本地/远程两种 provider。"""
        if self.provider == "openai":
            client = self._load_remote()
            resp = await client.embeddings.create(model=self.model_name, input=texts)
            return [d.embedding for d in resp.data]
        return await asyncio.to_thread(self.encode, texts)

    async def aencode_query(self, text: str) -> list[float]:
        """对 query 编码（huggingface provider 加指令前缀，openai 直接编码）。"""
        if self.provider == "openai":
            return (await self.aencode([text]))[0]
        return (await self.aencode([_QUERY_PREFIX + text]))[0]

    def warmup(self) -> None:
        """预热：提前加载模型权重 / 建立远程客户端。失败不抛异常，仅记录。

        供 lifespan 在后台线程调用，避免首个请求卡在权重下载 / 冷启动上。
        """
        try:
            if self.provider == "openai":
                self._load_remote()
            else:
                self._load()
        except Exception as exc:  # noqa: BLE001 — 预热失败不阻断启动
            logger.warning("嵌入模型预热失败：%s", exc)


_client: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient:
    """获取全局单例（懒加载模型权重 / 客户端）。"""
    global _client
    if _client is None:
        _client = EmbeddingClient()
    return _client
