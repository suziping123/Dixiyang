# DixyangFast - Python RAG 后端

> RAG 课程作业 + 向量库管理，依赖 Monorepo 共享库 `rag-shared`。

## 功能说明

| 功能 | 端口 | 说明 |
|------|------|------|
| Embedding 服务 | 8085 | `POST /api/rag/embed` 将文本转为 bge-m3 向量 |
| RAG Web 可视化 | 8085 | `GET /rag` 浏览向量库统计/搜索/文档 |
| ChromaDB 向量库 | 8000 | 存储文档向量，HTTP API |
| 向量库构建 | — | Windows RTX 4060 上运行，离线构建 |

## 一键启动

```bash
cd ~/项目/Dixiyang/DixyangFast
./start_rag.sh
```

启动后:
- **RAG Web 可视化**: http://localhost:8085/rag
- Embedding API: http://localhost:8085/api/rag/embed
- ChromaDB: http://localhost:8000

## 手动启动

```bash
# 终端1: ChromaDB
chroma run --path storage/vectordb_4060 --port 8000

# 终端2: Embedding 服务
cd ~/项目/Dixiyang/DixyangFast
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python python_api/main.py
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rag/embed` | 文本向量化 `{"text": "..."}` → `{"embedding": [...]}` |
| POST | `/api/rag/search` | 检索测试 `{"query": "...", "top_k": 5}` |
| GET | `/api/rag/stats` | 向量库统计（总数、来源分布、分类分布） |
| GET | `/api/rag/documents` | 文档浏览 `?page=1&page_size=20&source=book` |
| GET | `/rag` | Web 可视化页面 |

## Windows 构建向量库

两台机器必须用同一个 Embedding 模型（`bge-m3`，1024 维）。

```powershell
# Windows 上
cd Dixiyang\DixyangFast
.\.venv\Scripts\activate
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 首次全量构建（约 10-15 分钟）
python -m rag_shared.processor --hardware rtx_4060 --full

# 传输到 Linux
tar -czf vectordb_4060.tar.gz -C storage vectordb_4060
scp vectordb_4060.tar.gz 用户名@192.168.1.x:~/项目/Dixiyang/DixyangFast/storage/
```

## 数据文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `my_books/*.md` | 133MB | 27 本书 Markdown（不进 git，需 Windows 传输） |
| `datasets/datasets/*` | 676KB | 4 个数据集（法律、二手车、QA、公司） |
| `storage/vectordb_4060/` | ~14MB+ | 构建产物（不进 git） |

## 项目结构

```
DixyangFast/
├── python_api/main.py        # FastAPI 服务（端口 8085）
├── start_rag.sh              # 一键启动脚本
├── my_books/                 # 27 本书 Markdown（不进 git）
├── datasets/datasets/        # 4 个数据集
├── storage/vectordb_4060/    # ChromaDB 向量库
├── models/bge-m3/            # 本地 Embedding 模型
├── .venv/                    # Python 虚拟环境
└── README.md                 # 本文件
```
