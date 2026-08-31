"""FastAPI 入口。"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.tortoise import close_db, ensure_vector_extension, generate_schemas, init_db
from app.embeddings.client import get_embedding_client
from app.llm.client import get_client

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动钩子：初始化 Tortoise，确保 pgvector 扩展，开发环境自动建表
    await init_db()
    await ensure_vector_extension()
    if settings.environment == "development":
        await generate_schemas()
    # 初始化 LLM 客户端（校验 API Key 并预热；未配置则仅告警，不影响 CRUD）
    if settings.dashscope_api_key:
        get_client()
    else:
        logger.warning("DASHSCOPE_API_KEY 未配置，LLM 相关功能不可用")
    # 嵌入客户端：记录配置并在后台预热（huggingface 首次加载需下载权重，不阻塞启动）
    embedding_client = get_embedding_client()
    logger.info(
        "嵌入配置 provider=%s model=%s dim=%s",
        embedding_client.provider,
        embedding_client.model_name,
        settings.embedding_dimension,
    )
    if embedding_client.provider == "huggingface":
        asyncio.get_running_loop().create_task(asyncio.to_thread(embedding_client.warmup))
    yield
    # 关闭钩子：释放连接
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS：放行前端来源（本地开发 Vite dev server；生产同源部署时无跨域，此项不影响）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# 生产同源部署：前端 vite build 产物（fronted/dist）存在时，由后端直接托管（单进程单端口）。
# 开发期无 dist 目录则跳过，前端仍走 Vite dev server（5173）。
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "fronted", "dist")
)
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底异常处理：记录完整堆栈，对外返回通用 500（不泄露内部细节）。"""
    logger.exception("未处理异常 %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """根路径兜底：仅在未挂载前端静态产物时生效（挂载后由 StaticFiles 处理）。"""
    return {"name": settings.app_name, "docs": "/docs"}     # 文档路径
