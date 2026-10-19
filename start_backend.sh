#!/usr/bin/env bash
# 原生开发模式后端一键启动（Linux/macOS）
# Docker 部署不需要本脚本，见 docs/Linux部署指南.md
set -euo pipefail
cd "$(dirname "$0")/DixyangFast"

export REDIS_URL="${REDIS_URL:-redis://:123321@127.0.0.1:6379/0}"
exec uv run python src/dixiyang/main.py
