# Dixiyang - 小说创作管理平台

> 基于 Vue 3 + Python FastAPI 的全栈小说创作平台：AI 聊天 + RAG 知识检索 + 广场社区 + 灵感墙便签。
> Java Spring Boot（dixiyang-engine）为同端口的历史并存实现，当前**未使用**（见下文说明）。

---

## 🚀 从 GitHub 克隆后快速部署（Kubuntu / Ubuntu，推荐）

**只需要安装 Docker**，不需要在本机装 Python、Node.js、MySQL、Redis。

```bash
# 1. 克隆
git clone https://github.com/suziping123/Dixiyang.git
cd Dixiyang

# 2. 一键部署（自动生成 .env / 数据库密码 / JWT，构建并启动全部服务）
chmod +x scripts/deploy-linux.sh
./scripts/deploy-linux.sh

# 3. 浏览器访问
# 用户端：   http://localhost:8080
# 管理后台： http://localhost:8080/admin.html
# 管理员：   admin123 / 123456（首次登录后请修改）
```

脚本会自动启动：MySQL 8 + Redis 7 + Python FastAPI 后端 + Nginx 前端，并创建管理员账号。
首次构建约 3–15 分钟（取决于网络）；国内网络可在 `.env` 配置 npm/PyPI 镜像。

> **完整图文步骤、Docker 安装、局域网访问、升级、备份、排障、HTTPS**：
> 见 **[`docs/Linux部署指南.md`](docs/Linux部署指南.md)**。
>
> 不想用 Docker 的原生开发模式（uv + Node + 本机 MySQL）见该文档 §12。

---

## 项目总览

```
浏览器
    ↓
Vue 前端 (5173 开发 / 8080 Docker+Nginx) ──代理 /api──→ Python 主后端 FastAPI (8084)
                                                          ├── MySQL (3306)：用户/小说/聊天/便签/广场
                                                          ├── Redis (6379)：广场推荐缓存（可选，未起自动降级）
                                                          └── RAG 服务 (8085) + ChromaDB (8000)：向量检索（可选）
```

| 项目 | 技术栈 | 端口 | 用途 |
|------|--------|------|------|
| **Docker 部署（推荐）** | Docker Compose | `8080` | 一键拉起前端 + 后端 + MySQL + Redis |
| **dixiyang-vue/Dixiyang-vue3** | Vue 3 + Vite + Element Plus | `5173`（开发）/ `8080`（Docker） | 前端界面 |
| **DixyangFast**（主后端） | Python 3.11 + FastAPI | `8084` | 业务 API：认证、小说、聊天、RAG、广场、便签、管理后台 |
| **DixyangFast**（RAG 服务） | Python + ChromaDB | `8085` / `8000` | Embedding 向量化 + 知识库（可选） |
| **dixiyang-engine**（备用） | Java 17 + Spring Boot 3.4 | `8084` | 历史实现，与 Python 主后端**同端口二选一**，当前未使用 |
| **MySQL** | Docker 容器 `mysql-hmdp` / Compose `db` | `3306` | 关系数据库 |
| **Redis** | Docker 容器（可选） | `6379` | 广场综合推荐缓存，未启动自动降级 |

---

## ⚠️ 克隆后必做（原生开发/协作必看；Docker 一键部署已自动处理 ②③）

> 直接跑 `./scripts/deploy-linux.sh` 时，脚本会自动生成 `.env`、安装依赖（容器内）并创建管理员，可跳过本章。

### ① 配置 Git Hooks（防技能文件被 pull 删除）

本仓库的 `motion-web` 技能目录（`.agents/`、`.trae/` 等）**已移出版本库、仅本地保留**。
不配 hooks 直接 `git pull`，会把这些本地技能文件删掉。

```powershell
# Windows（克隆后立刻执行一次）
powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1
# 等价手动命令（Linux/macOS 通用）：
git config core.hooksPath .githooks
```

> 万一文件已被 pull 删掉：`powershell -ExecutionPolicy Bypass -File scripts/restore-skills.ps1` 从 git 历史恢复。
> 详见 `docs/技能库出库与同步.md`。

### ② 创建 .env（凭据文件，不入库）

根目录 `.env` 被 gitignore，克隆下来**没有**，原生开发必须自己从模板创建（Docker 一键脚本会自动创建）：

```powershell
# Windows
copy .env.example .env
# Linux/macOS
cp .env.example .env
```

编辑 `.env`，至少填好以下 4 项（主后端启动强依赖，缺了直接报错）：

| 变量 | 说明 |
|------|------|
| `DB_PASSWORD` | MySQL 密码（原生开发用 Docker 容器时可填 `123321`；一键脚本会生成随机密码） |
| `DATABASE_URL` | Python SQLAlchemy 连接串，把其中密码同步改成和 `DB_PASSWORD` 一致 |
| `JWT_SECRET_KEY` | 随机串，生成：`openssl rand -hex 32` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key，从 https://platform.deepseek.com 获取 |

> Java 备用后端（dixiyang-engine）只认**系统环境变量** `DEEPSEEK_API_KEY`，不读 `.env`；
> 当前主后端是 Python，读根 `.env`（`override=True`），无需设置系统变量。

### ③ 安装依赖（见下文各服务章节）

最小可用（原生开发）= MySQL + Python 主后端 + 前端，三步即可进入登录页。
Docker 一键部署不需要本步骤。

---

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| **Docker + Compose v2** | Docker 24+ / Compose 2.20+ | **推荐部署方式**，一条命令拉起全部服务 |
| **Python** | 3.11+ + **uv** | 原生开发/后端调试（Docker 部署无需安装） |
| **Node.js** | **^20.19 或 ≥22.12**（package.json engines 强制） | 原生开发前端；不要用 Node 18（Docker 部署无需安装） |
| **MySQL** | 8.0+（Docker） | 数据库（Docker 部署自动创建） |
| **Redis** | 可选 | 广场综合推荐缓存，不装自动降级（Docker 部署自动包含） |
| **JDK 17 + Maven** | 可选 | 仅在启用 Java 备用后端时需要 |

---

## 1. 克隆项目

```bash
git clone https://github.com/suziping123/Dixiyang.git
cd Dixiyang
# 纯 Docker 部署可跳过 hooks；开发协作建议立刻执行「克隆后必做 ①」
```

---

## 2. 启动 MySQL

### 首次：创建容器（自动建库 `dixiyang`）

```bash
docker run -d --name mysql-hmdp \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0
```

> 推荐直接用顶部「Docker 一键部署」：MySQL、Redis、后端、前端会一起启动，不用手动执行本节。

表结构**无需手动导入**：Python 主后端启动时 `Base.metadata.create_all` 自动建表 + 补列。
（`dixiyang-engine/src/main/resources/db/dixiyang.sql` 是 Java 侧备用完整脚本。）

### 后续启动

```bash
docker start mysql-hmdp
```

---

## 3. 启动 Python 主后端（8084，核心服务）

```powershell
cd DixyangFast

# 首次：创建虚拟环境并安装依赖（读 pyproject.toml + uv.lock）
uv sync

# 启动（Windows 一键，根目录）
cd .. && .\start_backend.bat
# Linux/macOS 一键：
#   ./start_backend.sh
# Linux 手动等价命令：
#   cd DixyangFast && REDIS_URL="redis://:123321@127.0.0.1:6379/0" uv run python src/dixiyang/main.py

# 开发热重载（可选）：set RELOAD=1 后再启动
```

启动成功标志：
```
Uvicorn running on http://0.0.0.0:8084
```

启动时会自动：读根 `.env` → 连 MySQL → 建表/补列 → 挂载全部 router（auth/novel/chat/rag/idea/sticky/admin…）。

> `start_backend.bat` 内置 `REDIS_URL=redis://:123321@127.0.0.1:6379/0`；
> Redis 没启动也没关系，推荐缓存会自动降级，只影响广场"综合推荐"的速度。

---

## 4. 启动 Vue 前端（5173）

```powershell
cd dixiyang-vue\Dixiyang-vue3
npm install
npm run dev
```

启动成功标志：`Local: http://localhost:5173/` ，浏览器打开看到登录页即可。

> 前端已配置代理：`/api` 自动转发到 `localhost:8084`（主后端）。

> **打包**：`npm run build` = `type-check` + `build-only`，当前 **type-check 0 错误**，直接可用。

---

## 5.（可选）Redis —— 广场综合推荐加速

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7 redis-server --requirepass 123321
```

密码须与 `start_backend.bat` 里的 `REDIS_URL` 一致（`123321` 仅本地 dev 用）。

---

## 6.（可选）RAG 服务（8085 + ChromaDB 8000）

RAG = 本地 Embedding（bge-m3）+ ChromaDB 向量库 + Reranker 精排。不启动不影响其他功能（Java/Python 侧日志会提示 RAG 禁用/降级）。

```powershell
cd DixyangFast

# 1) 下载 Embedding 模型到 models/bge-m3/（国内建议先设镜像）
$env:HF_ENDPOINT = "https://hf-mirror.com"
uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3').save('models/bge-m3')"

# 2) 构建向量库（首次，约 10-15 分钟，GPU 机器）
uv run -m rag_shared.processor --hardware rtx_4060 --full

# 3) 一键启动 ChromaDB(8000) + RAG 服务(8085)
.\start_rag.ps1        # Windows
# ./start_rag.sh       # Linux
```

> `start_rag.ps1` 会先检查 `storage/vectordb_4060/` 是否存在，不存在直接退出——先执行第 2 步。

验证：
```bash
curl http://localhost:8085/api/rag/health
```

---

## 7.（备用）Java 后端 dixiyang-engine

> **当前未使用**。它与 Python 主后端同占 8084 端口，**二选一，不能同时启动**。
> 历史接口说明见 `dixiyang-engine/docs/后端接口文档.md`。

```powershell
# 仅在需要时：先设系统环境变量（Java 不读 .env！）
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-你的key", "User")
# Linux: echo 'export DEEPSEEK_API_KEY=sk-你的key' >> ~/.bashrc && source ~/.bashrc

cd dixiyang-engine
mvn spring-boot:run
```

---

## 8. 启动顺序总结

```
最小启动（必选）：
0. Docker Compose  docker compose up -d --build   （推荐：8080 一站式，含 MySQL/Redis）
1. MySQL         docker start mysql-hmdp          （仅原生开发）
2. Python 主后端  ./start_backend.sh               （8084，自动建表；Windows 用 start_backend.bat）
3. Vue 前端       npm run dev                      （5173）

可选：
4. Redis         docker start redis-dev            （广场综合推荐加速）
5. RAG 服务      ./start_rag.sh                    （8085 + ChromaDB 8000，需先构建向量库）
```

---

## 环境变量参考

主后端（Python）从**项目根 `.env`** 读取；Java 备用后端只认系统环境变量。

| 变量 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | **是** | DeepSeek API Key（AI 聊天/补全） |
| `JWT_SECRET_KEY` | **是** | JWT 签名密钥（Python 侧 token） |
| `DB_PASSWORD` | **是** | MySQL 密码（Docker 容器默认 `123321`） |
| `DATABASE_URL` | **是** | Python SQLAlchemy 连接串（密码与上一项一致；Docker 内由 compose 覆盖主机） |
| `DB_NAME` / `WEB_PORT` / `BACKEND_PORT` | 否 | Docker 部署：数据库名 / 前端端口(8080) / 后端调试端口(8084) |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 否 | 一键脚本创建管理员（默认 `admin123` / `123456`） |
| `SMTP_HOST` / `SMTP_PORT` | 否 | QQ SMTP 邮箱验证码（默认 `smtp.qq.com:587`） |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | 否 | 发件邮箱 + SMTP 授权码 |
| `REDIS_URL` | 否 | 默认 `redis://localhost:6379/0`；Docker 内自动指向 `redis` |
| `UPLOAD_DIR` | 否 | 上传/JSON 存储根目录，默认 `uploads/`（Docker 为 `/app/uploads`） |
| `CHAT_STORAGE_PATH` | 否 | 聊天链文件目录，等于 `STORAGE_DIR`（代码会自动拼 `chat/`） |
| `RELOAD` | 否 | `1` 开启 uvicorn 热重载（开发） |
| `NPM_REGISTRY` / `PIP_INDEX_URL` | 否 | Docker 构建镜像源（国内加速） |
| `HF_ENDPOINT` | 否 | 模型下载镜像，慢时设 `https://hf-mirror.com` |
| `CHROMADB_HOST` / `CHROMADB_PORT` | 否 | 默认 `::1:8000` |

---

## 项目结构

```
Dixiyang/
├── dixiyang-vue/Dixiyang-vue3/   # Vue 前端（开发 5173 / Docker 8080）
│   └── src/{views,components,composables,api,stores,utils}
│
├── DixyangFast/                  # Python 全家桶
│   ├── src/dixiyang/             # ★ 主后端（8084）：main.py + routers(17个) + services + models
│   ├── python_api/main.py        # RAG 服务（8085）：Embedding + Reranker + Web UI
│   ├── models/bge-m3/            # 本地 Embedding 模型（需自行下载）
│   ├── storage/vectordb_4060/    # ChromaDB 向量库（需自行构建）
│   ├── start_rag.ps1 / .sh       # RAG 一键启动
│   └── pyproject.toml / uv.lock  # 依赖（uv sync）
│
├── deploy/                       # Docker 镜像与 Nginx 配置
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml            # ★ 一键部署：MySQL + Redis + 后端 + 前端
├── .dockerignore                 # 构建上下文裁剪
├── scripts/deploy-linux.sh       # ★ Linux 一键部署脚本
├── scripts/setup-hooks.ps1 / restore-skills.ps1
│
├── dixiyang-engine/              # Java 后端（备用，与 Python 同端口 8084）
│   └── src/main/{java,resources/{application.yml,db/dixiyang.sql}}
│
├── rag-shared/                   # RAG 共享库（数据处理、向量构建）
├── docs/                         # 全部开发文档（见 docs/README.md 索引）
├── uploads/                      # 统一存储：聊天链 JSON / 封面 / 背景图
├── storage/                      # 运行期数据
├── .env.example                  # 环境变量模板（复制为 .env 后填写）
├── start_backend.sh / .bat       # 原生开发后端一键启动
└── AGENTS.md                     # AI 协作规则（贡献必读）
```

---

## API 速查（主后端 localhost:8084/api）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` `/auth/register` | 登录 / 注册 |
| GET | `/novel/listall` | 小说列表 |
| POST | `/novel/create` `/novel/update/{id}` `/novel/delete/{id}` | 小说增改删 |
| GET/POST | `/novelCharacter/...` | 角色 CRUD |
| GET/POST | `/timeline/...` `/storyNode/...` | 时间线 / 故事节点 |
| GET/POST | `/volume/...` `/chapter/...` | 卷 / 章节 |
| POST | `/chat/stream` `/chat/regenerate` | AI 聊天（SSE 真流式）/ 重新生成 |
| GET | `/chatHistory/sessions` `/chatHistory/history/{sessionId}` | 聊天会话 / 历史 |
| POST | `/rag/search` `/rag/embed` `/rag/documents` `/rag/stats` `/rag/health` | RAG 检索（8085） |
| GET/POST | `/idea/posts` `/idea/draft` `/idea/collect` ... | 广场（点子库） |
| GET/POST | `/sticky/notes` | 灵感墙便签 |
| GET/POST | `/admin/stats` `/admin/users` `/admin/role` | 管理后台（需 admin 角色） |
| POST | `/upload/novel-cover` `/upload/idea-image` | 图片上传（MD5 去重） |

> 完整契约以 `docs/前后端接口对照分析.md` 与各 router 源码为准。

---

## 存储架构

大文本一律落**本地 JSON 文件**，数据库只存引用。DB 中的文件引用统一用 `__file__:` 前缀 + 相对路径：

| 字段 | 格式示例 | 说明 |
|------|---------|------|
| `extra` | `__file__:character/{id}.json` | 角色设定 |
| `head_path` | `__file__:chat/{userId}/{sessionId}/{file}.json` | 聊天链头文件 |
| `custom_bgs` | `__file__:user/customBgs/{userId}.json` | 自定义背景 |
| `font_colors_json` | `__file__:user/fontColors/{userId}.json` | 字体颜色 |
| `cover_url` | `/api/uploads/covers/{filename}.png` | 例外：HTTP URL |

```
uploads/storage/chat/{userId}/{sessionId}/
├── {timestamp}_{rand}.json   # 链文件（next 指针 = 纯文件名）
├── edits.json                 # 编辑修正记录（注入 AI prompt 学习）
└── summary.json               # 历史摘要
```

---

## 常见问题

### Q: Linux 上最简单怎么部署？
装 Docker 后运行 `./scripts/deploy-linux.sh`，完整步骤见 [`docs/Linux部署指南.md`](docs/Linux部署指南.md)。

### Q: Docker 部署后 8080 打不开 / 502
```bash
docker compose ps
docker compose logs --tail=100 backend db
```
等后端 healthy 后再刷新；端口冲突改 `.env` 的 `WEB_PORT`。

### Q: 改了 DB_PASSWORD 后连不上 MySQL
密码只在数据卷首次初始化时写入。改回原密码，或进容器 `ALTER USER`，详见部署指南 §11.4。

### Q: `uv run python src/dixiyang/main.py` 报数据库连接失败
MySQL 没起或 `.env` 没配好：`docker start mysql-hmdp`；检查 `.env` 的 `DB_PASSWORD` / `DATABASE_URL`。

### Q: 启动报 JWT / SECRET 相关错误
`.env` 缺 `JWT_SECRET_KEY`，生成一个填入：`openssl rand -hex 32`。

### Q: git pull 之后 motion-web 技能没了 / `.agents` 目录消失
没配 Git Hooks。执行 `powershell -File scripts/setup-hooks.ps1`，再用 `scripts/restore-skills.ps1` 从 git 历史恢复文件。

### Q: 8084 端口被占用
Python 主后端与 Java 备用后端**同端口**，只能跑一个。确认没有 `mvn spring-boot:run` 残留进程。

### Q: 广场"综合推荐"很慢 / 日志刷 Redis 连接失败
Redis 没启动，已自动降级走 DB 直查（功能可用，仅变慢）。要加速见「5.（可选）Redis」。

### Q: start_rag.ps1 直接退出，提示向量库不存在
需先构建向量库（见「6.（可选）RAG 服务」第 2 步）；模型下载慢设 `HF_ENDPOINT=https://hf-mirror.com`。

### Q: Java 启动报 "Could not resolve placeholder 'DEEPSEEK_API_KEY'"
Java 只读系统环境变量，不读 `.env`。设好后**重开终端**再启动（见「7.（备用）Java 后端」）。

### Q: 局域网里手机/另一台电脑访问不了前端
开发服务器已开 `host: true`；Windows 防火墙放行 5173/8084，并可用 adb reverse 调安卓。详见 `docs/局域网访问与launch调试.md`。

---

## 双机协作：Windows 构建向量库 + Linux 查询

两台机器必须用**同一个 Embedding 模型**（`bge-m3`，1024 维）。

```powershell
# Windows（RTX 4060 GPU）构建（约 10-15 分钟）
cd DixyangFast
$env:HF_ENDPOINT = "https://hf-mirror.com"
uv run -m rag_shared.processor --hardware rtx_4060 --full

# 打包传输
tar -czf vectordb_4060.tar.gz -C storage vectordb_4060
scp vectordb_4060.tar.gz 用户名@192.168.1.x:~/Dixiyang/DixyangFast/storage/
```

```bash
# Linux 解压
cd ~/Dixiyang/DixyangFast/storage && tar -xzf vectordb_4060.tar.gz
```

---

## 文档导航

完整索引见 **`docs/README.md`**。常用：

| 文档 | 说明 |
|------|------|
| `docs/Linux部署指南.md` | **Linux/Kubuntu 从零部署（Docker 一键、升级、备份、排障）** |
| `docs/系统总览.md` | 架构与端口全貌 |
| `docs/功能完成状态.md` | 各模块完成度对照 |
| `docs/前后端接口对照分析.md` | API 契约与前后端匹配情况 |
| `docs/后端开发技术文档.md` | 后端技术细节 |
| `dixiyang-engine/docs/后端接口文档.md` | Java 侧接口（备用后端） |
| `DixyangFast/README.md` / `rag-shared/README.md` | Python 侧说明 |
| `docs/技能库出库与同步.md` | Git Hooks 与技能文件恢复（**贡献前必读**） |
| `docs/局域网访问与launch调试.md` | 局域网访问 / VS Code launch 调试 |
| `docs/灵感墙便利贴实施记录.md` 等 | 各功能实施记录（docs 目录） |

---

**最后更新**: 2026-10-19
**维护者**: lijiajia
