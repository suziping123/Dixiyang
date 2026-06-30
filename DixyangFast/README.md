# Dixiyang Fast - RAG 知识库构建系统

Python 后端，使用 `uv` 管理环境，依赖 Monorepo 共享库 `rag-shared`。

## 整体架构

```
Dixiyang/
├── dixiyang-engine/       Java Spring Boot 后端（小说管理 + AI 聊天）
├── dixiyang-vue/          Vue 3 前端（创作管理平台 + RAG 聊天界面）
├── DixyangFast/           Python 后端（RAG 课程作业）← 你在 Windows 上操作的目录
│   ├── my_books/          27 本书 Markdown（133MB，不进 git）
│   ├── datasets/datasets/ 结构化数据（622MB，不进 git）
│   └── storage/           运行时生成（向量库、日志等）
├── rag-shared/            共享 RAG 核心库（Python 包）
└── docs/                  项目文档
```

**三端关系**：
- **Python（DixyangFast）**：离线构建向量库（Chroma），把书籍/数据集向量化
- **Java（dixiyang-engine）**：在线聊天服务，用 Qdrant 做向量检索（故事节点），调 DeepSeek 生成
- **Vue（dixiyang-vue）**：用户界面，聊天时可选开启 RAG 检索

---

## 数据文件说明

| 文件 | 大小 | 是否进 git | 说明 |
|------|------|-----------|------|
| `my_books/*.md` | 133MB | 否（.gitignore） | 27 本书的 Markdown，需要手动拷到 Windows |
| `datasets/datasets/*` | 622MB | 否（.gitignore） | 4 个数据集（法律、二手车、QA、公司） |
| `storage/vectordb_4060/` | ~几百MB | 否 | 构建产物，Windows→Linux 传输 |
| `rag-shared/` 代码 | <1MB | 是 | 代码进 git |
| `DixyangFast/` 代码 | <1MB | 是 | 代码进 git |

**结论**：数据文件需要单独转移（U盘或 scp），git 只管代码。

---

## 双机协作：Windows 构建 + Linux 部署

**核心思路**：Windows 笔记本（RTX 4060）有 GPU，跑得快，用来构建向量库；
构建完成后，把向量库文件传到 Linux（R5 5600U），Linux 只负责检索查询。

**关键前提**：两台机器必须用同一个 Embedding 模型（`bge-m3`，1024维），否则向量维度不一致，无法互用。

### 关于统一用 bge-m3 的影响

| 对比项 | bge-small (之前) | bge-m3 (现在) |
|--------|-----------------|---------------|
| 参数量 | 33M | 567M |
| 向量维度 | 512 | 1024 |
| CPU 编码速度 | 快 | 慢约 3-5 倍 |
| 检索质量 | 一般 | 好（多语言、长文本支持） |
| 影响 | — | **构建在 Windows GPU 上做，Linux 只查一条 query，无感知差异** |

### 第一步：Windows 上安装环境（只需做一次）

```
1. 安装 Python 3.11+
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. 安装 uv
   PowerShell 运行：
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

3. 把整个 Dixiyang 项目拷到 Windows（git clone 或 U盘）
   确保目录结构：
   Dixiyang/
   ├── DixyangFast/           ← 在这里操作
   │   ├── my_books/           ← 需要这 27 个 .md（从 Linux 拷）
   │   └── datasets/datasets/  ← 需要这 4 个文件（从 Linux 拷）
   └── rag-shared/             ← 共享库代码
```

### 第二步：Windows 上安装依赖（只需做一次）

```powershell
cd Dixiyang\DixyangFast
uv venv
.\.venv\Scripts\activate

# 共享库
uv pip install -e ..\rag-shared

# PyTorch GPU
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 其他依赖
uv pip install chromadb sentence-transformers langchain-text-splitters pyyaml tqdm pandas
```

### 第三步：Windows 上构建向量库

```powershell
cd Dixiyang\DixyangFast
.\.venv\Scripts\activate

$env:HF_ENDPOINT = "https://hf-mirror.com"
$env:SENTENCE_TRANSFORMERS_HOME = ".\models\cache"

# 首次全量构建
python -m rag_shared.processor --hardware rtx_4060 --full

# 后续增量更新（去掉 --full）
python -m rag_shared.processor --hardware rtx_4060
```

预计耗时：31 个文件，RTX 4060 GPU 约 10-15 分钟。

### 第四步：传向量库到 Linux

```powershell
# Windows 上压缩
tar -czf vectordb_4060.tar.gz -C DixyangFast\storage vectordb_4060

# scp 传到 Linux（替换 IP 和用户名）
scp vectordb_4060.tar.gz 用户名@192.168.1.x:~/项目/Dixiyang/DixyangFast/storage/
```

或用 U盘直接拷 `DixyangFast\storage\vectordb_4060\` 整个文件夹。

### 第五步：Linux 上解压并验证

```bash
cd ~/项目/Dixiyang/DixyangFast/storage
tar -xzf vectordb_4060.tar.gz
rm vectordb_4060.tar.gz

# 验证
cd ..
PYTHONPATH=../rag-shared/python .venv/bin/python -c "
import chromadb
client = chromadb.PersistentClient(path='storage/vectordb_4060')
col = client.get_collection('dixiyang_knowledge')
print(f'文档总数: {col.count()}')
"
```

### 第六步：Linux 上检索测试

```bash
cd ~/项目/Dixiyang/DixyangFast
PYTHONPATH=../rag-shared/python .venv/bin/python ../scripts/visualize_rag.py --hardware rtx_4060 --query "三体讲了什么"
```

---

## 前端可视化：当前状态与方案

### 现状

| 端 | 向量库 | 可视化 |
|----|--------|--------|
| Python CLI | Chroma | `visualize_rag.py`（命令行，已有） |
| Java Spring Boot | Qdrant | 无（向量检索对前端透明） |
| Vue 前端 | — | 无（只有聊天界面，看不到检索过程） |

**Vue 前端的 RAG 是"黑盒"**：用户勾选"启用 RAG 检索"→ 后端自动向量检索 → 注入 prompt → 返回 AI 回答。
前端看不到：检索到了哪些文档片段、相似度分数、来源等。

### 需要新增的功能

如果你要在前端看到向量数据库的具体情况，需要做以下工作：

**方案 A：Python 端加 Web 可视化（推荐，改动最小）**

在 `DixyangFast` 中加一个 Flask/Streamlit 页面，展示：
- 向量库统计（总文档数、按来源/分类分布饼图）
- 检索测试（输入 query，展示 Top-K 结果 + 相似度分数 + 来源）
- 数据探索（按书籍/分类浏览 chunk 列表）

**方案 B：Java 后端暴露向量库 API**

在 `dixiyang-engine` 中新增接口，返回 Qdrant 中的向量统计和检索结果，Vue 前端新增对应页面。

**方案 C：独立可视化工具**

保留 CLI 工具 `visualize_rag.py`，在 Windows/Linux 终端直接用。

> 你想要哪种方案？我可以马上实现。

---

## 向量库内容说明（你的顾虑）

### 法律/二手车数据会不会干扰小说 RAG？

**不会。** 每个 chunk 都有 metadata 标记来源：

| source 值 | 含量 | 查询时 |
|-----------|------|--------|
| `book` | 小说内容 | 你的 RAG 主要用这个 |
| `law` | 法律条文 | 可过滤排除 |
| `cars` | 二手车数据 | 可过滤排除 |
| `qa` | 医学 QA | 可过滤排除 |
| `company` | 公司信息 | 可过滤排除 |

查询时可以加 filter：`collection.query(where={"source": "book"})` 只搜小说。

### 27 本书的分类

| 分类 | 书名 |
|------|------|
| 科幻小说 | 三体全集、诡秘之主 |
| 玄幻小说 | 蛊真人、玄鉴仙族 |
| 恐怖悬疑 | 神秘复苏、诡舍 |
| 推理悬疑 | 占星术杀人魔法、不可以 |
| 历史读物 | 明朝那些事儿、中国史话 |
| 古典文学 | 红楼梦、阅微草堂笔记 |
| 现代文学 | 鲁迅全集、余华作品全集 |
| 外国名著 | 呼啸山庄、鲁滨逊漂流记 |
| 科普自然 | 昆虫记、生命进化的跃升、鸟有膝盖吗、我包罗万象 |
| 心理学 | 思考快与慢 |
| 编剧写作 | 救猫咪、故事的解剖 |
| 民俗百科 | 都市传说百科全书 |
| 美食文化 | 食饮记 |
| 史诗文学 | 摩诃婆罗多 |

---

## Windows 构建命令速查

| 场景 | 命令 |
|------|------|
| 首次全量构建 | `python -m rag_shared.processor --hardware rtx_4060 --full` |
| 新增书籍后增量更新 | `python -m rag_shared.processor --hardware rtx_4060` |
| 查看向量库文档数 | `python -m rag_shared.processor --hardware rtx_4060 --stats-only` |
| 重置重建 | 删除 `storage\vectordb_4060\`，再 `--full` |

---

## 双机器配置

| 配置项 | Windows RTX 4060（构建） | Linux R5 5600U（查询） |
|--------|--------------------------|------------------------|
| 用途 | 构建向量库 | 检索查询 |
| 设备 | CUDA (8GB VRAM) | CPU (6核12线程) |
| Embedding | `BAAI/bge-m3` (FP16) | `BAAI/bge-m3` (FP32) |
| 向量库路径 | `storage/vectordb_4060` | `storage/vectordb_4060`（同份） |

---

## 常见问题

### Windows 上 torch.cuda.is_available() 返回 False
```powershell
python -c "import torch; print(torch.cuda.is_available())"
# False 就重装 CUDA 版 PyTorch
uv pip install torch --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

### 模型下载慢
```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"   # Windows
export HF_ENDPOINT=https://hf-mirror.com      # Linux
```

### 显存不足 (OOM)
修改 `rag-shared/config/rag_rtx_4060.yaml`，把 `batch_size` 降一半。

### 向量库维度不一致报错
两边用了不同的 Embedding 模型。解决：统一用 `bge-m3`，在 Windows 上 `--full` 重建。

### scp 传文件太慢
压缩后再传：`tar -czf vectordb_4060.tar.gz -C storage vectordb_4060`

---

## 相关链接

- [Monorepo 根目录 README](../README.md)
- [共享库 rag-shared 文档](../rag-shared/README.md)
