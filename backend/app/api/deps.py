"""路由依赖：鉴权等。

Tortoise 无需 get_db 依赖，服务层直接使用 ORM。
鉴权采用轻量 API Key（X-API-Key 请求头）：未配置 API_KEY 时不启用（单用户本地工具）。
"""
from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """校验 API Key；未配置时放行。"""
    if not settings.api_key:
        return
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key"
        )
