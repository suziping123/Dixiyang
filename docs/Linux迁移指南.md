# Dixiyang RAG 数据迁移指南（Windows → Linux）

> **说明（2026-10-19 更新）**：本文只负责 **RAG 模型 / 向量库的跨机迁移**。
> 完整站点部署请看 **[`Linux部署指南.md`](./Linux部署指南.md)**（Docker 一键，推荐）。
> 旧版 Java 双后端启动方式已废弃：当前主后端是 Python FastAPI（8084）。

## 需要复制到 U 盘 / 移动硬盘的内容

| 路径 | 大小 | 说明 |
|------|------|------|
| `DixyangFast/storage/vectordb_4060/` | 约 1.7 GB | **向量数据库**（ChromaDB 持久化数据） |
| `DixyangFast/models/bge-m3/` | 约 2.2 GB | **Embedding 模型**（两台机器必须一致） |
| `DixyangFast/my_books/` | 约 133 MB | 27 本书 Markdown（构建向量库用，可选） |
| `uploads/` | 视数据量 | 用户上传/聊天 JSON（如也要迁移业务数据） |

> 源码建议在新电脑直接 `git clone`，只手动复制上面这些「不在 Git 里」的大文件。

## 1. 复制文件到 Linux

```bash
mkdir -p ~/Dixiyang/DixyangFast/{storage,models}
cp -r /media/$USER/U盘/vectordb_4060 ~/Dixiyang/DixyangFast/storage/
cp -r /media/$USER/U盘/bge-m3        ~/Dixiyang/DixyangFast/models/
```

确认目录结构：

```text
DixyangFast/
├── models/bge-m3/            # config.json / model.safetensors / tokenizer...
└── storage/vectordb_4060/    # chroma.sqlite3 等
```

## 2. 安装 RAG 依赖

RAG 服务依赖 `torch + sentence-transformers + chromadb`，这些**不在主后端依赖里**（体积大）。
先按 `Linux部署指南.md` §12 安装 uv，然后在 `DixyangFast/` 下：

```bash
cd ~/Dixiyang/DixyangFast

# 主后端依赖（含 chromadb，用于连接向量库）
uv sync

# RAG 额外依赖（CPU 版示例；有 NVIDIA GPU 时按官网替换 torch 源）
uv pip install -r requirements-rag.txt
uv pip install "torch>=2.0.0" --index-url https://download.pytorch.org/whl/cpu
```

> 国内网络慢时给 pip/uv 加镜像：`UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`。

## 3. 启动 RAG 服务（8085 + ChromaDB 8000）

```bash
cd ~/Dixiyang/DixyangFast
chmod +x start_rag.sh
./start_rag.sh
```

脚本会：

1. 检查 `storage/vectordb_4060/` 是否存在；
2. 启动 ChromaDB Server（8000）；
3. 启动 Embedding Service（8085）；
4. 自动做 CPU 线程优化。

验证：

```bash
curl http://localhost:8085/api/rag/health
curl http://localhost:8085/api/rag/stats
```

Web 可视化：`http://localhost:8085/rag`

停止：

```bash
pkill -f 'chroma run'; pkill -f 'python_api/main.py'
```

## 4. 主站如何连上 RAG

Docker 部署的主后端默认不启用 RAG。需要时有两种做法：

- **方式 A（简单）**：RAG 用上面的原生方式跑在宿主机 8085。Docker Compose 已给后端加 `extra_hosts: host.docker.internal:host-gateway`，默认通过 `http://host.docker.internal:8085` 访问；如需修改，在 `.env` 设置 `RAG_SERVICE_URL` / `RERANKER_URL` 后 `docker compose up -d backend`。
- **方式 B（完整原生）**：前后端都用原生模式跑（见 §12），RAG 直接 `localhost` 访问，无需改网络。

## 5. 重建向量库（可选）

不想搬 1.7 GB 向量库时，可以带 `my_books/` 到新机器重建：

```bash
cd ~/Dixiyang/DixyangFast
export HF_ENDPOINT=https://hf-mirror.com
uv run -m rag_shared.processor --hardware rtx_4060 --full   # 有 GPU
# 或按 rag-shared/config/rag_r5_5600u.yaml 选择其他硬件档
```

耗时约 10–15 分钟（GPU）到 1 小时以上（CPU）。详见 [`RAG离线构建流程.md`](./RAG离线构建流程.md)。

## 6. 常见问题

### ChromaDB 连接失败

- Linux 用 `localhost`；Windows 旧版 Java 后端曾要求 `[::1]`（已废弃）。
- 确认 `storage/vectordb_4060/` 是完整目录（含 `chroma.sqlite3`），而不是空文件夹。

### 模型加载失败 / 维度不一致

两台机器必须使用同一个 `bge-m3`（1024 维）。不要混用其他 embedding 模型。

### 内存不足

Embedding 服务加载模型约占 2–4 GB 内存；CPU 推理较慢，建议至少 8 GB 内存。

### 主站 AI 聊天不需要 RAG 吗？

不需要。AI 聊天走 DeepSeek API；RAG 只用于「知识库检索增强」，不启动不影响主功能。

---

**最后更新**: 2026-10-19
