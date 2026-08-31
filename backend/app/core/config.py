"""应用配置（pydantic-settings，从环境变量 / .env 读取）。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用
    app_name: str = "Writing Assistant API"
    environment: str = "development"
    log_level: str = "INFO"

    # CORS（允许的前端来源，逗号分隔；本地工具默认放行 Vite dev server）
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # 数据库（Tortoise ORM 使用 postgres:// 协议）
    database_url: str = "postgres://postgres:postgres@localhost:5432/writing_assistant"

    # LLM（通义千问，OpenAI 兼容模式）
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_api_key: str | None = None
    generation_model: str = "qwen3.5-flash"
    review_model: str = "qwen3.6-35b-a3b"

    # 嵌入
    # provider: huggingface（本地 sentence-transformers）/ openai（远程 DashScope embedding）
    embedding_provider: str = "huggingface"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dimension: int = 512

    # 鉴权（可选）：设置 API_KEY 后，生成类接口需携带 X-API-Key 请求头
    api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
