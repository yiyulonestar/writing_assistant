"""小说 schema。"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class NovelBase(BaseModel):
    title: str = Field(description="小说标题")
    genre: str | None = Field(default=None, description="题材类型（可选）")
    synopsis: str | None = Field(default=None, description="故事简介（可选）")
    notes: str | None = Field(default=None, description="备注（可选）")


class NovelCreate(NovelBase):
    pass


class NovelUpdate(BaseModel):
    title: str | None = Field(default=None, description="小说标题")
    genre: str | None = Field(default=None, description="题材类型")
    synopsis: str | None = Field(default=None, description="故事简介")
    notes: str | None = Field(default=None, description="备注")


class NovelRead(NovelBase, ORMModel):
    id: uuid.UUID = Field(description="小说 ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")