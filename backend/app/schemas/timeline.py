"""时间线事件 schema。"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TimelineEventBase(BaseModel):
    title: str = Field(description="事件标题")
    description: str | None = Field(default=None, description="事件描述（可选）")
    time_point: str | None = Field(default=None, description="时间点（可选）")
    order_index: int = Field(default=0, description="排序序号")
    status: str = Field(default="planned", description="事件状态")
    chapter_id: uuid.UUID | None = Field(default=None, description="关联章节 ID（可选）")
    involved_character_ids: list[str] | None = Field(default=None, description="涉及角色 ID 列表（可选）")


class TimelineEventCreate(TimelineEventBase):
    novel_id: uuid.UUID = Field(description="所属小说 ID")


class TimelineEventUpdate(BaseModel):
    title: str | None = Field(default=None, description="事件标题")
    description: str | None = Field(default=None, description="事件描述")
    time_point: str | None = Field(default=None, description="时间点")
    order_index: int | None = Field(default=None, description="排序序号")
    status: str | None = Field(default=None, description="事件状态")
    chapter_id: uuid.UUID | None = Field(default=None, description="关联章节 ID")
    involved_character_ids: list[str] | None = Field(default=None, description="涉及角色 ID 列表")


class TimelineEventRead(TimelineEventBase, ORMModel):
    id: uuid.UUID = Field(description="事件 ID")
    novel_id: uuid.UUID = Field(description="所属小说 ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")