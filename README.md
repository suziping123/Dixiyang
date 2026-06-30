# Dixiyang - 小说创作管理平台 (Monorepo)

> 采用前后端分离 + 多语言后端架构，为小说创作者提供全方位的工具支持。

## 🏗️ Monorepo 架构

```
Dixiyang/                              # 根目录
├── dixiyang-engine/                   # ☕ Java Spring Boot 后端（找工作主力）
│   ├── src/main/java/                 # 业务代码
│   ├── docs/                          # 后端接口文档
│   ├── python_api/                    # Python 子进程集成入口
│   │   └── dixiyang/                  # 供 Java 调用的 Python API
│   ├── pom.xml                        # Maven 配置
│   └── AGENTS.md                      # 后端开发指南
│
├── dixiyang-vue/                      # 🎨 Vue 3 前端
│   ├── Dixiyang-vue3/                 # Vite + Vue 3 + Pinia + Element Plus
│   ├── docs/                          # 前端接口需求文档
│   ├── package.json
│   └── AGENTS.md                      # 前端开发指南
│
├── DixyangFast/                       # 🐍 Python 后端 - RAG 课程作业
│   ├── my_books/                      # 25 本书籍 Markdown 数据源
│   ├── datasets/                      # 原始数据集
│   ├── storage/                       # 本地存储（向量库、聊天记录）
│   ├── pyproject.toml                 # 依赖配置（依赖 ../rag-shared）
│   └── README.md                      # Python 端专用文档
│
├── rag-shared/                        # 🔑 共享 RAG 核心库（Python 包）
│   ├── python/rag_shared/             # 核心代码
│   │   ├── config.py                  # 多硬件配置管理
│   │   ├── processor.py               # 数据处理流水线
│   │   └── __init__.py
│   ├── config/                        # YAML 配置文件
│   │   ├── rag_base.yaml              # 通用基础配置
│   │   ├── rag_r5_5600u.yaml          # CPU 配置 (R5 5600U)
│   │   └── rag_rtx_4060.yaml          # GPU 配置 (RTX 4060 Laptop)
│   ├── pyproject.toml                 # 共享库打包配置
│   └── README.md                      # 共享库文档
│
├── docs/                              # 📚 项目总体文档
│   ├── README.md                      # 文档索引
│   ├── 项目总体情况总结.md
│   ├── 前后端接口对照分析.md
│   └── 后端开发技术文档.md
│
├── storage/                           # 💾 共享存储（Git 忽略）
│   ├── rag/                           # RAG 向量库与元数据
│   │   ├── chroma_db/                 # Chroma 持久化（按硬件隔离）
│   │   ├── chunks/                    # 分块文本备份
│   │   ├── metadata.json              # 元数据汇总
│   │   └── file_states.json           # 增量更新状态
│   └── chat/                          # 聊天记录存储
│
├── uploads/                           # 文件上传存储
├── .env.example                       # 环境变量模板
├── .gitignore
└── README.md                          # 本文件
```

## 🚀 快速开始

### 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| JDK | 17+ | 推荐 Temurin/OpenJDK |
| Maven | 3.6+ | dixiyang-engine 使用 |
| Node.js | 18+ | dixiyang-vue 使用 |
| Python | 3.11+ | DixyangFast/rag-shared 使用 |
| uv | 最新 | Python 包管理器 |
| Docker | 推荐 | MySQL/Redis/Qdrant |

### 1. 配置环境变量

```bash
# 根目录下
cp .env.example .env
# 编辑 .env 填入: DB_USERNAME, DB_PASSWORD, DEEPSEEK_API_KEY 等
```

### 2. 启动基础设施（Docker）

```bash
# MySQL
docker run -d --name mysql-dixiyang \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0

# Redis (可选)
docker run -d --name redis-dixiyang -p 6379:6379 redis:7-alpine

# Qdrant 向量数据库 (可选，Java 后端用)
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 3. 启动 Java 后端 (dixiyang-engine)

```bash
cd dixiyang-engine

# IDEA: 设置 Project SDK = JDK 17，运行 DixiyangEngineApplication
# 命令行:
export JAVA_HOME=~/.sdkman/candidates/java/17.0.10-tem
./mvnw spring-boot:run
```

> 后端启动后: http://localhost:8084/api

### 4. 启动前端 (dixiyang-vue)

```bash
cd dixiyang-vue/Dixiyang-vue3
npm install
npm run dev
```

> 前端启动后: http://localhost:5173 (Vite 代理 `/api` → `localhost:8084`)

### 5. 构建 RAG 知识库 (DixyangFast + rag-shared)

```bash
cd DixyangFast

# 安装依赖（含共享库）
uv sync

# 自动检测硬件处理数据
uv run python -m rag_shared.processor --hardware auto

# 或指定配置
uv run python -m rag_shared.processor --hardware rtx_4060   # GPU
uv run python -m rag_shared.processor --hardware r5_5600u   # CPU
```

> 处理后的向量库存储在 `../storage/rag/chroma_db/`

## 🖥️ 多机器硬件适配 (RAG 核心特性)

本项目在 **两台开发机** 上运行，配置差异大，`rag-shared` 提供自动适配：

| 机器 | CPU/GPU | RAG 配置 | Embedding 模型 | 向量库路径 |
|------|---------|----------|----------------|------------|
| **当前机** | RTX 4060 Laptop (8GB VRAM) | `rag_rtx_4060.yaml` | `bge-m3` (FP16) | `storage/rag/chroma_db/vectordb_4060` |
| **另一台** | R5 5600U (集显/纯CPU) | `rag_r5_5600u.yaml` | `bge-small-zh-v1.5` (FP32) | `storage/rag/chroma_db/vectordb_r5` |

### 自动检测逻辑

```python
# rag_shared/config.py::detect_hardware()
if torch.cuda.is_available():
    if "4060" in gpu_name: return "rtx_4060"
    elif vram >= 6GB: return "rtx_4060"
    else: return "cpu_fallback"
elif "5600u" in cpu_info: return "r5_5600u"
else: return "cpu_fallback"
```

### 切换配置方式

```bash
# 1. 命令行（最高优先级）
uv run python -m rag_shared.processor --hardware rtx_4060

# 2. 环境变量（持久化，CI/CD 友好）
export RAG_HARDWARE=rtx_4060
export RAG_DEVICE=cuda
export RAG_EMBEDDING_MODEL=BAAI/bge-m3

# 3. 代码中指定
config = load_config("rtx_4060", config_dir=Path("../rag-shared/config"))
```

## 📊 核心功能模块

| 模块 | 状态 | 说明 |
|------|------|------|
| 用户认证授权 | ✅ | Spring Security + JWT |
| 小说管理 | ✅ | CRUD + 封面上传(MD5去重) |
| 角色管理 | ✅ | CRUD |
| 时间线管理 | ✅ | CRUD + 行内编辑 |
| 故事节点 | ✅ | CRUD |
| **RAG 智能创作助手** | ✅ | 向量检索 + LLM 生成 |
| 用户配置 | ⚠️ | 待完善 |

## 🔧 技术栈速览

### 后端 (dixiyang-engine)
- Spring Boot 3.4.2 + MyBatis Plus 3.5
- Spring Security + JWT + MySQL 8.0
- **Qdrant** 向量数据库 + Redis
- Spring AI + DeepSeek API
- **Python 子进程集成** `rag-shared` (RAG 离线处理)

### 前端 (dixiyang-vue)
- Vue 3.5 + Vite 7 + Pinia 3
- Vue Router 5 + Element Plus 2.13
- Axios + Tailwind CSS 4

### Python 生态 (DixyangFast + rag-shared)
- **uv** 包管理 + Python 3.11+
- FastAPI + Uvicorn (API 服务)
- **sentence-transformers** (bge-m3 / bge-small)
- **Chroma** 向量数据库 (本地持久化)
- **langchain-text-splitters** 语义切分
- 多硬件配置: CPU (R5 5600U) / GPU (RTX 4060)

## 📚 文档导航

| 文档 | 位置 | 说明 |
|------|------|------|
| 项目总体情况总结 | `docs/项目总体情况总结.md` | 项目全貌 |
| 前后端接口对照分析 | `docs/前后端接口对照分析.md` | 接口完成状态 |
| 后端开发指南 | `dixiyang-engine/AGENTS.md` | Java 后端必读 |
| 后端接口文档 | `dixiyang-engine/docs/后端接口文档.md` | API 详细说明 |
| 前端开发指南 | `dixiyang-vue/AGENTS.md` | Vue 前端必读 |
| 前端接口需求 | `dixiyang-vue/docs/前端接口需求文档.md` | 接口需求说明 |
| 后端技术文档 | `docs/后端开发技术文档.md` | 架构详解 |
| **RAG 理论基础** | `DixyangFast/03.RAG理论基础.md` | 课程作业理论 |
| **RAG 共享库文档** | `rag-shared/README.md` | 核心库使用指南 |
| **Python 端文档** | `DixyangFast/README.md` | 课程作业实操 |

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支: `git checkout -b feat/xxx`
3. 提交变更: `git commit -m 'feat: add xxx'`
4. 推送分支: `git push origin feat/xxx`
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**最后更新**: 2026-06-30  
**维护者**: lijiajia