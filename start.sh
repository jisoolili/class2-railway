#!/bin/bash
# Railway 启动脚本
# 使用 gunicorn 作为生产服务器，配合 uvicorn worker 运行 FastAPI

# Railway 会提供 PORT 环境变量，默认 8000
PORT=${PORT:-8000}

# 启动命令
exec gunicorn app:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:$PORT" \
    --timeout 120