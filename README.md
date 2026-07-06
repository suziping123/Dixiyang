# Dixiyang - 小说创作管理平台

> 基于 Vue 3 + Spring Boot 3 + Python FastAPI 的全栈小说创作平台，集成 AI 聊天助手 + RAG 知识检索 + Reranker 精排。

## 项目总览

```
用户浏览器
    ↓
Vue 前端 (5173) ──代理 /api──→ Java 后端 (8084)
                                    ├── MySQL (3306)：用户/小说/聊天记录
                                    ├── ChromaDB (8000)：向量检索
                                    └── Python Embedding (8085)：query 向量化 + Reranker 精排

Python Web UI (8085/rag) ← 浏览器直接访问：向量库统计/搜索/文档浏览
```

| 项目 | 技术栈 | 端口 | 用途 |
|------|--------|------|------|
| **dixiyang-engine** | Java 17 + Spring Boot 3.4 | `8084/api` | 核心后端：用户认证、小说管理、AI 聊天、RAG |
| **dixiyang-vue** | Vue 3 + Vite + Element Plus | `5173` | 前端界面 |
| **DixyangFast** | Python 3.11 + FastAPI | `8085` | Python 后端：RAG 服务 + Embedding |
| **rag-shared** | Python 包 | — | 共享库：数据处理、向量构建 |
| **ChromaDB** | 独立服务 | `8000` | 向量数据库 |
| **MySQL** | Docker 容器 `mysql-hmdp` | `3306` | 关系数据库 |

---

## 环境要求

| 组件 | 版本 | 安装方式 | 说明 |
|------|------|---------|------|
| **JDK** | 17 | sdkman | Java 运行环境 |
| **Maven** | 3.6+ | sdkman | Java 构建工具 |
| **Node.js** | 18+ | nvm | 前端运行环境 |
| **npm** | 9+ | 随 Node.js | 前端包管理 |
| **Python** | 3.11+ | uv | Python 运行环境 |
| **uv** | 最新 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python 包管理器 |
| **Docker** | 推荐 | 系统安装 | MySQL 容器 |

---

## 1. 克隆项目

```bash
git clone git@github.com:suziping123/Dixiyang.git
cd Dixiyang
```

---

## 2. 安装环境

### 2.1 安装 sdkman（管理 JDK + Maven）

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 安装 JDK 17
sdk install java 17.0.10-tem
sdk use java 17.0.10-tem

# 安装 Maven
sdk install maven
```

验证：
```bash
java -version    # openjdk version "17.0.10"
mvn -version     # Apache Maven 3.9+
```

### 2.2 安装 Node.js（管理前端）

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc

# 安装 Node.js 18+
nvm install 18
nvm use 18
```

验证：
```bash
node -v    # v18.x+
npm -v     # 9.x+
```

### 2.3 安装 Python + uv

```bash
# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 安装 Python 3.11
uv python install 3.11
```

验证：
```bash
uv --version    # uv x.x.x
python3 --version  # Python 3.11.x
```

### 2.4 安装 Docker（MySQL 用）

```bash
# 参考 https://docs.docker.com/engine/install/
# 安装完成后验证
docker --version
```

---

## 3. 启动 MySQL

### 3.1 创建容器（首次）

```bash
docker run -d --name mysql-hmdp \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0
```

### 3.2 导入表结构

```bash
docker exec -i mysql-hmdp mysql -u root -p123321 dixiyang \
  < dixiyang-engine/src/main/resources/db/dixiyang.sql
```

### 3.3 后续启动

```bash
docker start mysql-hmdp
```

验证：
```bash
curl http://localhost:3306  # 连接正常即可
```

---

## 4. 启动 Java 后端（dixiyang-engine）

### 4.1 设置环境变量

```bash
# DeepSeek API Key（AI 聊天必需）
export DEEPSEEK_API_KEY=sk-你的key
# 或者
export DS_API_KEY=sk-你的key

# 可选：自定义存储路径（默认 /home/lijiajia/项目/Dixiyang/uploads/storage/chat）
export CHAT_STORAGE_PATH=/你的路径/uploads/storage/chat
```

建议写入 `~/.bashrc` 永久生效：
```bash
echo 'export DEEPSEEK_API_KEY=sk-你的key' >> ~/.bashrc
source ~/.bashrc
```

### 4.2 编译并启动

```bash
cd dixiyang-engine

# 方式一：Maven 命令行
mvn spring-boot:run

# 方式二：IDEA
# 设置 Project SDK = JDK 17，运行 DixiyangEngineApplication
```

启动成功标志：
```
Started DixiyangEngineApplication in x.xx seconds
```

验证：
```bash
curl http://localhost:8084/api/auth/login
```

---

## 5. 启动 Vue 前端（dixiyang-vue）

```bash
cd dixiyang-vue/Dixiyang-vue3

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动成功标志：
```
Local: http://localhost:5173/
```

验证：浏览器打开 `http://localhost:5173`，看到登录页面即可。

> 前端已配置代理：`/api` 自动转发到 `localhost:8084`。

---

## 6. 启动 Python RAG 服务（DixyangFast）

### 6.1 安装 Python 依赖

```bash
cd DixyangFast

# 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt

# 安装 chromadb（RAG 依赖）
uv pip install chromadb
```

### 6.2 下载 Embedding 模型

模型文件需要放在 `DixyangFast/models/bge-m3/` 目录下：

```bash
# 方式一：从 HuggingFace 下载（需要网络）
cd DixyangFast
mkdir -p models/bge-m3
python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-m3')
model.save('models/bge-m3')
"

# 方式二：从已有备份传输（推荐，如果有的话）
# scp -r /path/to/bge-m3 DixyangFast/models/
```

### 6.3 下载 Reranker 模型（可选，推荐）

Reranker 用于搜索结果精排，显著提升检索质量：

```bash
# 模型放在 /home/lijiajia/models/bge-reranker-large/
# 或修改环境变量指向其他路径
export RAG_RERANKER_MODEL=/你的路径/bge-reranker-large
```

### 6.4 启动服务

```bash
cd DixyangFast

# 方式一：一键启动（推荐）
./start_rag.sh

# 方式二：手动启动
# 终端 1：ChromaDB 向量数据库
chroma run --path storage/vectordb_4060 --port 8000

# 终端 2：Python RAG 服务（Embedding + Reranker + Web UI）
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python python_api/main.py
```

启动成功标志：
```
加载 Embedding 模型: .../models/bge-m3 ...
模型加载完成，维度: 1024
加载 Reranker 模型: .../bge-reranker-large ...
Reranker 模型加载完成
Uvicorn running on http://0.0.0.0:8085
```

验证：
```bash
# 健康检查
curl http://localhost:8085/api/rag/health

# 测试 Embedding
curl -X POST http://localhost:8085/api/rag/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本"}'

# 测试 Reranker
curl -X POST http://localhost:8085/api/rag/rerank \
  -H "Content-Type: application/json" \
  -d '{"query": "主角性格", "documents": ["勇敢的人", "天气很好", "内向坚韧"], "top_k": 2}'
```

---

## 7. 启动顺序总结

```
1. MySQL (3306)          ← docker start mysql-hmdp
2. Java 后端 (8084)      ← cd dixiyang-engine && mvn spring-boot:run
3. Vue 前端 (5173)       ← cd dixiyang-vue/Dixiyang-vue3 && npm run dev
4. Python RAG (8085)     ← cd DixyangFast && ./start_rag.sh
5. ChromaDB (8000)       ← 随 start_rag.sh 自动启动
```

最小启动（不需要 RAG 功能时，只需 1-3 步）。

---

## 环境变量参考

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `DEEPSEEK_API_KEY` | **是** | — | DeepSeek API 密钥，AI 聊天必需 |
| `DS_API_KEY` | 否 | — | DEEPSEEK_API_KEY 的别名 |
| `DB_USERNAME` | 否 | `root` | MySQL 用户名 |
| `DB_PASSWORD` | 否 | `123321` | MySQL 密码 |
| `CHAT_STORAGE_PATH` | 否 | `/home/lijiajia/项目/Dixiyang/uploads/storage/chat` | 聊天文件存储路径 |
| `CHROMADB_HOST` | 否 | `localhost` | ChromaDB 地址 |
| `CHROMADB_PORT` | 否 | `8000` | ChromaDB 端口 |
| `HF_ENDPOINT` | 否 | — | HuggingFace 镜像，模型下载慢时设置 `https://hf-mirror.com` |
| `RAG_USE_RERANKER` | 否 | `true` | 是否启用 Reranker 精排 |
| `RAG_RERANKER_MODEL` | 否 | `/home/lijiajia/models/bge-reranker-large` | Reranker 模型路径 |
| `UPLOAD_DIR` | 否 | `/home/lijiajia/项目/Dixiyang/uploads` | 统一上传/存储根目录 |

---

## 项目结构

```
Dixiyang/
├── dixiyang-engine/              # Java 后端（Spring Boot）
│   ├── src/main/java/.../        # 源码
│   │   ├── Controller/           # REST 接口
│   │   ├── Service/              # 业务逻辑
│   │   │   ├── chat/             # Agent Pipeline + RAG 工具
│   │   │   └── impl/             # 服务实现
│   │   ├── Entity/               # 数据实体
│   │   ├── Mapper/               # MyBatis 映射
│   │   └── Utils/                # 工具类（StorageService）
│   ├── src/main/resources/
│   │   ├── application.yml       # 配置文件
│   │   └── db/dixiyang.sql       # 数据库建表脚本
│   └── pom.xml                   # Maven 依赖
│
├── dixiyang-vue/                 # Vue 前端
│   └── Dixiyang-vue3/
│       ├── src/
│       │   ├── views/            # 页面组件
│       │   ├── components/       # 通用组件
│       │   ├── composables/      # 组合式函数
│       │   ├── api/              # API 调用封装
│       │   └── utils/            # 工具函数
│       ├── vite.config.ts        # Vite 代理配置
│       └── package.json          # npm 依赖
│
├── DixyangFast/                  # Python 后端（FastAPI）
│   ├── python_api/main.py        # RAG 服务主文件（端口 8085）
│   ├── src/dixiyang/             # Python 业务代码
│   │   ├── routers/              # 路由（chat, character, file...）
│   │   ├── services/             # 服务（chain_file_manager, knowledge_search_tool...）
│   │   ├── models/               # 数据模型
│   │   └── config.py             # 配置
│   ├── models/                   # 本地模型文件
│   │   └── bge-m3/               # Embedding 模型
│   ├── storage/                  # ChromaDB 数据
│   │   └── vectordb_4060/        # 向量库
│   └── start_rag.sh              # 一键启动脚本
│
├── rag-shared/                   # RAG 共享库
│   ├── config/                   # 多硬件配置（GPU/CPU）
│   └── python/rag_shared/        # 核心逻辑
│
├── uploads/                      # 统一存储目录
│   ├── storage/                  # JSON 数据存储
│   │   ├── chat/                 # 聊天记录链文件
│   │   ├── character/            # 角色设定
│   │   └── user/                 # 用户配置
│   ├── covers/                   # 封面图
│   └── backgrounds/              # 背景图
│
├── .gitignore                    # Git 忽略规则
└── README.md                     # 本文件
```

---

## API 接口速查

### Java 后端 (localhost:8084/api)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/register` | 用户注册 |
| GET | `/novel/listall` | 小说列表 |
| POST | `/novel/create` | 创建小说 |
| POST | `/novel/update/{id}` | 更新小说 |
| POST | `/novel/delete/{id}` | 删除小说 |
| GET | `/novelCharacter/all/{novelId}` | 角色列表 |
| POST | `/novelCharacter/create` | 创建角色 |
| POST | `/novelCharacter/update/{id}` | 更新角色 |
| POST | `/novelCharacter/delete/{id}` | 删除角色 |
| POST | `/chat/stream` | AI 聊天（SSE 流式） |
| POST | `/chat/sync` | AI 聊天（同步） |
| POST | `/chat/regenerate` | 重新生成 AI 回答 |
| PUT | `/chatHistory/message/{sessionId}` | 编辑消息 |
| GET | `/chatHistory/sessions` | 聊天会话列表 |
| GET | `/chatHistory/history/{sessionId}` | 聊天历史 |
| POST | `/upload/novel-cover` | 上传封面 |
| GET | `/userConfig/background` | 获取背景配置 |
| POST | `/userConfig/background` | 更新背景配置 |

### Python RAG 服务 (localhost:8085)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rag/embed` | 文本向量化 |
| POST | `/api/rag/embed/batch` | 批量向量化 |
| POST | `/api/rag/search` | 向量检索（含 Reranker 精排） |
| POST | `/api/rag/rerank` | Reranker 重排序 |
| GET | `/api/rag/stats` | 向量库统计 |
| GET | `/api/rag/documents` | 文档浏览 |
| GET | `/api/rag/health` | 健康检查 |
| GET | `/rag` | Web 可视化页面 |

---

## 常见问题

### Q: Java 启动报 "RAG 功能已禁用"
ChromaDB 未启动。运行 `./start_rag.sh` 或手动启动 ChromaDB。

### Q: Embedding 服务报连接失败
检查 ChromaDB 是否在 8000 端口运行：
```bash
curl http://localhost:8000/api/v2/heartbeat
```

### Q: 前端聊天无响应
检查 Java 后端是否启动：
```bash
curl http://localhost:8084/api/auth/login
```

### Q: 模型下载慢
设置 HuggingFace 镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: 向量库显示 0 条数据
向量库目录 `storage/vectordb_4060/` 为空。需要在 Windows（有 GPU）上构建后传到 Linux。

### Q: Reranker 启动失败
检查模型路径是否正确：
```bash
ls -la /home/lijiajia/models/bge-reranker-large/
```
reranker 未安装时会自动跳过，不影响其他功能。

### Q: 前端代理不生效
检查 `vite.config.ts` 中代理配置：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8084',
    changeOrigin: true
  }
}
```

---

## 双机协作：Windows 构建 + Linux 查询

**核心思路**: Windows（RTX 4060 GPU）构建向量库 → 传输到 Linux（CPU）查询

两台机器必须用同一个 Embedding 模型（`bge-m3`，1024 维）。

### Windows 上构建向量库

```powershell
cd Dixiyang\DixyangFast
.\.venv\Scripts\activate
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 首次全量构建（约 10-15 分钟）
python -m rag_shared.processor --hardware rtx_4060 --full
```

### 传输向量库到 Linux

```powershell
# Windows 压缩
tar -czf vectordb_4060.tar.gz -C DixyangFast\storage vectordb_4060

# scp 传到 Linux
scp vectordb_4060.tar.gz 用户名@192.168.1.x:~/项目/Dixiyang/DixyangFast/storage/
```

### Linux 上解压

```bash
cd ~/项目/Dixiyang/DixyangFast/storage
tar -xzf vectordb_4060.tar.gz
rm vectordb_4060.tar.gz
```

---

## 存储架构

### 文件引用格式（`__file__:` 前缀）

所有 DB 中的文件引用字段使用 `__file__:` 前缀 + 相对路径：

| 字段 | 格式示例 | 说明 |
|------|---------|------|
| `extra` | `__file__:character/{id}.json` | 角色设定 |
| `head_path` | `__file__:chat/{userId}/{sessionId}/{file}.json` | 聊天链头文件 |
| `custom_bgs` | `__file__:user/customBgs/{userId}.json` | 用户自定义背景 |
| `font_colors_json` | `__file__:user/fontColors/{userId}.json` | 字体颜色配置 |
| `cover_url` | `/api/uploads/covers/{filename}.png` | 封面图（HTTP URL） |

### 聊天链文件结构

```
uploads/storage/chat/{userId}/{sessionId}/
├── {timestamp}_{rand}.json   # 链文件（next 指针连接）
├── edits.json                 # 编辑修正记录
└── summary.json               # 历史摘要
```

---

## 文档导航

| 文档 | 位置 | 说明 |
|------|------|------|
| 项目总体情况 | `docs/项目总体情况总结.md` | 项目全貌 |
| 后端接口文档 | `dixiyang-engine/docs/后端接口文档.md` | API 详细说明 |
| RAG 可视化指南 | `docs/向量库可视化指南.md` | Python Web UI 使用 |
| 共享库文档 | `rag-shared/README.md` | 核心库使用指南 |
| Python 端文档 | `DixyangFast/README.md` | Python 后端说明 |
| 存储迁移文档 | `DixyangFast/docs/STORAGE_MIGRATION.md` | 存储架构变更 |

---

**最后更新**: 2026-07-06
**维护者**: lijiajia
