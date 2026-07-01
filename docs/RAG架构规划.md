# Dixiyang RAG 架构规划

## 一、当前架构

```
┌──────────────────────────────────────────────────┐
│                dixiyang-vue (Vue 3)               │
│            端口 5173 (Vite dev server)            │
│         代理 /api → localhost:8084                │
└──────────────┬───────────────────────────────────┘
               │ /api/*
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────────┐   ┌──────────────────┐
│  Java 后端   │   │  Python 后端      │
│ Spring Boot │   │  FastAPI          │
│ 端口 8084   │   │  端口 8084       │
│ Qdrant向量库 │   │  ChromaDB向量库   │
└─────────────┘   └──────────────────┘
```

### 问题
1. Java 和 Python 用**不同的向量库**（Qdrant vs ChromaDB），数据不互通
2. 前端**没有** RAG 向量库可视化页面
3. Linux 迁移需要统一向量库方案

---

## 二、统一向量库方案

### 决策：统一使用 ChromaDB

| 对比 | Qdrant | ChromaDB |
|------|--------|----------|
| 部署方式 | Docker 容器 | Python 包，本地持久化 |
| 数据格式 | 自有格式 | SQLite + Parquet |
| 跨语言支持 | REST API (Go/Java/Python) | Python only |
| 与 rag-shared 兼容 | ❌ 需要适配 | ✅ 直接对接 |
| Linux 迁移 | 需导出/导入 | 文件夹直接复制 |

**选择 ChromaDB** 的原因：
- rag-shared processor 已经构建了 ChromaDB 数据（70458 chunks）
- 不需要重新跑 embedding 流水线
- Java 端通过 `chromadb-client` HTTP API 访问

### 架构目标

```
┌──────────────────────────────────────────────────┐
│                dixiyang-vue (Vue 3)               │
│         /api/rag/* → 向量库可视化                  │
└──────────────┬───────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────────┐   ┌──────────────────┐
│  Java 后端   │   │  Python 后端      │
│ Spring Boot │   │  FastAPI          │
│ 端口 8084   │   │  端口 8085       │
└──────┬──────┘   └───────┬──────────┘
       │                  │
       └────────┬─────────┘
                ▼
       ┌────────────────┐
       │    ChromaDB     │
       │  (共享向量库)    │
       │  端口 8000      │
       └────────────────┘
```

---

## 三、RAG 向量库可视化 API 设计

### 3.1 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/rag/stats` | 向量库统计信息 |
| GET | `/api/rag/collections` | 所有集合列表 |
| GET | `/api/rag/documents?collection=xxx&page=1&size=20` | 文档分块列表（分页） |
| POST | `/api/rag/search` | 语义检索测试 |
| GET | `/api/rag/document/{id}` | 单个分块详情 |

### 3.2 响应格式

```json
// GET /api/rag/stats
{
  "code": 200,
  "data": {
    "total_collections": 1,
    "total_documents": 70458,
    "embedding_model": "BAAI/bge-m3",
    "embedding_dimension": 1024,
    "collection_details": [
      {
        "name": "dixiyang_knowledge",
        "count": 70458,
        "metadata": {"hnsw:space": "cosine"}
      }
    ]
  }
}

// POST /api/rag/search
{
  "code": 200,
  "data": {
    "query": "修仙功法",
    "results": [
      {
        "id": "chunk_001",
        "content": "天元功法乃上古...",
        "score": 0.892,
        "metadata": {"source": "摩诃婆罗多", "chapter": "第一卷"}
      }
    ]
  }
}
```

---

## 四、Linux 迁移方案

### 4.1 向量库数据迁移

ChromaDB 数据位于 `storage/vectordb_4060/`，包含：
- `chroma.sqlite3` — 元数据（SQLite）
- `*/` — 各集合的数据目录（Parquet 文件）

**打包命令**（Windows）：
```powershell
# 打包整个向量库目录
tar -czf vectordb_4060.tar.gz -C storage/ vectordb_4060/

# 打包 embedding 模型（约 2.3GB）
tar -czf bge-m3.tar.gz -C models/ bge-m3/
```

**Linux 恢复**：
```bash
mkdir -p /app/storage
tar -xzf vectordb_4060.tar.gz -C /app/storage/
tar -xzf bge-m3.tar.gz -C /app/models/
```

### 4.2 Python 依赖导出

```powershell
# 在 Windows 上
.venv\Scripts\pip freeze > requirements.txt

# 在 Linux 上
pip install -r requirements.txt
```

核心依赖：
```
sentence-transformers>=3.0.0
chromadb>=0.5.0
langchain-text-splitters
torch>=2.4.0  # CUDA 版本根据 Linux GPU 情况选择
```

### 4.3 Java 依赖

Java 端需要通过 HTTP API 访问 ChromaDB，无需额外依赖。Spring Boot 应用本身通过 `RestTemplate` 或 `WebClient` 调用 ChromaDB REST API。

### 4.4 Docker Compose 参考

```yaml
version: '3.8'
services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - ./storage/vectordb_4060:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=False

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: dixiyang

  # Java 或 Python 后端
  backend:
    build: .
    ports:
      - "8084:8084"
    depends_on:
      - chromadb
      - mysql
```

---

## 五、实施步骤

### Phase 1: 向量库统一（优先级高）
1. [ ] Java 端移除 Qdrant 依赖，改用 ChromaDB REST API
2. [ ] Python 端保持 ChromaDB 本地持久化
3. [ ] 配置文件统一 ChromaDB 连接参数

### Phase 2: RAG 可视化 API（优先级高）
1. [ ] Java 端：新建 `RagController.java`
   - `GET /api/rag/stats` — 查询 ChromaDB 集合统计
   - `GET /api/rag/documents` — 查询分块列表
   - `POST /api/rag/search` — 语义检索
2. [ ] Python 端：新建 `routers/rag.py` + `services/rag_service.py`
   - 同样的 API 接口
3. [ ] 前端：新建 `views/RagKnowledgeView.vue`

### Phase 3: Linux 迁移（优先级中）
1. [ ] 编写迁移脚本（打包向量库 + 模型 + 代码）
2. [ ] 编写 `docker-compose.yml`
3. [ ] 编写部署文档 `DEPLOY.md`

### Phase 4: Go 后端（如果需要）
1. [ ] Go 通过 HTTP API 访问 ChromaDB
2. [ ] 实现相同的 RAG API 接口
3. [ ] Go 的 ChromaDB 客户端库：`github.com/amikos/chroma-go`

---

## 六、待确认事项

1. Linux 上主要运行 Java 还是 Python 后端？
2. 是否需要 Go 后端？
3. ChromaDB 是独立 Docker 服务还是嵌入式（Python 直接读取）？
4. 前端可视化需要哪些图表（分布图、热力图、散点图）？
