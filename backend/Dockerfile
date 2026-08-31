FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 复制源码（.env 等由 .dockerignore 排除）
COPY . .

# 安装运行时依赖
RUN pip install --upgrade pip \
    && pip install -e .

# 本地 embedding（默认开启；若仅用远程 DashScope，用 --build-arg INSTALL_EMBEDDINGS=false 跳过）
# 构建时预下载权重，避免容器启动时再下载（冷启动）
ARG INSTALL_EMBEDDINGS=true
ARG EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
RUN if [ "$INSTALL_EMBEDDINGS" = "true" ]; then \
        pip install -e ".[embeddings]" && \
        python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('$EMBEDDING_MODEL')"; \
    fi

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
