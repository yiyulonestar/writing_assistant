"""世界观设定（地理 / 势力 / 修炼体系 / 物品 / 规则…）。"""
from tortoise import fields
from tortoise.models import Model

from app.core.config import settings
from app.db.fields import VectorField


class WorldSetting(Model):
    id = fields.UUIDField(pk=True)
    novel = fields.ForeignKeyField(
        "models.Novel", related_name="world_settings", on_delete=fields.CASCADE
    )

    category = fields.CharField(max_length=50, index=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    parent = fields.ForeignKeyField(
        "models.WorldSetting", related_name="children", null=True, on_delete=fields.CASCADE
    )  # 层级关系（如：某大陆 → 某国 → 某城）
    notes = fields.TextField(null=True)

    embedding = VectorField(dim=settings.embedding_dimension, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "world_settings"
