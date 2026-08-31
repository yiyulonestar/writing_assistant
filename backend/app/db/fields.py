"""pgvector 向量字段（Tortoise 无原生支持，自定义映射到 vector 类型）。"""
from __future__ import annotations

from tortoise.fields import Field


class VectorField(Field):
    """映射 PostgreSQL vector 列。

    - 写入：Python list[float] → 文本 "[0.1,0.2,...]"（asyncpg 直接传字符串，由 pgvector cast）
    - 读取：文本 "[...]" → list[float]
    """

    def __init__(self, dim: int = 512, **kwargs) -> None:
        self.dim = dim
        super().__init__(**kwargs)

    @property
    def SQL_TYPE(self) -> str:
        return f"vector({self.dim})"

    def to_db_value(self, value, instance):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return "[" + ",".join(str(float(x)) for x in value) + "]"

    def to_python_value(self, value):
        if value is None:
            return None
        if isinstance(value, list):
            return [float(x) for x in value]
        if isinstance(value, str):
            inner = value.strip().strip("[]")
            if not inner:
                return []
            return [float(x) for x in inner.split(",")]
        return value
