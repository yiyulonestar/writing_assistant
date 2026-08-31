"""章节与草稿版本。"""
from __future__ import annotations

from tortoise import fields
from tortoise.models import Model


class Chapter(Model):
    id = fields.UUIDField(pk=True)
    novel = fields.ForeignKeyField(
        "models.Novel", related_name="chapters", on_delete=fields.CASCADE
    )

    number = fields.IntField()
    title = fields.CharField(max_length=255, null=True)
    summary = fields.TextField(null=True)  # 本章摘要（供前文摘要/伏笔检索）
    outline = fields.TextField(null=True)  # 本章大纲 / 目标
    content = fields.TextField(null=True)  # 正文
    word_count = fields.IntField(default=0)
    status = fields.CharField(max_length=20, default="draft")  # draft / revising / done
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    drafts: fields.ReverseRelation[ChapterDraft]

    class Meta:
        table = "chapters"


class ChapterDraft(Model):
    id = fields.UUIDField(pk=True)
    chapter = fields.ForeignKeyField(
        "models.Chapter", related_name="drafts", on_delete=fields.CASCADE
    )
    version = fields.IntField()
    content = fields.TextField()
    note = fields.TextField(null=True)  # 本次修改说明（人工或审稿）
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "chapter_drafts"
