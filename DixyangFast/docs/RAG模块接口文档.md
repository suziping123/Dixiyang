# RAG 模块接口文档

## 一、架构总览

```
dixiyang-vue (Vue 3)
  │  /api/rag/stats     (GET)
  │  /api/rag/count     (GET)
  │  /api/rag/documents (GET)
  │  /api/rag/search    (POST)
  │  /api/chat/stream   (POST, 含 knowledge_search 工具)
  │
  ├──> dixiyang-engine (Java, Spring Boot, 8084)
  │      RagController.java → RagService.java
  │        ├── GET  /rag/stats      → ChromaDB REST API (8000)
  │        ├── GET  /rag/count      → ChromaDB REST API
  │        ├── GET  /rag/documents  → ChromaDB REST API
  │        ├── POST /rag/search     → Python embed (8085) → ChromaDB
  │        └── ChatController.java (ragEnabled 控制工具注入)
  │
  └──> DixyangFast (Python, FastAPI, 8085)
         routers/rag.py
           ├── GET  /rag/stats      → langchain_chroma.Chroma
           ├── GET  /rag/count      → langchain_chroma.Chroma
           ├── GET  /rag/documents  → langchain_chroma.Chroma
           ├── POST /rag/search     → langchain_chroma.Chroma
           └── POST /rag/embed      → DixiyangEmbeddings

         routers/chat.py
           └── POST /chat/stream    → is_rag_enabled() 控制 knowledge_search 工具
```

---

## 二、Python FastAPI 端点

### 2.1 `GET /rag/stats`

获取向量库统计信息。

**请求**:
```
GET /rag/stats
Authorization: Bearer <token>
```

**响应** (`Result.success` 包裹):
```json
{
  "code": 200,
  "msg": "success",
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
    ],
    "connected": true
  }
}
```

**错误时**:
```json
{"code": 500, "msg": "获取统计失败: ...", "data": null}
```

**实现**: `routers/rag.py:32` — 使用 `vectorstore._collection.count()`。

---

### 2.2 `GET /rag/count`

仅返回文档总数。

**请求**:
```
GET /rag/count
Authorization: Bearer <token>
```

**响应**:
```json
{"code": 200, "msg": "success", "data": 70458}
```

**实现**: `routers/rag.py:55` — 同 `_collection.count()`。

---

### 2.3 `GET /rag/documents`

分页浏览文档。

**请求**:
```
GET /rag/documents?page=1&pageSize=20
Authorization: Bearer <token>
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码，≥1 |
| `pageSize` | int | 20 | 每页条数，1-100 |

**响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "ids": ["三体_0", "三体_1", ...],
    "documents": ["三体问题是一个天体力学...", ...],
    "metadatas": [{"source": "book", "book_title": "三体"}, ...],
    "page": 1,
    "page_size": 20
  }
}
```

**实现**: `routers/rag.py:64` — `vectorstore.get(limit, offset, include=...)`。

---

### 2.4 `POST /rag/search`

向量语义搜索。**注意：前端使用 query params 传参，非 JSON body**（对齐 Spring 做法）。

**请求**:
```
POST /rag/search?query=面壁计划&topK=5
Content-Type: application/json
Authorization: Bearer <token>
```
（POST 请求体为空）

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | (必填) | 搜索关键词 |
| `topK` | int | 5 | 返回条数，1-50 |

**响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "query": "面壁计划",
    "results": [
      {
        "id": "三体_42",
        "content": "面壁计划是联合地球防御计划...",
        "metadata": {"source": "book", "book_title": "三体"},
        "score": 0.892
      }
    ]
  }
}
```

**实现**: `routers/rag.py:82` — `vectorstore.similarity_search_with_score()`。

---

### 2.5 `POST /rag/embed`

单条文本向量化。**无 JWT 认证**（被 Java `RagService` HTTP 调用）。

**请求**:
```
POST /rag/embed
Content-Type: application/json

{"text": "三体中的面壁计划"}
```

**响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "embedding": [0.023, -0.156, ...],
    "dimension": 1024
  }
}
```

**实现**: `routers/rag.py:106` — `DixiyangEmbeddings.embed_query()`（优先 httpx 调 Java embed，降级 sentence_transformers）。

---

## 三、Java Spring 端点（对照参考）

Java `RagController.java` 提供相同的 4 个端点，全部通过 `ChromaDB REST API` 而非 LangChain 实现：

| 方法 | 路径 | 对比 Python |
|------|------|-------------|
| GET | `/rag/stats` | `getStats()` → 调 ChromaDB `GET /api/v2/.../collections` |
| GET | `/rag/count` | `getCollectionCount()` → 调 ChromaDB `GET .../collections/{id}/count` |
| GET | `/rag/documents` | `getDocuments(page, pageSize)` → 调 ChromaDB `POST .../collections/{id}/get` |
| POST | `/rag/search` | `search(query, topK)` → 先调 Python `/rag/embed` 获取向量，再调 ChromaDB `POST .../collections/{id}/query` |

**核心差异**:
- Java 直接调 ChromaDB REST API（端口 8000）
- Python 通过 `langchain_chroma.Chroma` 封装层（内部也走 HTTP，但 LangChain 管理连接）
- Java 的 search 多一步 reranker 精排（调 Python `/api/rag/rerank`）
- Java 的 search 调用 Python `/api/rag/embed` 获取 query embedding
- Python 的 search 直接在本地用 `DixiyangEmbeddings` 生成 embedding

### Java 特有端点

Java 无 `/rag/embed` 端点（embedding 由 Python 提供）。

---

## 四、前端 API 调用

**文件**: `dixiyang-vue/Dixiyang-vue3/src/api/ragApi.ts`

```typescript
// 获取统计
export const getRagStats = async () => {
  const res = await http.get('/rag/stats')
  return assertApiResponse<RagStats>(res)  // 返回 {code, msg, data}
}

// 获取文档列表（分页）
export const getRagDocuments = async (page = 1, pageSize = 20) => {
  const res = await http.get('/rag/documents', { params: { page, pageSize } })
  return assertApiResponse<RagDocPage>(res)
}

// 搜索（POST，query params）
export const searchRag = async (query: string, topK = 5) => {
  const res = await http.post('/rag/search', null, { params: { query, topK } })
  return assertApiResponse<RagSearchResult>(res)
}
```

**注意**: 前端以 `res.data` 获取实际数据（HTTP 拦截器返回完整 `{code, msg, data}` 对象）。

**页面**:
- `RagKnowledgeView.vue` — RAG 知识库浏览页（统计 + 文档列表 + 搜索）
- `RagAssistantView.vue` — RAG 助手页（聊天 + useRag 复选框）

---

## 五、RAG 启用机制

### 5.1 后端启用标志 `is_rag_enabled()`

Python `routers/chat.py:30`:
```python
def is_rag_enabled() -> bool:
    global _rag_enabled
    if _rag_enabled is not None:
        return _rag_enabled
    try:
        Chroma(...)  # 尝试创建 LangChain Chroma 实例
        _rag_enabled = True
    except Exception:
        _rag_enabled = False
    return _rag_enabled
```

- 惰性检测（首次调用时检查，结果缓存）
- 使用 `langchain_chroma.Chroma` 纯 LangChain 方式，不访问内部属性
- 仅检测 Chroma 是否可达，不关心具体集合内容

### 5.2 工具注入控制

只在 `_stream_with_tool_loop` 中使用（`chat.py:273`）：
```python
tools = get_all_tools(novel_id)
if is_rag_enabled():
    tools.append(knowledge_search)
```

- `GET /chat` 和 `POST /chat`（非流式）不使用工具循环，不涉及此标志
- `POST /chat/stream` 和 `POST /chat/regenerate` 走工具循环，会检查

### 5.3 `useRag` 用户标志（与 `is_rag_enabled` 正交）

| 标志 | 作用范围 | 说明 |
|------|---------|------|
| `is_rag_enabled()` | 后端全局 | Chroma 可达时才有 knowledge_search 工具 |
| `req.use_rag` | 单次对话 | 控制是否注入角色/故事节点固定上下文（`build_fixed_context`） |

- `use_rag=true` + `is_rag_enabled()=false` → 有固定上下文，无向量检索
- `use_rag=false` + `is_rag_enabled()=true` → 无固定上下文，有向量检索
- 两者完全正交，可独立开关

### 5.4 Spring 对照

Java `ChatController.java`:
```java
this.ragEnabled = (ragService != null);  // Bean 注入时确定
```
`useRag` 在 Java 端发送但不实际读取（`ChatRequest` 中有字段但 `chatStream()` 不使用）。

---

## 六、数据流
### 6.1 知识库管理流
```
用户点击「RAG 知识库」→ RagKnowledgeView.vue
  ├── onMounted → getRagStats()      → GET  /rag/stats      → 显示统计
  └── onMounted → getRagDocuments()  → GET  /rag/documents  → 显示文档列表

用户搜索 → handleSearch() → searchRag(query) → POST /rag/search?query=...→ 展示结果
```

### 6.2 聊天流（含 RAG 工具调用）
```
用户输入消息 → RagAssistantView.vue
  └── sendStreamMessage()
        └── POST /api/chat/stream
              Body: { message, useRag, novelId, ... }
              │
              ▼
        chat.py:_build_stream_messages()
          ├── if useRag → build_fixed_context()  // 角色/节点上下文
          └── 拼装 system + user prompt
              │
              ▼
        _stream_with_tool_loop()
          ├── tools = get_all_tools(novel_id)
          ├── if is_rag_enabled() → tools.append(knowledge_search)
          │
          ▼
        LLM (DeepSeek) 收到 system + user prompt + tool_spec
          │
          ├── LLM 自行判断 → 可能调用 knowledge_search(query)
          │     └── knowledge_search_tool.py
          │           ├── langchain_chroma.Chroma.similarity_search_with_score()
          │           ├── reranker 精排
          │           └── 返回格式化文本
          │
          └── 最终回答 → SSE 流回前端
```

---

## 七、配置文件对照

| 配置项 | 环境变量 | Python 默认值 | Java 默认值 |
|--------|---------|---------------|-------------|
| Chroma 持久化目录 | `CHROMA_PERSIST_DIR` | `./storage/vectordb_4060` | N/A（Java 直连 HTTP） |
| Chroma 集合名 | `CHROMA_COLLECTION_NAME` | `dixiyang_knowledge` | `dixiyang_knowledge` |
| Chroma 主机 | `CHROMADB_HOST` | N/A（本地持久化） | `[::1]` |
| Chroma 端口 | `CHROMADB_PORT` | N/A（本地持久化） | `8000` |
| Python Embedding 服务 | — | 内置 `DixiyangEmbeddings` | `http://localhost:8085/api/rag/embed` |

---

## 八、端口占用

| 服务 | 端口 | 用途 |
|------|------|------|
| ChromaDB | 8000 | 向量数据库 HTTP API |
| Java Spring Boot | 8084 | 业务 API（含 RAG 代理） |
| Python FastAPI | 8085 | RAG Embedding + 知识库管理 API |
| Vue Dev Server | 5173 | 前端开发服务器（代理 /api → 8084） |
| MySQL | 3306 | 关系数据库 |

---

## 九、文件索引

| 文件 | 角色 |
|------|------|
| `DixyangFast/src/dixiyang/routers/rag.py` | Python RAG 知识库 API（stats/count/documents/search/embed） |
| `DixyangFast/src/dixiyang/routers/chat.py` | Python 聊天 API（含 `is_rag_enabled()` + `knowledge_search` 工具注入） |
| `DixyangFast/src/dixiyang/services/knowledge_search_tool.py` | `@tool knowledge_search` 工具实现 |
| `DixyangFast/src/dixiyang/services/embeddings.py` | `DixiyangEmbeddings`（httpx → sentence_transformers 降级） |
| `dixiyang-engine/.../Controller/RagController.java` | Java RAG 知识库 API |
| `dixiyang-engine/.../Service/RagService.java` | Java RAG 业务逻辑（ChromaDB REST 直连） |
| `dixiyang-engine/.../Controller/ChatController.java` | Java 聊天 API（`ragEnabled` 标志） |
| `dixiyang-engine/.../Service/chat/agent/KnowledgeSearchTool.java` | Java `@Tool knowledge_search` |
| `dixiyang-vue/.../src/api/ragApi.ts` | 前端 RAG API 调用封装 |
| `dixiyang-vue/.../src/views/RagKnowledgeView.vue` | RAG 知识库页面 |
| `dixiyang-vue/.../src/views/RagAssistantView.vue` | RAG 助手页面（含 useRag 复选框） |
