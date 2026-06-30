# rag-shared - Dixiyang 共享 RAG 核心库

可被 **DixyangFast (Python)** 和 **dixiyang-engine (Java/Python API)** 共同使用的 RAG 知识库构建与检索库。

## 🎯 设计目标

- **多硬件自适配**: 自动检测 CPU/GPU，加载对应最优配置
- **多数据源统一**: 支持 Markdown/CSV/JSON/TXT 统一处理流水线
- **增量更新**: 基于 mtime+hash 的智能增量，避免重复处理
- **跨语言复用**: Python 包可被 Java (via GraalPy/Jython/子进程) 调用
- **零配置部署**: 环境变量覆盖，适配 CI/CD 和多机器环境

## 📦 安装

```bash
# 开发模式安装（推荐）
uv pip install -e .

# 或直接依赖（在 DixyangFast/pyproject.toml 中）
# dixiyang-rag-shared @ file://../rag-shared
```

## 🚀 快速使用

### 命令行

```bash
# 进入 DixyangFast 目录运行
cd ../DixyangFast

# 自动检测硬件处理
uv run python -m rag_shared.processor --hardware auto

# 指定配置
uv run python -m rag_shared.processor --hardware rtx_4060
```

### Python API

```python
from rag_shared import (
    load_config, 
    RAGProcessor, 
    get_config_summary,
    RAGConfig,
    DocumentChunk,
)

# 1. 加载配置（自动检测硬件）
config = load_config(
    hardware="auto",  # 或 "r5_5600u", "rtx_4060"
    config_dir=Path("path/to/rag-shared/config")
)
print(get_config_summary(config))

# 2. 自定义路径
config = RAGConfig(
    vectordb_path="./my_vectordb",
    books_dir="./my_books",
    # ... 其他字段
)

# 3. 运行处理器
processor = RAGProcessor(config)
stats = processor.run(incremental=True)
print(f"处理完成: {stats['total_chunks']} chunks")

# 4. 检索示例
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer(config.embedding_model, device=config.device)
client = chromadb.PersistentClient(path=config.vectordb_path)
col = client.get_collection(config.collection_name)

query = "三国演义诸葛亮"
query_emb = model.encode([query]).tolist()
results = col.query(query_embeddings=query_emb, n_results=5)
```

## ⚙️ 配置系统

### 配置文件层级

```
rag_base.yaml          # 通用基础配置（数据源、切分规则、元数据模板）
    ↓ 合并
rag_r5_5600u.yaml      # CPU 专用（小模型、大worker、无重排序）
rag_rtx_4060.yaml      # GPU 专用（大模型、FP16、重排序、大batch）
    ↓ 环境变量覆盖（最高优先级）
RAG_DEVICE, RAG_EMBEDDING_MODEL, RAG_BATCH_SIZE...
```

### 硬件预设对比

| 参数 | r5_5600u (CPU) | rtx_4060 (GPU) |
|------|----------------|----------------|
| Embedding | bge-small-zh-v1.5 | bge-m3 |
| 精度 | FP32 | FP16 |
| chunk_size | 400 | 600 |
| batch_size | 16 | 64 |
| reranker | 关闭 | bge-reranker-v2-m3 |
| workers | 5 | 2 |
| vectordb | ./storage/vectordb_r5 | ./storage/vectordb_4060 |

### 环境变量覆盖表

| 环境变量 | 对应字段 | 示例 |
|----------|----------|------|
| `RAG_DEVICE` | device | `cuda` / `cpu` |
| `RAG_EMBEDDING_MODEL` | embedding_model | `BAAI/bge-m3` |
| `RAG_BATCH_SIZE` | batch_size | `32` |
| `RAG_CHUNK_SIZE` | chunk_size | `500` |
| `RAG_VECTORDB_PATH` | vectordb_path | `./my_vectordb` |
| `RAG_CACHE_DIR` | cache_dir | `./models/cache` |
| `RAG_NUM_WORKERS` | num_workers | `4` |
| `RAG_USE_RERANKER` | use_reranker | `true` / `false` |

## 📂 数据处理流水线

```
文件发现 → 加载器路由 → 语义切分 → Embedding编码 → Chroma写入 → JSONL备份
    ↓           ↓           ↓           ↓            ↓           ↓
collect_  .md→Markdown  标题层级   sentence-   批量upsert  按source分文件
files()   .csv→CSVLoader  递归切分   transformers           存储
          .json→JSONLoader               ↓
          .txt→TextLoader           归一化+向量化
```

### 内置加载器

| 扩展名 | 加载器 | 适用场景 | 关键特性 |
|--------|--------|----------|----------|
| `.md` | `MarkdownLoader` | 书籍、文档 | 按 `#`/`##` 标题层级切分，保留章节元数据 |
| `.csv` | `CSVLoader` | 结构化数据 | 模版化行转文本，自动识别法条/二手车/QA |
| `.json` | `JSONLoader` | QA对、标注数据 | 保留 instruction/input/output 结构 |
| `.txt` | `TextLoader` | 纯文本 | 空行分段，简单场景 |

## 🔄 增量更新

```python
# 自动增量（默认开启）
processor = RAGProcessor(config)
stats = processor.run(incremental=True)  # 只处理变更文件

# 强制全量
stats = processor.run(incremental=False)  # --full 参数等效
```

**状态文件** (`storage/rag/file_states.json`)：
```json
{
  "my_books/三国演义.md": {
    "mtime": 1700000000.0,
    "hash": "a1b2c3d4...",
    "chunks_count": 1245,
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

## 📊 输出结构

```
storage/rag/
├── chroma_db/
│   ├── vectordb_r5/        # CPU 版向量库
│   └── vectordb_4060/      # GPU 版向量库（维度不同，隔离存储）
├── chunks/
│   ├── book.jsonl          # 书籍分块备份
│   ├── law.jsonl           # 法律条文备份
│   ├── cars.jsonl          # 二手车数据备份
│   └── qa.jsonl            # QA数据备份
├── metadata.json           # 本次处理元数据汇总
├── processing_stats.json   # 处理统计（耗时、错误等）
└── file_states.json        # 增量更新状态
```

## 🧪 测试

```bash
# 运行配置测试
cd ../DixyangFast
uv run python -c "
from rag_shared.config import load_config, get_config_summary
for hw in ['r5_5600u', 'rtx_4060', 'auto']:
    cfg = load_config(hw, config_dir=Path('../rag-shared/config'))
    print(get_config_summary(cfg))
"
```

## 📝 开发指南

### 添加新数据源

1. 在 `rag_base.yaml` 的 `data_sources.supported_extensions` 添加扩展名
2. 在 `processor.py` 的 `loaders` 字典注册新加载器
3. 实现 `BaseLoader` 子类，实现 `load()` 生成 `DocumentChunk`

### 添加新硬件预设

1. 在 `config/` 创建 `rag_xxx.yaml`
2. 在 `config.py` 的 `HARDWARE_PRESETS` 注册
3. 在 `detect_hardware()` 添加检测逻辑

### 自定义切分策略

修改 `rag_base.yaml` 的 `text_splitter` 或在代码中传入自定义 `RecursiveCharacterTextSplitter`。

## 🔗 集成到 Java 后端

```java
// 方案 1: 子进程调用
ProcessBuilder pb = new ProcessBuilder(
    "uv", "run", "python", "-m", "rag_shared.processor",
    "--hardware", "auto"
);
pb.directory(new File("/path/to/DixyangFast"));
Process process = pb.start();

// 方案 2: GraalPy 嵌入（需引入 graalpy 依赖）
// Context context = Context.create();
// Value ragModule = context.eval("python", "import rag_shared; rag_shared.load_config('auto')");
```

## 📄 许可证

MIT License - 与 Monorepo 根目录一致