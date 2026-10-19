# syntax=docker/dockerfile:1
# Dixiyang Python 主后端（FastAPI，8084）
FROM python:3.11-slim-bookworm

# 国内网络可在 .env 设置 PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_INDEX_URL=https://pypi.org/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    UV_INDEX_URL=${PIP_INDEX_URL} \
    UV_DEFAULT_INDEX=${PIP_INDEX_URL} \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/DixyangFast/src \
    TZ=Asia/Shanghai

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tzdata libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "uv==0.11.6"

WORKDIR /app/DixyangFast

# 先装依赖：只有 pyproject/uv.lock 变化才重新安装，日常改代码命中缓存
COPY DixyangFast/pyproject.toml DixyangFast/uv.lock DixyangFast/README.md ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

COPY DixyangFast/src ./src

# 非 root 运行；上传/聊天 JSON 落在 /app/uploads（compose 命名卷）
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/uploads \
    && chown -R app:app /app
USER app

EXPOSE 8084
CMD ["python", "src/dixiyang/main.py"]
