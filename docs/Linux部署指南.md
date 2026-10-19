# Dixiyang Linux 部署指南（Kubuntu / Ubuntu）

> 适用：Kubuntu 22.04 / 24.04、Ubuntu 22.04 / 24.04、Debian 12（x86_64）。
> 目标：**从 GitHub 克隆后，只装 Docker，一条命令拉起完整站点**。
> 最后更新：2026-10-19

---

## 0. 部署完成后是什么样

```
浏览器
  │
  ▼
┌──────────────────────────────────────────────┐
│ frontend（Nginx 容器，宿主机 8080）           │
│  ├─ Vue 用户端  http://IP:8080/               │
│  ├─ 管理后台    http://IP:8080/admin.html     │
│  └─ /api/* 反向代理（含 SSE 流式）            │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ backend（Python 3.11 + FastAPI，容器 8084）   │
│  只绑定 127.0.0.1:8084，供本机调试            │
└──────────┬───────────────────────┬───────────┘
           ▼                       ▼
   MySQL 8（容器 3306）      Redis 7（容器 6379）
   命名卷 mysql_data         命名卷 redis_data
           │
           └── 上传/聊天 JSON：命名卷 uploads_data
```

默认只对外开放 **8080**（前端）。MySQL、Redis、后端都不暴露到局域网，避免被扫端口。

---

## 1. 前置条件

| 项目 | 要求 | 说明 |
|------|------|------|
| 系统 | Kubuntu / Ubuntu 22.04+ / Debian 12+ | 64 位；已验证环境为 x86_64，arm64 理论可行但未实测 |
| 内存 | 建议 ≥ 4 GB | 前端构建峰值约 1–2 GB |
| 磁盘 | 建议 ≥ 10 GB 空闲 | 镜像 + 依赖 + 数据库 |
| 网络 | 能访问 GitHub / Docker Hub / PyPI / npm | 国内网络见 §2.4 镜像加速 |
| 账号 | DeepSeek API Key | https://platform.deepseek.com 获取；不填也能启动，但 AI 功能不可用 |
| 权限 | 能使用 sudo | 安装 Docker、开放防火墙 |

> 不需要预装 Python、Node.js、MySQL、Redis。它们全部在容器里。

---

## 2. 安装 Docker（只需做一次）

### 2.1 最快：官方脚本

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable --now docker
```

### 2.2 推荐：Ubuntu 官方仓库（便于后续升级）

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

### 2.3 让当前用户免 sudo 使用 Docker

```bash
sudo usermod -aG docker "$USER"
newgrp docker          # 或者注销后重新登录（最可靠）
docker run --rm hello-world
```

看到 `Hello from Docker!` 即成功。

### 2.4（可选）国内网络镜像加速

如果 `docker pull` 很慢，配置镜像加速（镜像地址会变化，失效就换一个）：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "registry-mirrors": ["https://docker.m.daocloud.io"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Python / npm 构建慢时，在项目 `.env` 里取消注释：

```dotenv
NPM_REGISTRY=https://registry.npmmirror.com
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

然后重新执行 `docker compose build`。

---

## 3. 获取代码

### 3.1 公开仓库（HTTPS，推荐）

```bash
sudo apt install -y git
git clone https://github.com/suziping123/Dixiyang.git
cd Dixiyang
```

> 没有 Git 也可以在 GitHub 页面点 **Code → Download ZIP**，解压后进入目录，后续命令完全一样（但无法用 `git pull` 升级）。

### 3.2 私有仓库 / 需要登录

GitHub 已不允许用账号密码克隆，请使用 Personal Access Token（PAT）：

```bash
git clone https://<你的用户名>:<你的PAT>@github.com/suziping123/Dixiyang.git
```

或配置 SSH：

```bash
ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub
# 把公钥粘贴到 GitHub → Settings → SSH and GPG keys
git clone git@github.com:suziping123/Dixiyang.git
```

### 3.3 配置 Git Hooks（开发协作建议，纯部署可跳过）

```bash
git config core.hooksPath .githooks
```

作用：防止 `git pull` 删除本地 `motion-web` 技能目录。详见 `docs/技能库出库与同步.md`。

---

## 4. 一键部署（推荐）

```bash
cd ~/Dixiyang          # 进入克隆后的目录
chmod +x scripts/deploy-linux.sh
./scripts/deploy-linux.sh
```

如果提示权限不足（例如放在 noexec 分区）：

```bash
bash scripts/deploy-linux.sh
```

### 4.1 脚本会做什么

1. 检查 `docker` / `docker compose`；Docker 未启动时尝试 `sudo systemctl start docker`。
2. 没有 `.env` 时从 `.env.example` 复制，并自动生成：
   - 随机数据库密码（`DB_PASSWORD`）
   - 随机 JWT 密钥（`JWT_SECRET_KEY`）
   - 对应的 `DATABASE_URL`
3. 交互式询问 DeepSeek API Key（直接回车可跳过，之后可编辑 `.env` 补上）。
4. 执行 `docker compose up -d --build`：
   - 拉取 MySQL 8 / Redis 7 / Python / Nginx 基础镜像
   - 安装 Python 依赖（`uv sync --frozen`，使用仓库内 `uv.lock`）
   - 构建 Vue 前端（`npm ci && npm run build`）
5. 等待后端健康（最多 180 秒）。
6. 创建管理员账号（幂等）：默认 `admin123 / 123456`。
7. 打印访问地址和常用命令。

### 4.2 首次构建耗时

| 网络 | 预计 |
|------|------|
| 正常 | 3–8 分钟 |
| 国内直连 | 10–20 分钟，建议先做 §2.4 镜像加速 |

构建期间看到大量下载日志是正常的。**不要中断**；中断后重新执行脚本即可，Docker 会复用已完成层。

### 4.3 成功标志

```text
[deploy] 后端已就绪。
[seed_admin] 已创建管理员：admin123（role=admin）
[deploy] 部署完成 ✅
  用户端:   http://localhost:8080
  管理后台: http://localhost:8080/admin.html
  管理员:   admin123 / 123456
```

浏览器打开 `http://localhost:8080`，能看到落地页即成功。

---

## 5. 手动部署（脚本失败时的等价步骤）

### 5.1 准备 .env

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

至少改这 4 项：

```dotenv
DB_PASSWORD=换成一个随机强密码
DATABASE_URL=mysql+pymysql://root:换成一个随机强密码@127.0.0.1:3306/dixiyang?charset=utf8
JWT_SECRET_KEY=输出 openssl rand -hex 32 的结果
DEEPSEEK_API_KEY=sk-你的真实key
```

> `DATABASE_URL` 里的密码要和 `DB_PASSWORD` 完全一致。
> 密码建议只用字母/数字；含 `@ : / ? #` 等字符时需 URL 编码。
> Docker 部署时后端实际连接的是容器内 `db`，compose 会自动覆盖 `DATABASE_URL` 的主机部分；保留本机地址用于原生开发即可。

### 5.2 构建并启动

```bash
docker compose up -d --build
docker compose ps
```

四个服务都应为 `running` / `healthy`：

```text
dixiyang-db         healthy
dixiyang-redis      healthy
dixiyang-backend    healthy
dixiyang-web        running
```

### 5.3 创建管理员

```bash
docker compose exec -T backend python -m dixiyang.seed_admin
```

自定义账号：

```bash
docker compose exec -T backend python -m dixiyang.seed_admin \
  --username myadmin --password 'my-strong-password' --email me@example.com
```

账号被登录风控锁住 / 忘记密码：

```bash
docker compose exec -T backend python -m dixiyang.seed_admin \
  --username admin123 --password 'new-password' --reset-password
```

### 5.4 健康检查

```bash
curl http://localhost:8080/healthz          # 前端 → ok
curl http://127.0.0.1:8084/                 # 后端 → JSON
curl http://127.0.0.1:8084/api/rag/stats    # 未登录应返回 401（说明 API 通了）
```

---

## 6. 访问与局域网

### 6.1 本机访问

| 入口 | 地址 |
|------|------|
| 用户端 / 落地页 | `http://localhost:8080` |
| 登录页 | `http://localhost:8080/login` |
| 管理后台 | `http://localhost:8080/admin.html` |
| 后端 API（仅本机） | `http://127.0.0.1:8084/api` |

管理员默认账号：`admin123 / 123456`。

普通用户可自行注册（不填验证码即可注册）。配置 SMTP 后额外支持邮箱验证码登录、修改邮箱验证码；不配置邮件不影响主流程。

### 6.2 同一局域网的其他电脑/手机访问

```bash
hostname -I | awk '{print $1}'       # 例如 192.168.1.20
```

然后访问：

```text
http://192.168.1.20:8080
```

如果打不开，放行防火墙：

```bash
sudo ufw status
sudo ufw allow 8080/tcp
sudo ufw reload
```

> 不要放行 3306 / 6379 / 8084。它们默认只绑定本机或未映射，暴露到公网有被入侵风险。

### 6.3 修改端口

编辑 `.env`：

```dotenv
WEB_PORT=80          # 想直接用 http://IP 访问就改成 80（需要 root 权限绑定）
BACKEND_PORT=8084
```

然后：

```bash
docker compose up -d
```

---

## 7. 环境变量说明

完整模板见 `.env.example`。

| 变量 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `DB_PASSWORD` | **是** | — | MySQL root 密码；首次启动后不要随意改（见 §11.4） |
| `DATABASE_URL` | **是** | — | SQLAlchemy 连接串；Docker 部署由 compose 覆盖主机 |
| `DB_NAME` | 否 | `dixiyang` | 数据库名，MySQL 容器首次启动自动创建 |
| `JWT_SECRET_KEY` | **是** | — | JWT 签名密钥；`openssl rand -hex 32` |
| `DEEPSEEK_API_KEY` | 强烈建议 | — | AI 聊天 / 续写；缺失时相关接口报错 |
| `REDIS_PASSWORD` | 否 | `123321` | Redis 密码；Redis 不可用时广场推荐自动降级 |
| `WEB_PORT` | 否 | `8080` | 前端对外端口 |
| `BACKEND_PORT` | 否 | `8084` | 后端本机调试端口（只绑 127.0.0.1） |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 否 | `admin123` / `123456` | 一键脚本创建管理员时使用 |
| `SMTP_HOST` | 否 | `smtp.qq.com` | 邮件服务器 |
| `SMTP_PORT` | 否 | `587` | 465 用 SSL，587 用 STARTTLS |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | 否 | — | QQ 邮箱 + SMTP 授权码（不是登录密码） |
| `NPM_REGISTRY` | 否 | 官方 | npm 镜像，国内可设 `https://registry.npmmirror.com` |
| `PIP_INDEX_URL` | 否 | 官方 | PyPI 镜像，国内可设清华源 |
| `UPLOAD_DIR` | 否 | `/app/uploads` | 上传/聊天 JSON 根目录（compose 已设） |
| `STORAGE_DIR` / `CHAT_STORAGE_PATH` | 否 | `/app/uploads/storage` | JSON 存储根；代码会自动在其下拼 `chat/`、`character/` 等子目录 |
| `RAG_SERVICE_URL` / `RERANKER_URL` | 否 | `http://host.docker.internal:8085` | RAG 服务地址（可选） |

> 注意：代码读取的是 `SMTP_*`，不是旧文档里的 `MAIL_USERNAME` / `MAIL_PASSWORD`。

---

## 8. 日常运维

### 8.1 状态与日志

```bash
docker compose ps                      # 服务状态
docker compose logs -f backend         # 后端日志（Ctrl+C 退出）
docker compose logs -f frontend        # Nginx 日志
docker compose logs -f db              # MySQL 日志
docker stats                           # CPU/内存占用
```

### 8.2 重启 / 停止 / 启动

```bash
docker compose restart                 # 全部重启
docker compose restart backend         # 只重启后端
docker compose stop                    # 停止（保留容器和数据）
docker compose down                    # 删除容器（保留命名卷数据）
docker compose up -d                   # 再次启动
```

### 8.3 更新代码

```bash
cd ~/Dixiyang
git pull
docker compose up -d --build
```

只改前端时也可 `docker compose up -d --build frontend`；只改后端同理。

更新后如果新增了表/列，后端启动时会自动 `create_all` 并补列。

### 8.4 备份

#### 备份 MySQL

```bash
mkdir -p backups
docker compose exec -T db sh -c \
  'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction --routines --triggers dixiyang' \
  > "backups/dixiyang-$(date +%F-%H%M).sql"
```

#### 备份上传/聊天 JSON

```bash
docker run --rm \
  -v dixiyang_uploads_data:/data:ro \
  -v "$PWD/backups":/backup \
  alpine tar czf "/backup/uploads-$(date +%F).tar.gz" -C /data .
```

#### 恢复

```bash
# 1) 停服务（保留数据卷）
docker compose stop backend frontend

# 2) 恢复数据库
cat backups/dixiyang-2026-10-19-1200.sql | \
  docker compose exec -T db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" dixiyang'

# 3) 恢复上传文件
docker run --rm \
  -v dixiyang_uploads_data:/data \
  -v "$PWD/backups":/backup \
  alpine sh -c 'cd /data && tar xzf /backup/uploads-2026-10-19.tar.gz'

# 4) 启动
docker compose start backend frontend
```

> 备份文件默认在 `backups/`，已被 `.gitignore` 忽略，不会被误提交。

### 8.5 彻底重置（⚠️ 删除全部数据）

```bash
docker compose down -v
docker compose up -d --build
docker compose exec -T backend python -m dixiyang.seed_admin
```

`-v` 会删除 MySQL、Redis、上传文件三个命名卷，不可恢复。

---

## 9. 数据存在哪里

| 数据 | Docker 卷 | 容器路径 | 说明 |
|------|-----------|----------|------|
| MySQL 表数据 | `dixiyang_mysql_data` | `/var/lib/mysql` | 用户/小说/聊天元数据等 |
| Redis AOF | `dixiyang_redis_data` | `/data` | 推荐缓存，可丢 |
| 上传/聊天 JSON | `dixiyang_uploads_data` | `/app/uploads` | 封面、背景、聊天链、章节正文 |

查看卷位置：

```bash
docker volume inspect dixiyang_mysql_data
docker volume inspect dixiyang_uploads_data
```

进入容器看文件：

```bash
docker compose exec backend sh
ls -lh /app/uploads
exit
```

---

## 10.（可选）RAG 知识库服务

Docker 快速部署**不包含** RAG 服务，原因：

- Embedding 模型 `bge-m3` 约 2.2 GB；
- 向量库 `storage/vectordb_4060` 约 1.7 GB；
- 二者都不在 Git 仓库里，首次构建时间/体积都很大。

不启动 RAG 不影响登录、小说、角色、时间线、聊天（非知识库检索）、广场、便签。

需要时按 `docs/RAG离线构建流程.md` 与 `DixyangFast/README.md` 操作，或把现成数据从旧电脑复制：

```bash
# 在旧电脑打包（示例）
tar -czf bge-m3.tar.gz -C DixyangFast/models bge-m3
tar -czf vectordb_4060.tar.gz -C DixyangFast/storage vectordb_4060

# 复制到新电脑后解压
mkdir -p DixyangFast/models DixyangFast/storage
tar -xzf bge-m3.tar.gz -C DixyangFast/models
tar -xzf vectordb_4060.tar.gz -C DixyangFast/storage

# 启动 RAG（8085）与 ChromaDB（8000）
cd DixyangFast
./start_rag.sh
```

详见 `docs/Linux迁移指南.md`。

---

## 11. 常见问题

### 11.1 `permission denied while trying to connect to the Docker daemon socket`

```bash
sudo usermod -aG docker "$USER"
newgrp docker
# 仍不行就注销重新登录
```

### 11.2 `port is already allocated` / 8080 被占用

```bash
sudo ss -ltnp | grep ':8080'
```

改 `.env` 的 `WEB_PORT=8081`，再 `docker compose up -d`。

### 11.3 构建很慢 / 超时

- 按 §2.4 配 Docker 镜像加速；
- `.env` 里配 `NPM_REGISTRY` / `PIP_INDEX_URL`；
- 重新执行 `docker compose build`，已完成的层会复用；
- 确认磁盘 ≥ 10 GB：`df -h`。

### 11.4 改了 `DB_PASSWORD` 后后端连不上数据库

MySQL 的 root 密码只在**数据卷首次初始化**时写入。之后改 `.env` 不会改数据库里的密码。

处理方式：

```bash
# 方式 A：把 .env 改回原密码（推荐，数据不丢）
nano .env
docker compose up -d

# 方式 B：进数据库改密码（知道旧密码时）
docker compose exec db mysql -uroot -p
# SQL: ALTER USER 'root'@'%' IDENTIFIED BY '新密码'; FLUSH PRIVILEGES;

# 方式 C：删除数据卷重来（⚠️ 数据全丢）
docker compose down -v
```

### 11.5 前端 502 / 一直转圈

后端还没起来或崩了：

```bash
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 db
```

常见原因：数据库未就绪、`DATABASE_URL` 密码不一致、DeepSeek Key 格式错误（不会阻止启动）。

### 11.6 管理后台登录提示“需要管理员权限”

执行：

```bash
docker compose exec -T backend python -m dixiyang.seed_admin
```

或指定账号提升：

```bash
docker compose exec -T backend python -m dixiyang.seed_admin --username 你的账号
```

### 11.7 AI 聊天 401 / 无响应

- 检查 `.env` 的 `DEEPSEEK_API_KEY` 是否为真实 key；
- 登录 https://platform.deepseek.com 确认余额；
- 修改后 `docker compose up -d backend` 让容器重新读取环境变量。

### 11.8 SSE 不流式 / 一次性返回

本项目 Nginx 已配置 `proxy_buffering off`。如果你在前面又套了 CDN/反向代理，需要在那一层也关闭缓冲并放宽读超时。

### 11.9 上传图片 404

确认上传卷存在：

```bash
docker volume ls | grep uploads
docker compose exec backend ls -lh /app/uploads
```

### 11.10 `git pull` 后技能目录消失

```bash
git config core.hooksPath .githooks
powershell -File scripts/restore-skills.ps1   # Windows
# Linux 没有 PowerShell 时，从 git 历史恢复：
git checkout $(git rev-list -n 1 HEAD -- motion-web-main) -- motion-web-main
```

纯部署环境不需要 `motion-web`，可忽略。

---

## 12.（可选）原生开发模式

只有需要改代码/调试时才用。生产部署优先 Docker。

### 12.1 安装基础环境

```bash
# uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Node 22（nvm 方式，避免系统 Node 过旧）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
node -v        # 应 ≥ v22.12
```

### 12.2 启动 MySQL / Redis（Docker）

> 如果已经用 Docker Compose 部署，先 `docker compose down`（保留数据），避免 3306/6379/8084 端口冲突。

```bash
docker run -d --name mysql-hmdp \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0

docker run -d --name redis-dev \
  -p 6379:6379 \
  redis:7 redis-server --requirepass 123321
```

### 12.3 启动后端

```bash
cd DixyangFast
uv sync
REDIS_URL='redis://:123321@127.0.0.1:6379/0' \
  uv run python src/dixiyang/main.py
```

看到 `Uvicorn running on http://0.0.0.0:8084` 即成功。

### 12.4 启动前端

```bash
cd dixiyang-vue/Dixiyang-vue3
npm ci
npm run dev
```

访问 `http://localhost:5173`。Vite 已把 `/api` 代理到 `localhost:8084`。

### 12.5 创建管理员

```bash
cd DixyangFast
uv run python -m dixiyang.seed_admin
```

---

## 13.（可选）域名 + HTTPS

最省事的是 Caddy（自动申请 Let's Encrypt 证书）：

```bash
sudo apt install -y caddy
```

编辑 `/etc/caddy/Caddyfile`：

```caddyfile
dixiyang.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

```bash
sudo systemctl reload caddy
```

同时：

- 域名 A 记录指向服务器公网 IP；
- 云安全组/防火墙放行 80、443；
- 关闭 8080 的公网暴露（`sudo ufw deny 8080/tcp`），只让 Caddy 访问本机。

Caddy 默认支持 SSE 长连接，无需额外配置。

---

## 14. 部署验收清单

逐项打勾：

- [ ] `docker compose ps` 四个服务均 running/healthy
- [ ] `curl http://localhost:8080/healthz` 返回 `ok`
- [ ] 浏览器能打开落地页
- [ ] `http://localhost:8080/login` 能用 `admin123 / 123456` 登录
- [ ] `admin.html` 能进管理后台，能看到用户/内容管理
- [ ] 新建一本小说、新建角色、刷新后仍在（数据库正常）
- [ ] 上传一张封面，刷新后能看到（上传卷正常）
- [ ] AI 聊天能逐字输出（DeepSeek Key 正常）
- [ ] 局域网另一台设备能打开 `http://IP:8080`
- [ ] 已修改默认管理员密码（设置 → 账号安全 → 修改密码）

---

## 15. 本次部署改造涉及文件

| 文件 | 作用 |
|------|------|
| `docker-compose.yml` | MySQL / Redis / 后端 / 前端四服务编排 |
| `deploy/backend.Dockerfile` | Python 3.11 + uv 后端镜像 |
| `deploy/frontend.Dockerfile` | Node 22 构建 + Nginx 托管 |
| `deploy/nginx.conf` | SPA 兜底、`/api` 反代、SSE 放行 |
| `.dockerignore` | 排除 `.venv`、`node_modules`、模型、上传数据 |
| `scripts/deploy-linux.sh` | Linux 一键部署脚本 |
| `DixyangFast/src/dixiyang/seed_admin.py` | 幂等创建管理员 |
| `DixyangFast/pyproject.toml` / `uv.lock` | 补全运行依赖并锁定版本 |
| `.env.example` | 部署变量模板（修正 SMTP 变量名） |

---

## 16. 变更记录

### v1.0（2026-10-19）

- 新增 Docker Compose 全栈部署（MySQL 8 + Redis 7 + FastAPI + Nginx/Vue）。
- 新增 Linux 一键部署脚本、管理员初始化脚本。
- 补全 Python 运行依赖（`pymysql`、`redis`、`langchain-chroma`、`chromadb`、`python-dotenv`），提交 `uv.lock`。
- 修正 `.env.example` 的 SMTP 变量名，补充 Docker 部署参数。
- 新增 Nginx SSE 反向代理配置与上传大小限制。
- 更新 `README.md` 快速开始与文档索引。
