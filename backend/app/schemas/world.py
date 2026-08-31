"""世界观设定 schema。"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class WorldSettingBase(BaseModel):
    category: str = Field(description="设定分类")
    name: str = Field(description="设定名称")
    description: str | None = Field(default=None, description="设定描述（可选）")
    parent_id: uuid.UUID | None = Field(default=None, description="父级设定 ID（可选）")
    notes: str | None = Field(default=None, description="备注（可选）")


class WorldSettingCreate(WorldSettingBase):
    novel_id: uuid.UUID = Field(description="所属小说 ID")


class WorldSettingUpdate(BaseModel):
    category: str | None = Field(default=None, description="设定分类")
    name: str | None = Field(default=None, description="设定名称")
    description: str | None = Field(default=None, description="设定描述")
    parent_id: uuid.UUID | None = Field(default=None, description="父级设定 ID")
    notes: str | None = Field(default=None, description="备注")


class WorldSettingRead(WorldSettingBase, ORMModel):
    id: uuid.UUID = Field(description="设定 ID")
    novel_id: uuid.UUID = Field(description="所属小说 ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")