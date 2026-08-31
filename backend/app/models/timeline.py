"""时间线事件（防前后矛盾的关键表）。"""
from tortoise import fields
from tortoise.models import Model

from app.core.config import settings
from app.db.fields import VectorField


class TimelineEvent(Model):
    id = fields.UUIDField(pk=True)
    novel = fields.ForeignKeyField(
        "models.Novel", related_name="timeline_events", on_delete=fields.CASCADE
    )

    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    time_point = fields.CharField(max_length=255, null=True)  # 网文时间多为相对/虚数，用文本
    order_index = fields.IntField(default=0)  # 排序
    status = fields.CharField(max_length=20, default="planned")  # planned / occurred
    chapter = fields.ForeignKeyField(
        "models.Chapter", related_name="timeline_events", null=True, on_delete=fields.SET_NULL
    )
    involved_character_ids = fields.JSONField(null=True)

    embedding = VectorField(dim=settings.embedding_dimension, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "timeline_events"
