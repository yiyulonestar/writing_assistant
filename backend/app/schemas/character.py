"""角色 schema。"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CharacterBase(BaseModel):
    name: str = Field(description="角色名称")
    aliases: list[str] | None = Field(default=None, description="角色别名列表（可选）")
    role: str | None = Field(default=None, description="角色定位（可选）")
    personality: str | None = Field(default=None, description="性格描述（可选）")
    background: str | None = Field(default=None, description="背景故事（可选）")
    appearance: str | None = Field(default=None, description="外貌描述（可选）")
    goals: str | None = Field(default=None, description="目标动机（可选）")
    relationships: dict | None = Field(default=None, description="人物关系（可选）")
    notes: str | None = Field(default=None, description="备注（可选）")


class CharacterCreate(CharacterBase):
    novel_id: uuid.UUID = Field(description="所属小说 ID")


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, description="角色名称")
    aliases: list[str] | None = Field(default=None, description="角色别名列表")
    role: str | None = Field(default=None, description="角色定位")
    personality: str | None = Field(default=None, description="性格描述")
    background: str | None = Field(default=None, description="背景故事")
    appearance: str | None = Field(default=None, description="外貌描述")
    goals: str | None = Field(default=None, description="目标动机")
    relationships: dict | None = Field(default=None, description="人物关系")
    notes: str | None = Field(default=None, description="备注")


class CharacterRead(CharacterBase, ORMModel):
    id: uuid.UUID = Field(description="角色 ID")
    novel_id: uuid.UUID = Field(description="所属小说 ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")