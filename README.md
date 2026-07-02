# Dixiyang - 小说创作管理平台 (Monorepo)

> 采用前后端分离 + 多语言后端架构，为小说创作者提供全方位的工具支持。

## 项目总览

| 项目 | 技术栈 | 用途 | 端口 |
|------|--------|------|------|
| **dixiyang-engine** | Java 17 + Spring Boot 3.4 | 后端服务：用户认证、小说管理、AI 聊天、RAG 检索 | `8084/api` |
| **dixiyang-vue** | Vue 3 + Vite + Element Plus | 前端界面：创作管理平台 + RAG 聊天界面 | `5173` |
| **DixyangFast** | Python 3.11 + FastAPI + ChromaDB | Python 后端：Embedding 服务 + RAG Web 可视化 | `8085` |
| **rag-shared** | Python 包 | 共享库：多硬件配置、数据处理流水线、向量构建 | — |
| **ChromaDB** | 独立服务 | 向量数据库，存储文档向量 | `8000` |
| **MySQL** | Docker 容器 `mysql-hmdp` | 关系数据库，存储用户、小说、聊天记录 | `3306` |

## 三端关系

```
用户浏览器
    ↓
Vue 前端 (5173) ──代理 /api──→ Java 后端 (8084)
                                    ├── MySQL (3306)：用户/小说/聊天记录
                                    ├── ChromaDB (8000)：向量检索
                                    └── Python Embedding (8085)：query 向量化
                                    
Python Web UI (8085/rag) ← 浏览器直接访问：向量库统计/搜索/浏览
```

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| JDK | 17 | sdkman 管理，`~/.sdkman/candidates/java/17.0.10-tem` |
| Maven | 3.6+ | Java 构建 |
| Node.js | 18+ | 前端构建 |
| Python | 3.11+ | Python 后端 |
| uv | 最新 | Python 包管理器 |
| Docker | 推荐 | MySQL 容器 |

## 快速启动（Linux 开发机）

### 第 1 步：启动 MySQL（Docker）

```bash
# 已有容器直接启动
docker start mysql-hmdp

# 新建容器（首次）
docker run -d --name mysql-hmdp \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0

# 导入表结构
docker exec -i mysql-hmdp mysql -u root -p123321 dixiyang < dixiyang-engine/src/main/resources/db/dixiyang.sql
```

### 第 2 步：启动 Java 后端 (dixiyang-engine)

```bash
cd dixiyang-engine

# IDEA: 设置 Project SDK = JDK 17，运行 DixiyangEngineApplication
# 命令行:
export JAVA_HOME=~/.sdkman/candidates/java/17.0.10-tem
./mvnw spring-boot:run
```

启动后: `http://localhost:8084/api`

> 注意：application.yml 中 API Key 读取顺序：`DEEPSEEK_API_KEY` → `DS_API_KEY`，需确保环境变量已设置。

### 第 3 步：启动 Vue 前端 (dixiyang-vue)

```bash
cd dixiyang-vue/Dixiyang-vue3
npm install
npm run dev
```

启动后: `http://localhost:5173`（自动代理 `/api` → `localhost:8084`）

### 第 4 步：启动 Python 服务（RAG 可视化 + Embedding）

```bash
cd DixyangFast

# 启动向量库和 Embedding 服务（一键）
./start_rag.sh

# 或手动启动
# 终端1: ChromaDB
chroma run --path storage/vectordb_4060 --port 8000

# 终端2: Embedding 服务
HF_HUB_OFFLINE=1 .venv/bin/python python_api/main.py
```

启动后:
- Embedding API: `http://localhost:8085/api/rag/embed`
- **RAG Web 可视化**: `http://localhost:8085/rag`（浏览器打开）
- ChromaDB: `http://localhost:8000`

### 启动顺序总结

```
MySQL (3306) → Java 后端 (8084) → Vue 前端 (5173)
                                → Python 服务 (8085) + ChromaDB (8000)
```

## 各项目详细说明

### 1. dixiyang-engine（Java 后端）

**做什么**: 小说创作管理的核心服务

- 用户注册/登录（Spring Security + JWT）
- 小说 CRUD + 封面上传
- 角色、时间线、故事节点管理
- AI 聊天助手（DeepSeek API）
- RAG 智能检索（调 ChromaDB + Python Embedding）

**关键文件**:
- `ChatController.java` - AI 聊天 + RAG 检索入口
- `RagService.java` - ChromaDB HTTP 客户端
- `application.yml` - 端口 8084，context-path `/api`

### 2. dixiyang-vue（Vue 前端）

**做什么**: 用户界面

- 创作管理：小说/角色/时间线/故事节点
- AI 聊天界面：支持 RAG 检索开关、流式输出
- 聊天历史管理

**关键文件**:
- `vite.config.js` - 代理 `/api` → `localhost:8084`
- `src/views/Chat*.vue` - 聊天界面

### 3. DixyangFast（Python 后端）

**做什么**: RAG 课程作业 + 向量库管理

- **Embedding 服务** (`POST /api/rag/embed`): 将文本转为 bge-m3 向量
- **RAG Web 可视化** (`GET /rag`): 浏览向量库统计、搜索测试、文档浏览
- **向量库构建**: 在 Windows RTX 4060 上运行，将书籍/数据集向量化
- **ChromaDB 代理**: 转发请求到 ChromaDB HTTP API

**启动方式**:
```bash
cd DixyangFast
./start_rag.sh  # 一键启动 ChromaDB + Embedding 服务
```

**关键文件**:
- `python_api/main.py` - FastAPI 服务（端口 8085）
- `start_rag.sh` - 一键启动脚本

### 4. rag-shared（共享库）

**做什么**: 跨项目共享的 RAG 核心逻辑

- 多硬件配置管理（RTX 4060 / R5 5600U / 通用）
- 数据加载器（Markdown、CSV、JSON、TXT）
- Embedding 模型封装（bge-m3）
- 向量库操作封装（ChromaDB）
- 语义文本切分

**配置文件**:
- `config/rag_base.yaml` - 基础配置（数据源、书籍分类）
- `config/rag_rtx_4060.yaml` - Windows GPU 配置（bge-m3 FP16）
- `config/rag_r5_5600u.yaml` - Linux CPU 配置（bge-m3 FP32）

## 双机协作：Windows 构建 + Linux 查询

**核心思路**: Windows（RTX 4060 GPU）构建向量库 → 传输到 Linux（R5 5600U CPU）查询

**关键前提**: 两台机器用同一个 Embedding 模型（`bge-m3`，1024 维）

### Windows 上构建向量库

```powershell
cd Dixiyang\DixyangFast
.\.venv\Scripts\activate

# 设置 HuggingFace 镜像
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 首次全量构建（约 10-15 分钟）
python -m rag_shared.processor --hardware rtx_4060 --full

# 后续增量更新
python -m rag_shared.processor --hardware rtx_4060
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

## 端口速查

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | Docker 容器 `mysql-hmdp` |
| Java 后端 | 8084 | context-path: `/api` |
| Vue 前端 | 5173 | Vite dev server |
| Python Embedding | 8085 | FastAPI + RAG Web UI |
| ChromaDB | 8000 | 向量数据库 HTTP API |

## 环境变量

```bash
# DeepSeek API Key（Java 后端用）
export DEEPSEEK_API_KEY=sk-xxx
# 或
export DS_API_KEY=sk-xxx

# HuggingFace 镜像（模型下载用）
export HF_ENDPOINT=https://hf-mirror.com
```

## 常见问题

### Java 启动报 "RAG 功能已禁用"
ChromaDB 未启动。运行 `./start_rag.sh` 启动 ChromaDB。

### Embedding 服务报连接失败
检查 ChromaDB 是否在 8000 端口运行：`curl http://localhost:8000/api/v2/heartbeat`

### 向量库显示 0 条数据
向量库目录 `storage/vectordb_4060/` 为空或未传输。在 Windows 上构建后传到 Linux。

### 前端聊天无响应
检查 Java 后端是否启动：`curl http://localhost:8084/api/chat/session`

### 模型下载慢
设置 HuggingFace 镜像：`export HF_ENDPOINT=https://hf-mirror.com`

## 文档导航

| 文档 | 位置 | 说明 |
|------|------|------|
| 项目总体情况总结 | `docs/项目总体情况总结.md` | 项目全貌 |
| 后端接口文档 | `dixiyang-engine/docs/后端接口文档.md` | API 详细说明 |
| RAG 可视化指南 | `docs/向量库可视化指南.md` | Python Web UI 使用 |
| 共享库文档 | `rag-shared/README.md` | 核心库使用指南 |
| Python 端文档 | `DixyangFast/README.md` | 课程作业实操 |

---

**最后更新**: 2026-07-01  
**维护者**: lijiajia
