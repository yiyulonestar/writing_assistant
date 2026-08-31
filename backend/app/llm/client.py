"""通义千问客户端封装（通过 OpenAI SDK 兼容模式）。

- 生成主模型：qwen3.5-flash
- 审稿模型：qwen3.6-35b-a3b
- base_url 指向 DashScope 兼容端点
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """获取全局单例客户端（首次调用时校验 API Key 并建立连接）。"""
    global _client
    if _client is None:
        if not settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY 未配置，请在 .env 中设置")
        _client = AsyncOpenAI(
            api_key=settings.dashscope_api_key, base_url=settings.llm_base_url
        )
    return _client


class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        self.client = get_client()
        self.model = model or settings.generation_model

    def _build_messages(self, messages: list[dict], system: str | None) -> list[dict]:
        msgs: list[dict] = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)
        return msgs

    async def complete(
        self,
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 8000,
        temperature: float = 0.8,
    ) -> str:
        """生成一段文本并聚合返回（非流式）。"""
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(messages, system),
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )
        return resp.choices[0].message.content or ""

    async def stream(
        self,
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 8000,
        temperature: float = 0.8,
    ) -> AsyncIterator[str]:
        """流式生成，逐段 yield 文本增量（供正文生成实时推送使用）。

        注意：openai 3.6.0 内置的 httpcore2 在 Python 3.14 下关闭流式响应时会
        打出一条「generator didn't stop after athrow()」的清理告警（不影响内容）。
        正文生成接入前（阶段四）需确认 SDK 升级或换用兼容版本。
        """
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(messages, system),
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in resp:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
