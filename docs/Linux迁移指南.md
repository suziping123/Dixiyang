# Dixiyang Linux 迁移指南

## 需要复制到 U 盘的内容

在 Windows 上复制以下内容到 U 盘（共约 **4.5 GB**）：

| 路径 | 大小 | 说明 |
|------|------|------|
| `DixyangFast/storage/vectordb_4060/` | 1.7 GB | **向量数据库**（ChromaDB 数据，111509 条嵌入） |
| `DixyangFast/models/bge-m3/` | 2.2 GB | **嵌入模型**（bge-m3，与训练时一致） |
| 整个项目文件夹 `Dixiyang/` | ~0.5 GB | **源码**（Java + Python + Vue 前端），剔除 `.venv/` `node_modules/` |

> 向量库和模型体积大且不在 git 中，必须手动复制。源码部分建议在 Linux 上 `git clone` 后只手动复制向量库和模型。

## Linux 部署步骤

### 1. 复制文件到 Linux

```bash
mkdir -p /app/Dixiyang
# 从 U 盘复制
cp -r /mnt/usb/vectordb_4060 /app/Dixiyang/DixyangFast/storage/
cp -r /mnt/usb/bge-m3 /app/Dixiyang/DixyangFast/models/
# 如果源码也在 U 盘上则复制源码
cp -r /mnt/usb/Dixiyang /app/
```

### 2. 安装依赖

**Python 环境：**
```bash
cd /app/Dixiyang/DixyangFast
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# 安装核心依赖
pip install sentence-transformers chromadb langchain-text-splitters fastapi uvicorn
# PyTorch（根据 Linux GPU 选版本）
pip install torch --index-url https://download.pytorch.org/whl/cu124  # 有 GPU
# 或
pip install torch --index-url https://download.pytorch.org/whl/cpu   # 无 GPU
```

**Java 环境：**
```bash
# 安装 Java 17
sudo apt install openjdk-17-jdk maven
```

**前端环境：**
```bash
cd /app/Dixiyang/dixiyang-vue/Dixiyang-vue3
npm install
```

### 3. 启动顺序

```bash
# 终端 1: ChromaDB Server
cd /app/Dixiyang/DixyangFast
source .venv/bin/activate
chroma run --path storage/vectordb_4060 --port 8000

# 终端 2: Python 后端（提供 embedding 服务，端口 8085）
cd /app/Dixiyang/DixyangFast
source .venv/bin/activate
RAG_EMBEDDING_MODEL=models/bge-m3 RAG_DEVICE=cuda uvicorn dixiyang.main:app --host 0.0.0.0 --port 8085

# 终端 3: Java 后端（端口 8084，context-path /api）
cd /app/Dixiyang/dixiyang-engine
# 设置环境变量
export DB_PASSWORD=你的MySQL密码
export DEEPSEEK_API_KEY=你的DeepSeekKey
export CHROMADB_HOST=localhost  # Linux 上 ChromaDB 监听 0.0.0.0，用 localhost 即可
mvn spring-boot:run

# 终端 4: 前端（端口 5173）
cd /app/Dixiyang/dixiyang-vue/Dixiyang-vue3
npm run dev
```

### 4. 验证

```bash
# RAG 统计
curl http://localhost:8084/api/rag/stats
# 期望：connected: true, total_documents: 111509

# 文档列表
curl "http://localhost:8084/api/rag/documents?page=1&pageSize=3"
```

## Linux 与 Windows 差异

| 项目 | Windows | Linux |
|------|---------|-------|
| ChromaDB host | `[::1]`（仅 IPv6） | `localhost`（IPv4+IPv6） |
| Python 端口 | 8085 | 8085 |
| Java 端口 | 8084 (context-path `/api`) | 8084 (context-path `/api`) |
| 模型路径 | `.\models\bge-m3` | `models/bge-m3` |
| 向量库路径 | `storage/vectordb_4060` | `storage/vectordb_4060` |
| CUDA | RTX 4060 | 视 Linux 机器而定 |

> **无需重新跑 embedding 流水线**：ChromaDB 数据直接文件夹复制即可使用，不分系统。

## 常见问题

- **ChromaDB host 设置**：Windows 上 Java 连接需用 `[::1]`，Linux 上用 `localhost`。通过环境变量 `CHROMADB_HOST=localhost` 控制。
- **MySQL 密码**：通过 `DB_PASSWORD` 环境变量传入，默认 `123321`。
- **Python embedding 服务**：Java 搜索功能依赖 Python 端 `/api/rag/embed`，必须先启动 Python。
