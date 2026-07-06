# RAG 离线构建流程：GPU 文本切割与向量化

## 一、概述

RAG 离线构建管道将 **MD/TXT/CSV/JSON** 源文件经过 **文本切分 → Embedding 编码 → 向量库存储** 三个步骤，构建可被语义检索的知识库。

核心代码位于 `rag-shared/python/rag_shared/`，支持 GPU（RTX 4060）和 CPU（R5 5600U）双模式。

### 数据流

```
my_books/*.md         datasets/*.{csv,json,txt}
       │                       │
       ▼                       ▼
  MarkdownLoader         CSVLoader / TextLoader / JSONLoader
       │                       │
       └───────────┬───────────┘
                   ▼
           DocumentChunk[]     ←── 文本分块
                   │
                   ▼
          EmbeddingModel       ←── sentence-transformers (GPU/CPU)
                   │
                   ▼
            VectorDB           ←── ChromaDB PersistentClient
                   │
                   ▼
     storage/vectordb_4060/
     ├── chroma.sqlite3        (元数据)
     └── dixiyang_knowledge/   (向量数据)
```

---

## 二、硬件自动检测

`config.py:detect_hardware()` 自动选择配置预设：

```
torch.cuda.is_available()
  ├── true  → 检查 GPU 型号
  │     ├── "RTX 4060"     → rtx_4060.yaml     (FP16 + reranker)
  │     ├── VRAM ≥ 6GB     → rtx_4060.yaml     (其他 GPU)
  │     └── VRAM < 6GB     → cpu_fallback      (低显存回退)
  └── false → 检查 CPU 型号
        ├── "R5 5600U"     → r5_5600u.yaml     (CPU 优化)
        └── 其他            → cpu_fallback      (通用 CPU)
```

**GPU 配置（`rag_rtx_4060.yaml`）关键参数：**

| 参数 | GPU (RTX 4060) | CPU (R5 5600U) |
|------|----------------|----------------|
| `device` | `cuda` | `cpu` |
| `precision` | `fp16` | `fp32` |
| `batch_size` | 64 | 32 |
| `max_length` | 8192 | 512 |
| `half_precision` | true | false |
| `num_workers` | 2 | 10 |
| `use_reranker` | true | false |

---

## 三、第一步：文本加载与切分

### 3.1 文件类型与加载器

| 扩展名 | 加载器 | 说明 |
|--------|--------|------|
| `.md` | `MarkdownLoader` | 按 `#` `##` 标题层级切分 → `RecursiveCharacterTextSplitter` |
| `.csv` | `CSVLoader` | 按行处理，支持 cars/law 等模板 |
| `.txt` | `TextLoader` | 按 `\n\n` 分段 |
| `.json` | `JSONLoader` | QA 对格式（instruction/input/output） |

### 3.2 Markdown 切分流程（最核心）

```
MarkdownLoader.load(file_path)
  │
  ├── 1. 解析文件名
  │     文件名格式: "三体 (刘慈欣).md"
  │     → book_title="三体", author="刘慈欣"
  │
  ├── 2. 匹配分类
  │     rag_base.yaml → book_categories
  │     "三体" → "科幻小说"
  │
  ├── 3. _split_by_headers(text)
  │     正则匹配 # (h1) 和 ## (h2) 标题行
  │     → 按标题分割为语义段落（保留层级关系）
  │
  ├── 4. _split_text(section_content)
  │     RecursiveCharacterTextSplitter(
  │       chunk_size=600,          ← 配置可调
  │       chunk_overlap=120,       ← 相邻块重叠 20%
  │       separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
  │       keep_separator=True
  │     )
  │     → 进一步切分为更小的文本块
  │
  └── 5. 过滤短块 + 注入元数据
         min_chunk_length=50（跳过过短块）
         metadata = {
           source: "book",
           book_title, author, category,
           chapter(h1), section(h2),
           chunk_id: "三体_0",
           file_path
         }
```

### 3.3 切分示例

```
原始文本（# 三体 / ## 汪淼 / 汪淼是一个纳米材料科学家...）
  │
  ▼
按 h1/h2 切分:
  [{h1:"三体", h2:"汪淼", content:"汪淼是一个纳米材料科学家..."}]
  │
  ▼
RecursiveCharacterTextSplitter (chunk_size=600):
  chunk_0: "汪淼是一个纳米材料科学家。他拥有...（约 600 字）"
  chunk_1: "...坚韧不拔的性格。在《三体》中...（约 600 字，重叠 120 字）"
```

### 3.4 语义切分的优势

| 方式 | 切分逻辑 | 问题 |
|------|---------|------|
| ❌ 固定长度切割 | 每 N 字符一刀切 | 可能在句子中间断开，丢失语义 |
| ✅ 递归字符分割 | 按 \n\n → \n → 。→ ！→ ；→ ，→ 空格 依次尝试 | 尽量在自然边界切割，保留语义完整性 |

---

## 四、第二步：Embedding 向量化

### 4.1 模型

- **模型**: `BAAI/bge-m3`（BAAI 通用多模态 Embedding 模型）
- **输出维度**: 1024
- **相似度度量**: Cosine（向量归一化后等价于内积）

### 4.2 GPU 加速

```python
# embeddings.py
class EmbeddingModel:
    def _load_model(self):
        self.model = SentenceTransformer(
            "BAAI/bge-m3",
            device="cuda",                          # GPU
            cache_folder="./models/cache"
        )
        # GPU 模式：启用 FP16 半精度
        self.model.half()                           # 显存减半，速度翻倍
```

| 模式 | 精度 | 显存占用 | 编码速度（千条/秒） |
|------|------|---------|-------------------|
| CPU FP32 | FP32 | 0 MB | ~5 |
| GPU FP32 | FP32 | ~1200 MB | ~80 |
| GPU FP16 | FP16 | ~600 MB | ~150 |

### 4.3 分批编码

```
encode(texts)
  │
  ├── len(texts) ≤ 5000 → 一次性编码
  └── len(texts) > 5000 → 批量循环（每批 5000 条）
       │
       └── model.encode(
             batch,
             batch_size=64,              ← GPU 并行度
             show_progress_bar=True,
             convert_to_numpy=True,
             normalize_embeddings=True   ← L2 归一化
           )
           → List[float]  (1024 维)
```

### 4.4 为什么归一化？

归一化后 Cosine 距离 = 内积距离，HNSW 索引仅支持 L2 和内积两种度量。使用 Cosine + 归一化，既保证语义相似度准确，又利用 HNSW 加速检索。

---

## 五、第三步：写入向量数据库

### 5.1 ChromaDB 持久化

```python
# vectordb.py
self.client = chromadb.PersistentClient(path="./storage/vectordb_4060")
self.collection = self.client.get_or_create_collection(
    name="dixiyang_knowledge",
    metadata={"hnsw:space": "cosine"}   ← HNSW 索引使用余弦距离
)
```

### 5.2 批量写入

```python
# processor.py:RAGProcessor.process_file()
BATCH = 5000
for start in range(0, len(all_ids), BATCH):
    self.vectordb.collection.add(
        ids=all_ids[start:start + BATCH],
        documents=all_docs[start:start + BATCH],
        embeddings=all_embs[start:start + BATCH],
        metadatas=all_metas[start:start + BATCH],
    )
```

### 5.3 存储结构

```
storage/vectordb_4060/
├── chroma.sqlite3              ← 元数据（SQLite）：集合信息、ID → 文件映射
└── dixiyang_knowledge/
    ├── index/                  ← HNSW 索引文件
    │   ├── index_0.pkl
    │   └── index_0.parquet
    └── data/                   ← 向量与文档数据
        ├── embeddings_0.parquet
        └── documents_0.parquet
```

### 5.4 JSONL 备份

每个文件处理后，chunks 同时追加写入 `storage/rag/chunks/{source_type}.jsonl`，便于数据恢复和问题排查。

---

## 六、增量更新机制

```python
# tracker.py
class FileStateTracker:
    def is_changed(self, file_path) -> bool:
        # 双重校验：mtime + MD5 hash
        if key not in self.states: return True       # 新文件
        if mtime != old_mtime: return True            # 修改时间变更
        if hash != old_hash: return True              # 内容变更
        return False                                  # 未变化
```

- 状态存储在 `storage/rag/file_states.json`
- 每处理 100 个文件自动 checkpoint
- 全量模式（`--full`）忽略状态，重新处理所有文件

---

## 七、运行命令

```bash
cd /home/lijiajia/项目/Dixiyang/rag-shared

# GPU 全量重建
python -m rag_shared.processor --hardware rtx_4060 --full

# CPU 增量更新
python -m rag_shared.processor --hardware r5_5600u

# 查看统计
python -m rag_shared.processor --stats-only

# 重置向量库
python -m rag_shared.processor --reset-db
```

---

## 八、包结构

```
rag-shared/
├── config/
│   ├── rag_base.yaml              # 通用基础配置
│   ├── rag_rtx_4060.yaml          # GPU 配置
│   └── rag_r5_5600u.yaml          # CPU 配置
├── python/
│   └── rag_shared/
│       ├── __init__.py            # 公共 API（保持向后兼容）
│       ├── config.py              # 配置管理：检测硬件 + 合并 YAML
│       ├── tracker.py             # 文件状态追踪（增量更新）
│       ├── loaders.py             # 数据加载器 + 文本切分
│       ├── embeddings.py          # Embedding 模型封装
│       ├── vectordb.py            # 向量数据库封装
│       └── processor.py           # 主流程编排 + CLI 入口
├── pyproject.toml
└── README.md
```
