"""章节生成 schema。"""
import uuid

from pydantic import BaseModel, Field


class GenerateChapterRequest(BaseModel):
    novel_id: uuid.UUID = Field(description="小说 ID")
    chapter_number: int = Field(description="章节序号")
    outline: str | None = Field(default=None, description="本章大纲（可选，缺省由 planner 拆解）")
    target_word_count: int = Field(default=3000, description="目标字数")


class ReviewReport(BaseModel):
    issues: list[str] = Field(default=[], description="问题列表")
    conflicts: list[str] = Field(default=[], description="冲突列表")
    fixed: bool = Field(default=False, description="是否已自动修复")
    summary: str | None = Field(default=None, description="审稿摘要（可选）")


class GenerateChapterResponse(BaseModel):
    chapter_id: uuid.UUID = Field(description="生成的章节 ID")
    content: str = Field(description="生成的章节内容")
    word_count: int = Field(description="实际字数")
    review: ReviewReport | None = Field(default=None, description="审稿报告（可选）")


class GenerateChaptersRequest(BaseModel):
    novel_id: uuid.UUID = Field(description="小说 ID")
    start_chapter: int = Field(description="起始章节序号")
    count: int = Field(description="生成章节数")
    target_word_count: int = Field(default=3000, description="目标字数")
    outlines: list[str] | None = Field(default=None, description="各章大纲列表（可选，按顺序对应各章）")