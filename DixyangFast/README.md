# DixyangFast - Python 主后端 + RAG 服务

> 本目录包含 Dixiyang 的 **Python FastAPI 主后端（8084）** 和 **RAG/Embedding 服务（8085）**。
> 根目录的 Docker Compose 部署只使用主后端；RAG 因模型/向量库体积大，作为可选项单独启动。

## 一键部署（推荐）

在项目根目录执行：

```bash
./scripts/deploy-linux.sh
```

完整说明见 [`../docs/Linux部署指南.md`](../docs/Linux部署指南.md)。

## 主后端（8084）

```bash
cd DixyangFast
uv sync
REDIS_URL='redis://:123321@127.0.0.1:6379/0' \
  uv run python src/dixiyang/main.py
```

- 依赖声明：`pyproject.toml`（运行依赖已补全）
- 锁文件：`uv.lock`（已纳入版本管理）
- 启动时自动读根目录 `.env`、连接 MySQL、`create_all` 建表/补列
- 创建管理员：`uv run python -m dixiyang.seed_admin`
- 端口：`8084`

## RAG 服务（8085 + ChromaDB 8000）

RAG = 本地 Embedding（bge-m3）+ ChromaDB 向量库 + Reranker 精排。
不启动不影响登录、小说、角色、时间线、广场、便签等主功能。

```bash
cd DixyangFast

# 1) 下载 Embedding 模型到 models/bge-m3/（国内建议先设镜像）
export HF_ENDPOINT=https://hf-mirror.com
uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3').save('models/bge-m3')"

# 2) 构建向量库（首次，约 10-15 分钟）
uv run -m rag_shared.processor --hardware rtx_4060 --full

# 3) 一键启动 ChromaDB(8000) + RAG 服务(8085)
./start_rag.sh
```

验证：

```bash
curl http://localhost:8085/api/rag/health
```

> 模型与向量库都不在 Git 仓库中，需要从旧电脑复制或重新构建，详见
> [`../docs/Linux迁移指南.md`](../docs/Linux迁移指南.md) 和 [`../docs/RAG离线构建流程.md`](../docs/RAG离线构建流程.md)。

## 目录结构

```
DixyangFast/
├── src/dixiyang/             # ★ 主后端（8084）
│   ├── main.py               # FastAPI 入口
│   ├── routers/              # auth/novel/chat/rag/idea/sticky/admin...
│   ├── services/             # 业务逻辑
│   └── seed_admin.py         # 幂等创建管理员
├── python_api/main.py        # RAG 服务（8085）
├── start_rag.sh / .ps1       # RAG 一键启动
├── pyproject.toml / uv.lock  # 主后端依赖
├── models/bge-m3/            # Embedding 模型（不入库）
└── storage/vectordb_4060/    # ChromaDB 向量库（不入库）
```

## 常用命令

```bash
uv sync                       # 安装/同步依赖
uv run python -m dixiyang.seed_admin
uv run python -m dixiyang.seed_admin --reset-password
```
