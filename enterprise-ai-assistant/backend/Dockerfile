# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装编译依赖（pymysql 已纯 Python 不需要，但保险起见保留 build tools）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖（利用层缓存）
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制应用代码
COPY . .

# 入口脚本：等待 MySQL 可用 → 初始化 DB → 启动 uvicorn
RUN echo '#!/bin/sh
set -e
echo "[entrypoint] 等待 MySQL ..."
for i in $(seq 1 30); do
  python -c "import pymysql; pymysql.connect(host=\"${MYSQL_HOST}\", port=int(\"${MYSQL_PORT:-3306}\"), user=\"${MYSQL_USER}\", password=\"${MYSQL_PASSWORD}\")" 2>/dev/null && break
  sleep 2
done
echo "[entrypoint] 初始化数据库 ..."
python init_db.py || echo "[entrypoint] init_db 失败（非阻塞）"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
