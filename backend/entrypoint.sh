#!/bin/sh
set -e

export PYTHONPATH=/app

echo "[entrypoint] ensure pgvector extension"
python -m app.db.ensure

echo "[entrypoint] start app"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000