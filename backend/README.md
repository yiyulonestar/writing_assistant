# 长篇小说 / 网文创作辅助 Agent —— 后端

基于 **FastAPI + Tortoise ORM + PostgreSQL（pgvector）** 的网文写作辅助后端，LLM 走 **通义千问（OpenAI 兼容模式）**，嵌入用 **BAAI/bge-small-zh-v1.5**（本地 huggingface 或远程 DashScope 两种 provider 可选）。

> 📖 **接口使用说明**见 [`../使用说明.md`](../使用说明.md)（含启动步骤、Swagger 测试方法、字段速查、各接口示例与完整流程演示）。

核心能力：

- **结构化设定管理**：角色 / 世界观 / 时间线存结构化表，embedding 列做语义检索
- **多步生成流水线**：拆解 → 检索设定 → 生成草稿 → 审稿 → 落库
- **一致性审稿**：独立审稿模块核对角色语气、剧情逻辑、设定违背
- **工具调用**：文本统计（本地确定性计算）+ 百科检索
- **交互式重写**：按章节/段落局部重写，保留草稿版本历史

## 技术栈

| 层 | 选型 |
|----|------|
| 语言 | Python 3.14 |
| Web | FastAPI（全异步） |
| ORM | Tortoise ORM 1.x（async） |
| 迁移 | 开发环境自动建表（`generate_schemas`） |
| 数据库 | PostgreSQL 16 + pgvector |
| LLM | 通义千问（qwen-max / qwen-plus，通过 OpenAI SDK 3.x 兼容模式） |
| Embedding | BAAI/bge-small-zh-v1.5（512 维，本地 huggingface / 远程 DashScope 可选） |

## 目录结构

```
backend/
├── app/
│   ├── main.py                 # FastAPI 入口 + Tortoise 生命周期
│   ├── core/config.py          # 配置（.env）
│   ├── db/
│   │   ├── tortoise.py         # Tortoise 初始化 + TORTOISE_ORM 配置
│   │   ├── fields.py           # 自定义 VectorField（映射 pgvector）
│   │   └── ensure.py           # 确保 pgvector 扩展存在
│   ├── models/                 # Tortoise 模型：novel / character / world / timeline / chapter
│   ├── schemas/                # Pydantic 请求/响应
│   ├── api/v1/endpoints/       # 路由（novels/characters/chapters/timeline/world-settings/generate）
│   ├── services/
│   │   ├── stats.py            # 文本统计
│   │   ├── settings.py         # 设定检索 + embedding 同步 + 事实清单
│   │   └── generation/         # 生成流水线（桩）
│   ├── llm/                    # 通义千问客户端 + 提示词 + 工具
│   └── embeddings/             # 嵌入编码（huggingface / openai 双 provider）
├── tests/
├── Dockerfile                  # 应用容器
├── docker-compose.yml          # db + app
├── entrypoint.sh               # 容器启动：ensure pgvector + uvicorn
└── pyproject.toml
```

## 快速开始（本地开发）

```bash
# 1. 起数据库（PostgreSQL + pgvector）
docker compose up -d db

# 2. 装依赖（uv 按 uv.lock 精确安装到 .venv；embeddings 可选：本地编码时才需要）
uv sync --extra dev --extra embeddings

# 3. 配置环境变量
cp .env.example .env                 # 填入 DASHSCOPE_API_KEY 等

# 4. 启动（开发环境 lifespan 自动建表 + 确保 vector 扩展）
uv run uvicorn app.main:app --reload
# 文档：http://localhost:8000/docs

# 5. 测试与 lint
uv run pytest
uv run ruff check .
```

> 开发环境无需手动迁移：`app.main.lifespan` 会调用 `ensure_vector_extension` + `generate_schemas` 自动建表。
> 若不想本地加载 embedding 权重，可将 `.env` 里 `EMBEDDING_PROVIDER=openai`，走 DashScope 远程嵌入。

## Docker 部署

```bash
# 构建并启动（db + app，默认包含本地 embedding 依赖）
docker compose up -d --build

# 若仅用远程 DashScope embedding（减小镜像体积）：
# docker compose build --build-arg INSTALL_EMBEDDINGS=false app
```

容器 `app` 启动流程（见 `entrypoint.sh`）：确保 vector 扩展 → `uvicorn`。

## 当前状态

- ✅ CRUD：小说 / 角色 / 章节（含草稿版本历史、局部重写）/ 时间线 / 世界观（含 embedding 同步）
- ✅ 设定检索：结构化精确查询 + pgvector 向量召回 + 事实清单
- ✅ LLM 客户端（通义千问，OpenAI 兼容模式）+ 嵌入客户端（bge-small-zh，双 provider）
- ✅ 生成流水线：planner → retriever → generator → reviewer（含回退修正、前文摘要、批量生成）
- ✅ 多 Agent 编排（LangGraph，checkpointer 断点续跑）
- ✅ 鉴权（可选 API Key）
- ✅ 测试：13 个用例（CRUD / 服务 / 流水线，LLM 打桩）

## 约定

- 全异步：Tortoise ORM + asyncpg，所有 IO 走 `async`
- 主键 UUID，`created_at` / `updated_at` 由 `DatetimeField(auto_now_add/auto_now)` 维护
- 生成用 `qwen-max`，审稿用 `qwen-plus`（可在 `.env` 覆盖）
- 设定一致性靠「结构化表 + embedding 检索」，向量维度见 `EMBEDDING_DIMENSION`（默认 512）
- pgvector 字段由自定义 `VectorField` 映射，召回用原生 SQL 余弦距离（`<=>`）