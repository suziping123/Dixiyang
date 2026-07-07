# RAG 向量化与检索完整流程

> 本文档完整说明：MD 文档如何被向量化存入数据库，以及 Java 后端如何调用这些向量做 RAG 检索。

---

## 一、整体流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    离线构建（一次性/增量）                      │
│                                                             │
│  my_books/*.md (27本书)                                      │
│       │                                                     │
│       ▼                                                     │
│  MarkdownLoader  ── 按 # ## 标题切分 + RecursiveCharacter    │
│                     TextSplitter 进一步切分为 chunks         │
│       │                                                     │
│       ▼                                                     │
│  EmbeddingModel  ── SentenceTransformer("bge-m3")           │
│                     批量编码 → 1024维归一化向量               │
│       │                                                     │
│       ▼                                                     │
│  VectorDB (ChromaDB)  ── collection.add(id, content,        │
│                                          embedding, metadata)│
│       │                                                     │
│       ▼                                                     │
│  FileStateTracker  ── 记录 MD5 hash，下次仅处理变更文件      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    在线检索（每次用户提问）                    │
│                                                             │
│  用户: "帮我分析三体中的面壁计划"                              │
│       │                                                     │
│       ▼                                                     │
│  ChatController.buildFullPrompt()                            │
│       │                                                     │
│       ├── buildContextFromDatabase()  ── 查 MySQL 拿角色/节点│
│       │                                                     │
│       └── RagService.search(query, topK=5)                   │
│               │                                             │
│               ├── POST localhost:8085/api/rag/embed          │
│               │   (Python SentenceTransformer 向量化 query)  │
│               │                                             │
│               └── POST localhost:8000/.../collections/       │
│                       {id}/query (ChromaDB cosine 检索)      │
│       │                                                     │
│       ▼                                                     │
│  拼装 Prompt: 【参考资料】+ DB上下文 + 用户需求               │
│       │                                                     │
│       ▼                                                     │
│  chatClient.prompt(fullPrompt).stream().content()            │
│  (DeepSeek → SSE 逐 token 返回前端)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、离线构建：MD 文档 → 向量库

### 2.1 运行命令

```bash
cd DixyangFast

# Windows RTX 4060（GPU 构建）
python -m rag_shared.processor --hardware rtx_4060 --full

# Linux R5 5600U（CPU 构建）
python -m rag_shared.processor --hardware r5_5600u --full
```

### 2.2 入口代码

**文件**: `rag-shared/python/rag_shared/processor.py`

```
main()
  → load_config("rtx_4060")        # 加载 YAML 配置
  → RAGProcessor(config)            # 初始化处理器
  → processor.run(incremental=False) # 执行处理
```

### 2.3 单文件处理流程

`RAGProcessor.process_file()` (第554行)：

```
process_file(file_path)
  │
  ├── 1. MarkdownLoader.load(file_path)
  │      │
  │      ├── 读取 MD 全文
  │      ├── 解析文件名 → 书名 + 作者
  │      │   例: "三体 (刘慈欣).md" → 书名="三体", 作者="刘慈欣"
  │      ├── 查 book_categories → 分类
  │      │   例: "三体" → "科幻小说"
  │      ├── _split_by_headers(text)  ── 按 # ## 标题切分
  │      │   例: "# 三体 第一部\n## 汪淼\n内容..."
  │      │   → [{h1:"三体第一部", h2:"汪淼", content:"内容..."}, ...]
  │      └── _split_text(content)  ── 按 chunk_size 进一步切分
  │          RecursiveCharacterTextSplitter(
  │            chunk_size=600,       # 每个chunk最大600字
  │            chunk_overlap=120,    # 相邻chunk重叠120字
  │            separators=["\n\n", "\n", "。", "！", "？", ...]
  │          )
  │          → ["三体问题是一个天体力学中的经典问题...", "..."]
  │
  ├── 2. EmbeddingModel.encode(texts)
  │      SentenceTransformer("BAAI/bge-m3").encode(
  │        texts,
  │        batch_size=64,
  │        normalize_embeddings=True   # 归一化，用于 cosine 相似度
  │      )
  │      → [[0.023, -0.156, ...], ...]  # 1024维向量列表
  │
  ├── 3. VectorDB.add(chunks, embeddings)
  │      ChromaDB collection.add(
  │        ids=["三体_0", "三体_1", ...],
  │        documents=["三体问题是一个天体力学...", ...],
  │        embeddings=[[0.023, ...], ...],
  │        metadatas=[{source:"book", book_title:"三体",
  │                    author:"刘慈欣", category:"科幻小说",
  │                    chapter:"第一部", section:"汪淼"}, ...]
  │      )
  │      → 持久化到 storage/vectordb_4060/chroma.sqlite3
  │
  └── 4. FileStateTracker.update(file_path, chunks_count)
         记录: {mtime, MD5_hash, chunks_count, updated_at}
         → 下次运行时跳过未修改文件
```

### 2.4 Metadata 字段说明

每个 chunk 存入 ChromaDB 时携带以下 metadata：

| 字段 | 类型 | 示例 | 说明 |
|------|------|------|------|
| `source` | string | `"book"` | 数据来源：book/qa/law/cars/company |
| `book_title` | string | `"三体全集（共3册）"` | 书名 |
| `author` | string | `"刘慈欣"` | 作者 |
| `category` | string | `"科幻小说"` | 分类（来自 rag_base.yaml） |
| `chapter` | string | `"第一部"` | 章节标题 |
| `section` | string | `"汪淼"` | 小节标题 |
| `file_path` | string | `"my_books/三体.md"` | 原始文件路径 |
| `chunk_id` | int | `0` | chunk 序号 |

### 2.5 向量库存储位置

```
storage/vectordb_4060/
├── chroma.sqlite3          # 元数据（SQLite）
└── dixiyang_knowledge/     # 集合数据目录
    └── *.parquet           # 向量数据文件
```

### 2.6 配置文件

**文件**: `rag-shared/config/rag_rtx_4060.yaml`（Windows GPU 配置）

```yaml
embedding:
  model: "BAAI/bge-m3"
  device: "cuda"
  half_precision: true       # FP16 加速
  batch_size: 64

text_splitter:
  chunk_size: 600
  chunk_overlap: 120

vectordb:
  path: "./storage/vectordb_4060"
  collection_name: "dixiyang_knowledge"
  distance_metric: "cosine"  # 余弦相似度
```

---

## 三、在线检索：用户提问 → RAG 增强

### 3.1 Java 后端调用链

**文件**: `dixiyang-engine/.../Controller/ChatController.java`

```
用户发送 ChatRequest { message, novelId, useRag, sessionId, ... }
    │
    ▼
buildFullPrompt(request)          # 第221行
    │
    ├── buildContextFromDatabase()
    │   → 查 MySQL: NovelCharacter 表 → 角色信息
    │   → 查 MySQL: StoryNode 表 → 故事节点
    │   → 拼成 "【角色信息】..." 字符串
    │
    ├── if (useRag):
    │   ragService.search(finalMessage, 5)     # 第167行
    │       │
    │       ├── Step 1: getEmbedding(query)    # 第64行
    │       │   POST http://localhost:8085/api/rag/embed
    │       │   Body: {"text": "帮我分析三体中的面壁计划"}
    │       │   Response: {"embedding": [0.023, -0.156, ...]}
    │       │   → 返回 1024 维 float 数组
    │       │
    │       ├── Step 2: 构造 ChromaDB 查询
    │       │   POST http://localhost:8000/api/v2/tenants/
    │       │         default_tenant/databases/default_database/
    │       │         collections/{col_id}/query
    │       │   Body: {
    │       │     "query_embeddings": [[0.023, -0.156, ...]],
    │       │     "n_results": 5,
    │       │     "include": ["documents", "metadatas", "distances"]
    │       │   }
    │       │
    │       └── Step 3: 解析结果
    │           score = 1.0 - distance    # 余弦距离转相似度
    │           → [{content, metadata, score}, ...]
    │
    ├── 注入 edits 上下文（编辑修正记录）
    │
    └── 组装最终 Prompt
```

### 3.2 最终注入到 AI 的 Prompt 格式

```
【参考资料】
[三体] 宇宙社会学的基本公理是：生存是文明的第一需要...
---
[三体] 黑暗森林法则的核心在于猜疑链和技术爆炸...
---
[三体] 面壁计划是联合地球防御计划的重要组成部分...

【角色信息】
- 张三（男，25岁）:
  * 外貌：...
  * 性格：...

用户需求：帮我分析三体中的面壁计划

请基于以上信息回答用户的问题。如果参考资料与问题相关，请重点参考；如不相关，可忽略。
```

### 3.3 流式输出

**文件**: `ChatController.java` 第122行

```java
@PostMapping("/chat/stream")
public SseEmitter chatStream(@RequestBody ChatRequest request) {
    String fullPrompt = buildFullPrompt(request);
    Flux<String> flux = chatClient.prompt(fullPrompt)
                        .stream()
                        .content();
    // Flux 逐 token 推 SSE
    // 实时检测 <thinking>/</thinking> 标签
    // 拆分为 type="thinking" 和 type="content" 两种 SSE 事件
    // 前端根据 type 分别渲染
}
```

---

## 四、Python Embedding 服务（端口 8085）

### 4.1 核心端点

**文件**: `DixyangFast/python_api/main.py`

| 方法 | 路径 | 说明 | 调用方 |
|------|------|------|--------|
| POST | `/api/rag/embed` | 单条文本向量化 | Java RagService |
| POST | `/api/rag/embed/batch` | 批量向量化 | — |
| GET | `/api/rag/stats` | 向量库统计 | Web UI |
| POST | `/api/rag/search` | 检索测试 | Web UI |
| GET | `/api/rag/documents` | 分页浏览文档 | Web UI |
| GET | `/rag` | RAG Web 可视化页面 | 浏览器 |

### 4.2 Embed API 实现

```python
MODEL_NAME = "BAAI/bge-m3"

@asynccontextmanager
async def lifespan(app):
    local_model_path = str(Path(__file__).parent.parent / "models" / "bge-m3")
    _model = SentenceTransformer(local_model_path, cache_folder=cache_dir)
    # 模型维度: 1024

@app.post("/api/rag/embed")
async def embed(req: EmbedRequest):
    """单条文本向量化 → Java RagService 调用"""
    emb = _model.encode([req.text], normalize_embeddings=True)
    return {"embedding": emb[0].tolist()}
```

### 4.3 RAG Web 可视化页面

浏览器访问 `http://localhost:8085/rag` 可以看到：

- **统计面板**: 总文档数、来源分布（book/qa/law/cars）、分类分布
- **搜索测试**: 输入 query，展示 Top-K 结果 + 相似度分数 + 来源
- **文档浏览**: 按 source 筛选，分页查看所有 chunks

---

## 五、ChromaDB 向量数据库

### 5.1 启动方式

```bash
cd DixyangFast

# 一键启动
./start_rag.sh

# 或手动
chroma run --path storage/vectordb_4060 --port 8000
```

### 5.2 HTTP API

ChromaDB 1.5.9 提供 REST API：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v2/heartbeat` | 健康检查 |
| GET | `/api/v2/tenants/default_tenant/databases/default_database/collections` | 列出所有集合 |
| GET | `.../collections/{id}/count` | 获取集合文档数 |
| POST | `.../collections/{id}/query` | 向量检索（传入 query_embeddings） |
| POST | `.../collections/{id}/get` | 获取文档列表（分页） |

### 5.3 检索原理

ChromaDB 使用 HNSW (Hierarchical Navigable Small World) 索引：

```
query: "三体中的面壁计划"
    ↓ bge-m3 编码
query_embedding: [0.023, -0.156, ...]  (1024维)
    ↓ ChromaDB cosine 最近邻搜索
top_k=5 → 找到最相似的 5 个 chunks
    ↓ 返回
[{content, metadata, distance}, ...]
score = 1.0 - distance  (余弦距离转相似度)
```

---

## 六、端口速查

| 服务 | 端口 | 用途 |
|------|------|------|
| MySQL | 3306 | 关系数据库（用户/小说/聊天记录） |
| Java 后端 | 8084 | Spring Boot（context-path: `/api`） |
| Vue 前端 | 5173 | Vite dev server（代理 `/api` → 8084） |
| Python Embedding | 8085 | FastAPI + RAG Web UI |
| ChromaDB | 8000 | 向量数据库 HTTP API |

### 调用关系

```
浏览器 → Vue(5173) → Java(8084) → MySQL(3306)
                           ↓
                      ChromaDB(8000) ←── Python(8085) 提供 Embedding
```

---

## 七、完整代码位置索引

| 功能 | 文件 | 行号 |
|------|------|------|
| MD 加载切分 | `rag-shared/python/rag_shared/processor.py` | 107 (MarkdownLoader) |
| Embedding 编码 | `rag-shared/python/rag_shared/processor.py` | 392 (EmbeddingModel) |
| ChromaDB 存储 | `rag-shared/python/rag_shared/processor.py` | 449 (VectorDB) |
| 增量更新追踪 | `rag-shared/python/rag_shared/processor.py` | 44 (FileStateTracker) |
| 配置加载 | `rag-shared/python/rag_shared/config.py` | — (load_config) |
| Python Embed API | `DixyangFast/python_api/main.py` | 72 (embed) |
| Python 搜索 API | `DixyangFast/python_api/main.py` | 188 (rag_search) |
| Python 统计 API | `DixyangFast/python_api/main.py` | 128 (rag_stats) |
| Java RAG 检索 | `dixiyang-engine/.../Service/RagService.java` | 167 (search) |
| Java Embed 调用 | `dixiyang-engine/.../Service/RagService.java` | 64 (getEmbedding) |
| Java Prompt 构建 | `dixiyang-engine/.../Controller/ChatController.java` | 221 (buildFullPrompt) |
| Java 流式输出 | `dixiyang-engine/.../Controller/ChatController.java` | 122 (chatStream) |
