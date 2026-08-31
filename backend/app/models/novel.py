"""小说主体。"""
from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
    from app.models.chapter import Chapter
    from app.models.character import Character
    from app.models.timeline import TimelineEvent
    from app.models.world import WorldSetting


class Novel(Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    genre = fields.CharField(max_length=100, null=True)
    synopsis = fields.TextField(null=True)  # 全书简介
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    chapters: fields.ReverseRelation[Chapter]                 # 章节
    characters: fields.ReverseRelation[Character]             # 角色
    world_settings: fields.ReverseRelation[WorldSetting]      # 世界设置
    timeline_events: fields.ReverseRelation[TimelineEvent]    # 时间线事件

    class Meta:
        table = "novels"
