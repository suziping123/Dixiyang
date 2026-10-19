#!/usr/bin/env bash
# Dixiyang Linux 一键部署（Docker Compose）
# 适用：Kubuntu / Ubuntu / Debian（x86_64 / arm64）
# 用法：./scripts/deploy-linux.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { printf "${GREEN}[deploy]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[warn]${NC} %s\n" "$*"; }
die()  { printf "${RED}[error]${NC} %s\n" "$*" >&2; exit 1; }

env_value() {
  # 读取 .env 中最后一个 KEY=value（不存在则输出空）
  [ -f .env ] || return 0
  sed -n "s/^$1=//p" .env | tail -n 1
}

gen_hex() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex "$1"
  else
    head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n'
  fi
}

# ---------- 1. 环境检查 ----------
command -v docker >/dev/null 2>&1 || die "未安装 Docker。请先看 docs/Linux部署指南.md 的「安装 Docker」一节。"

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  die "未找到 Docker Compose。请安装 docker-compose-plugin（见 docs/Linux部署指南.md）。"
fi

if ! docker info >/dev/null 2>&1; then
  warn "Docker 服务未运行，尝试启动..."
  if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl start docker || true
    sleep 2
  fi
fi
docker info >/dev/null 2>&1 || die "Docker 服务仍不可用。请执行：sudo systemctl start docker，并确认当前用户在 docker 组。"

command -v curl >/dev/null 2>&1 || warn "未安装 curl，将跳过 HTTP 健康等待（不影响启动）。"

# ---------- 2. 初始化 .env ----------
if [ ! -f .env ]; then
  log "未发现 .env，从 .env.example 生成并写入随机密钥..."
  cp .env.example .env
  chmod 600 .env

  DB_PASS="$(gen_hex 12)"
  JWT_SECRET="$(gen_hex 32)"

  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=${DB_PASS}|" .env
  sed -i "s|^DATABASE_URL=.*|DATABASE_URL=mysql+pymysql://root:${DB_PASS}@127.0.0.1:3306/dixiyang?charset=utf8|" .env
  sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|" .env
  sed -i "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD:-123321}|" .env

  if [ -t 0 ]; then
    printf "请输入 DeepSeek API Key（直接回车可跳过，之后编辑 .env 补上）："
    read -r DS_KEY || true
    if [ -n "${DS_KEY:-}" ]; then
      sed -i "s|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=${DS_KEY}|" .env
      log "DeepSeek API Key 已写入 .env"
    else
      warn "已跳过 DeepSeek Key：登录/小说/便签可用，AI 聊天与补全不可用。"
    fi
  else
    warn "非交互环境：跳过 DeepSeek Key 输入，请稍后手动编辑 .env。"
  fi
else
  log "检测到已存在的 .env，保持不覆盖。"
fi

# 校验关键占位符
if grep -q '^JWT_SECRET_KEY=your-secret-key-here' .env; then
  die ".env 的 JWT_SECRET_KEY 仍是占位符，请修改后再部署。"
fi
if grep -q '^DB_PASSWORD=your_password_here' .env; then
  die ".env 的 DB_PASSWORD 仍是占位符，请修改后再部署。"
fi
if grep -q '^DEEPSEEK_API_KEY=sk-your-api-key-here' .env; then
  warn "DEEPSEEK_API_KEY 仍是占位符：系统能启动，但 AI 功能会不可用。"
fi

BACKEND_PORT="$(env_value BACKEND_PORT)"; BACKEND_PORT="${BACKEND_PORT:-8084}"
WEB_PORT="$(env_value WEB_PORT)";         WEB_PORT="${WEB_PORT:-8080}"
ADMIN_USERNAME="$(env_value ADMIN_USERNAME)"; ADMIN_USERNAME="${ADMIN_USERNAME:-admin123}"
ADMIN_PASSWORD="$(env_value ADMIN_PASSWORD)"; ADMIN_PASSWORD="${ADMIN_PASSWORD:-123456}"

# ---------- 3. 构建并启动 ----------
log "开始构建并启动容器（首次 5-15 分钟，取决于网络；请耐心等待）..."
"${COMPOSE[@]}" up -d --build

# ---------- 4. 等待后端健康 ----------
if command -v curl >/dev/null 2>&1; then
  log "等待后端就绪..."
  READY=0
  DEADLINE=$((SECONDS + 180))
  while [ "$SECONDS" -lt "$DEADLINE" ]; do
    if curl -fsS --max-time 2 "http://127.0.0.1:${BACKEND_PORT}/" >/dev/null 2>&1; then
      READY=1
      break
    fi
    sleep 2
  done
  if [ "$READY" -ne 1 ]; then
    "${COMPOSE[@]}" ps || true
    "${COMPOSE[@]}" logs --tail=100 backend db || true
    die "后端 180 秒内未就绪。请查看上面的日志，或执行：docker compose logs -f backend"
  fi
  log "后端已就绪。"
fi

# ---------- 5. 创建管理员（幂等） ----------
log "创建/确认管理员账号 ${ADMIN_USERNAME} ..."
if ! "${COMPOSE[@]}" exec -T \
  -e ADMIN_USERNAME="${ADMIN_USERNAME}" \
  -e ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
  backend python -m dixiyang.seed_admin; then
  warn "管理员创建失败。可手动执行："
  warn "  docker compose exec -T backend python -m dixiyang.seed_admin"
fi

# ---------- 6. 输出访问信息 ----------
LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
echo
log "部署完成 ✅"
echo "  用户端:   http://localhost:${WEB_PORT}"
if [ -n "${LAN_IP:-}" ]; then
  echo "  局域网:   http://${LAN_IP}:${WEB_PORT}"
fi
echo "  管理后台: http://localhost:${WEB_PORT}/admin.html"
echo "  后端 API: http://127.0.0.1:${BACKEND_PORT}/api"
echo "  管理员:   ${ADMIN_USERNAME} / ${ADMIN_PASSWORD}"
echo
echo "常用命令："
echo "  docker compose ps                 # 状态"
echo "  docker compose logs -f backend    # 后端日志"
echo "  docker compose down               # 停止（保留数据）"
echo "  docker compose up -d --build      # 更新后重建"
echo
warn "首次登录后请尽快修改默认管理员密码；生产环境请配置防火墙与 HTTPS（见 docs/Linux部署指南.md）。"
