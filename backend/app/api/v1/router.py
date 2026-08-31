"""v1 路由聚合。"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    chapters,
    characters,
    generate,
    health,
    novels,
    timeline,
    world_settings,
    ws,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(novels.router, prefix="/novels", tags=["novels"])
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"])
api_router.include_router(world_settings.router, prefix="/world-settings", tags=["world-settings"])
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
api_router.include_router(ws.router, prefix="/generate", tags=["generate"])
