"""角色设定。"""
from tortoise import fields
from tortoise.models import Model

from app.core.config import settings
from app.db.fields import VectorField


class Character(Model):
    id = fields.UUIDField(pk=True)
    novel = fields.ForeignKeyField(
        "models.Novel", related_name="characters", on_delete=fields.CASCADE
    )

    name = fields.CharField(max_length=100)
    aliases = fields.JSONField(null=True)  # 别名/称号
    role = fields.CharField(max_length=50, null=True)  # 主角/配角/反派…
    personality = fields.TextField(null=True)  # 性格
    background = fields.TextField(null=True)  # 背景故事
    appearance = fields.TextField(null=True)  # 外貌
    goals = fields.TextField(null=True)  # 动机/目标
    relationships = fields.JSONField(null=True)  # 与其他角色的关系
    notes = fields.TextField(null=True)

    # 语义检索向量：由「名字 + 性格 + 背景 + 目标…」拼装文本后编码
    embedding = VectorField(dim=settings.embedding_dimension, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "characters"
