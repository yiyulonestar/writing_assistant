"""通用 schema。"""
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """响应基类：允许从 ORM 对象实例化（Pydantic v2 的 from_attributes）。"""

    model_config = ConfigDict(from_attributes=True)
