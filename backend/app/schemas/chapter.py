"""章节 schema。"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ChapterBase(BaseModel):
    number: int = Field(description="章节序号")
    title: str | None = Field(default=None, description="章节标题（可选）")
    summary: str | None = Field(default=None, description="章节摘要（可选）")
    outline: str | None = Field(default=None, description="章节大纲（可选）")
    content: str | None = Field(default=None, description="章节内容（可选）")
    word_count: int = Field(default=0, description="字数")
    status: str = Field(default="draft", description="章节状态")


class ChapterCreate(ChapterBase):
    novel_id: uuid.UUID = Field(description="所属小说 ID")


class ChapterUpdate(BaseModel):
    title: str | None = Field(default=None, description="章节标题（可选）")
    summary: str | None = Field(default=None, description="章节摘要（可选）")
    outline: str | None = Field(default=None, description="章节大纲（可选）")
    content: str | None = Field(default=None, description="章节内容（可选）")
    word_count: int | None = Field(default=None, description="字数")
    status: str | None = Field(default=None, description="章节状态")


class ChapterRead(ChapterBase, ORMModel):
    id: uuid.UUID = Field(description="章节 ID")
    novel_id: uuid.UUID = Field(description="所属小说 ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class DraftCreate(BaseModel):
    content: str = Field(description="草稿内容")
    note: str | None = Field(default=None, description="本次修改说明（人工或审稿）")


class DraftRead(ORMModel):
    id: uuid.UUID = Field(description="草稿 ID")
    chapter_id: uuid.UUID = Field(description="所属章节 ID")
    version: int = Field(description="版本号")
    content: str = Field(description="草稿内容")
    note: str | None = Field(default=None, description="修改说明")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class RewriteRequest(BaseModel):
    start: int = Field(description="起始段落下标（含，0 起）")
    end: int = Field(description="结束段落下标（含）")
    instruction: str | None = Field(default=None, description="修改指令（可选）")


class DraftDiff(BaseModel):
    from_version: int = Field(description="起始版本号")
    to_version: int = Field(description="目标版本号")
    diff: list[str] = Field(description="差异行列表")