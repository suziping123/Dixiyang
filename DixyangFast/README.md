# Dixiyang Fast - RAG 知识库构建系统

Python 后端（RAG 课程作业），使用 `uv` 管理环境，依赖 Monorepo 共享库 `rag-shared`。

## 📁 项目结构（Monorepo）

```
Dixiyang/                          # Monorepo 根目录
├── dixiyang-engine/               # Java Spring Boot 后端（找工作用）
├── dixiyang-vue/                  # Vue 3 前端（最终构建 dist 部署）
├── DixyangFast/                   # Python 后端 - RAG 课程作业（本项目）
│   ├── my_books/                  # 25 本书籍 Markdown
│   ├── datasets/                  # 原始数据集
│   │   └── datasets/              # 结构化数据
│   ├── storage/                   # 本地存储（向量库、聊天记录等）
│   ├── pyproject.toml             # 依赖配置（依赖 ../rag-shared）
│   └── README.md                  # 本文件
├── rag-shared/                    # 🔑 共享 RAG 核心库（Python 包）
│   ├── python/rag_shared/         # 可被 Java/Python 共同调用
│   │   ├── config.py              # 多硬件配置管理
│   │   ├── processor.py           # 数据处理流水线
│   │   └── __init__.py
│   ├── config/                    # YAML 配置文件
│   │   ├── rag_base.yaml          # 通用基础配置
│   │   ├── rag_r5_5600u.yaml      # CPU 配置 (R5 5600U)
│   │   └── rag_rtx_4060.yaml      # GPU 配置 (RTX 4060 Laptop)
│   ├── pyproject.toml             # 共享库打包配置
│   └── README.md
└── docs/                          # 项目总体文档
```

## ⚡ 快速开始

### 1. 安装依赖（在 DixyangFast 目录下）

```bash
cd DixyangFast

# 使用 uv 安装（推荐）
uv sync

# 或手动安装共享库 + 依赖
uv pip install -e ../rag-shared
uv pip install -r requirements-rag.txt  # 如果有额外依赖
```

### 2. 运行 RAG 数据处理

```bash
# 自动检测硬件（推荐）
uv run python -m rag_shared.processor --hardware auto

# 指定硬件配置
uv run python -m rag_shared.processor --hardware r5_5600u   # CPU 模式
uv run python -m rag_shared.processor --hardware rtx_4060   # GPU 模式

# 全量重建（忽略增量）
uv run python -m rag_shared.processor --hardware auto --full

# 重置向量库
uv run python -m rag_shared.processor --hardware auto --reset-db

# 仅查看统计
uv run python -m rag_shared.processor --hardware auto --stats-only
```

### 3. 在代码中使用

```python
from rag_shared import load_config, RAGProcessor, get_config_summary

# 加载配置（自动检测硬件）
config = load_config("auto", config_dir=Path("../rag-shared/config"))
print(get_config_summary(config))

# 运行处理
processor = RAGProcessor(config)
stats = processor.run(incremental=True)
```

## 🖥️ 双机器配置对比

| 配置项 | R5 5600U (CPU) | RTX 4060 Laptop (GPU) |
|--------|----------------|----------------------|
| **设备** | CPU (6核12线程) | CUDA (8GB VRAM) |
| **Embedding 模型** | `bge-small-zh-v1.5` (33M) | `bge-m3` (567M) |
| **精度** | FP32 | FP16 (半精度) |
| **Chunk 大小** | 400 字 | 600 字 |
| **Batch Size** | 16 | 64 |
| **重排序** | 关闭 | 开启 (bge-reranker-v2-m3) |
| **并行 Workers** | 5 | 2 |
| **向量库路径** | `./storage/vectordb_r5` | `./storage/vectordb_rag/vectordb_4060` |
| **预估处理速度** | ~500 chunks/分钟 | ~5000 chunks/分钟 |

## ⚙️ 配置切换方式

### 方式 1：命令行参数（推荐）
```bash
uv run python -m rag_shared.processor --hardware rtx_4060
```

### 方式 2：环境变量（持久化，适合 CI/CD）
```bash
export RAG_HARDWARE=rtx_4060
export RAG_DEVICE=cuda
export RAG_EMBEDDING_MODEL=BAAI/bge-m3
uv run python -m rag_shared.processor
```

### 方式 3：代码中指定
```python
config = load_config("rtx_4060", config_dir=Path("../rag-shared/config"))
```

### 方式 4：自定义配置文件
```bash
cp ../rag-shared/config/rag_rtx_4060.yaml ../rag-shared/config/rag_my_custom.yaml
# 编辑自定义配置
uv run python -m rag_shared.processor --hardware ../rag-shared/config/rag_my_custom.yaml
```

## 📊 数据源与处理策略

| 来源 | 文件 | 类型 | 切分策略 | 关键元数据 |
|------|------|------|----------|------------|
| 书籍 | `my_books/*.md` (25本) | 长文档 | 语义切分（按标题层级） | book_title, author, category, chapter, section |
| 法律 | `datasets/datasets/法律数据集.csv` | 结构化 | 逐行（每条文=1 chunk） | law_name, article_num |
| 公司 | `datasets/datasets/华清远见.txt` | 短文本 | 段落分割 | company, section |
| 二手车 | `datasets/datasets/guazi.csv` | 表格 | 行转文本模版 | brand, model, year, mileage, city, price |
| 医学QA | `datasets/datasets/Chinese.json` | QA对 | 整条保留 | instruction, input, output, category |

## 🔄 增量更新机制

- **状态文件**: `storage/rag/file_states.json`
- **判断依据**: 文件 `mtime` + `MD5 hash` 双重校验
- **自动跳过**: 内容未修改的文件
- **强制全量**: `--full` 参数

## 📝 输出目录

处理后的数据输出到 Monorepo 共享存储：

```
~/项目/Dixiyang/storage/rag/
├── chroma_db/              # Chroma 向量库（按硬件隔离）
│   ├── vectordb_r5/        # CPU 版本
│   └── vectordb_4060/      # GPU 版本
├── chunks/                 # 分块文本备份 (JSONL)
├── metadata.json           # 元数据汇总
├── processing_stats.json   # 处理统计
└── file_states.json        # 增量更新状态
```

> 注意：向量库按硬件配置隔离（`vectordb_r5` vs `vectordb_4060`），避免模型维度不一致。

## 🐛 常见问题

### 显存不足 (OOM)
```bash
export RAG_BATCH_SIZE=32
# 或修改 ../rag-shared/config/rag_rtx_4060.yaml
```

### 模型下载慢
```bash
export HF_ENDPOINT=https://hf-mirror.com
export SENTENCE_TRANSFORMERS_HOME=./models/cache
```

### 换 Embedding 模型
```bash
export RAG_EMBEDDING_MODEL=BAAI/bge-base-zh-v1.5
```

## 🔗 相关链接

- [Monorepo 根目录 README](../README.md)
- [共享库 rag-shared 文档](../rag-shared/README.md)
- [RAG 理论基础](../DixyangFast/03.RAG理论基础.md)