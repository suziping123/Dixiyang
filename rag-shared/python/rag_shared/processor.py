"""
RAG 数据处理主脚本
支持多硬件配置、增量更新、多源数据加载
"""
import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from tqdm import tqdm
import yaml

from .config import load_config, get_config_summary, RAGConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """文档分块"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "source": self.source
        }


class FileStateTracker:
    """文件状态追踪（用于增量更新）"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.states = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}")
        return {}

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, ensure_ascii=False, indent=2)

    def get_file_hash(self, file_path: Path) -> str:
        """计算文件 MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def is_changed(self, file_path: Path) -> bool:
        """检查文件是否变更"""
        key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        current_hash = self.get_file_hash(file_path)

        if key not in self.states:
            return True

        old_state = self.states[key]
        return (old_state.get('mtime') != current_mtime or
                old_state.get('hash') != current_hash)

    def update(self, file_path: Path, chunks_count: int):
        """更新文件状态"""
        key = str(file_path)
        self.states[key] = {
            'mtime': file_path.stat().st_mtime,
            'hash': self.get_file_hash(file_path),
            'chunks_count': chunks_count,
            'updated_at': datetime.now().isoformat()
        }


class BaseLoader:
    """基础加载器"""

    def __init__(self, config: RAGConfig):
        self.config = config

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        raise NotImplementedError


class MarkdownLoader(BaseLoader):
    """Markdown 文件加载器（按标题层级语义切分）"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        import re

        text = file_path.read_text(encoding='utf-8')

        # 从文件名提取书名和作者
        filename = file_path.stem
        book_title, author = self._parse_filename(filename)

        # 获取分类
        category = self.config.raw.get('book_categories', {}).get(book_title, "其他")

        # 按标题切分
        sections = self._split_by_headers(text)

        chunk_index = 0
        for section in sections:
            # 进一步按 chunk_size 切分
            sub_chunks = self._split_text(section['content'])

            for sub_chunk in sub_chunks:
                if len(sub_chunk.strip()) < self.config.raw.get('preprocessing', {}).get('min_chunk_length', 50):
                    continue

                metadata = {
                    "source": "book",
                    "book_title": book_title,
                    "author": author,
                    "category": category,
                    "chapter": section.get('h1', ''),
                    "section": section.get('h2', ''),
                    "chunk_id": f"{book_title}_{chunk_index}",
                    "file_path": str(file_path)
                }

                yield DocumentChunk(
                    content=sub_chunk.strip(),
                    metadata=metadata,
                    chunk_id=metadata["chunk_id"],
                    source="book"
                )
                chunk_index += 1

    def _parse_filename(self, filename: str) -> tuple:
        """解析文件名：书名 (作者).md"""
        import re
        match = re.match(r'^(.+?)\s*\((.+?)\)$', filename)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return filename, "未知"

    def _split_by_headers(self, text: str) -> List[Dict[str, str]]:
        """按 Markdown 标题层级切分"""
        import re

        lines = text.split('\n')
        sections = []
        current_h1 = ""
        current_h2 = ""
        current_content = []

        for line in lines:
            h1_match = re.match(r'^#\s+(.+)$', line)
            h2_match = re.match(r'^##\s+(.+)$', line)

            if h1_match:
                if current_content:
                    sections.append({
                        'h1': current_h1,
                        'h2': current_h2,
                        'content': '\n'.join(current_content)
                    })
                current_h1 = h1_match.group(1)
                current_h2 = ""
                current_content = [line]
            elif h2_match:
                if current_content:
                    sections.append({
                        'h1': current_h1,
                        'h2': current_h2,
                        'content': '\n'.join(current_content)
                    })
                current_h2 = h2_match.group(1)
                current_content = [line]
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                'h1': current_h1,
                'h2': current_h2,
                'content': '\n'.join(current_content)
            })

        return sections

    def _split_text(self, text: str) -> List[str]:
        """按 chunk_size 切分文本"""
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            keep_separator=True,
        )
        return splitter.split_text(text)


class CSVLoader(BaseLoader):
    """CSV 文件加载器"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        import pandas as pd

        df = pd.read_csv(file_path)
        filename = file_path.stem

        dataset_types = self.config.raw.get('dataset_types', {})

        for idx, row in df.iterrows():
            dtype = self._detect_dataset_type(filename, dataset_types)
            type_config = dataset_types.get(dtype, {})

            if dtype == 'cars':
                template = type_config.get('template', "{leixing} {nianfen} {licheng} {didian} {shoujia} {yuanjia}")
                content = template.format(**row.to_dict())
                metadata = {
                    "source": "cars",
                    "brand": row.get('leixing', '').split()[0] if row.get('leixing') else '',
                    "model": row.get('leixing', ''),
                    "year": str(row.get('nianfen', '')),
                    "mileage": str(row.get('licheng', '')),
                    "city": str(row.get('didian', '')),
                    "price": str(row.get('shoujia', '')),
                    "original_price": str(row.get('yuanjia', '')),
                    "chunk_id": f"cars_{idx}",
                    "file_path": str(file_path)
                }
            elif dtype == 'law':
                content = row.get('text', '')
                import re
                article_match = re.search(r'《.+?》第.+?条', content)
                article_num = article_match.group() if article_match else ''

                metadata = {
                    "source": "law",
                    "law_name": self._extract_law_name(content),
                    "article_num": article_num,
                    "chunk_id": f"law_{idx}",
                    "file_path": str(file_path)
                }
            else:
                content = row.to_json(force_ascii=False)
                metadata = {
                    "source": "csv",
                    "file": filename,
                    "row": idx,
                    "chunk_id": f"csv_{filename}_{idx}",
                    "file_path": str(file_path)
                }

            if content.strip():
                yield DocumentChunk(
                    content=content.strip(),
                    metadata=metadata,
                    chunk_id=metadata["chunk_id"],
                    source=dtype or "csv"
                )

    def _detect_dataset_type(self, filename: str, dataset_types: Dict) -> str:
        for dtype, config in dataset_types.items():
            pattern = config.get('file_pattern', '')
            if pattern and pattern.replace('*', '') in filename:
                return dtype
        return 'unknown'

    def _extract_law_name(self, text: str) -> str:
        import re
        match = re.search(r'《(.+?)》', text)
        return match.group(1) if match else "未知法律"


class TextLoader(BaseLoader):
    """纯文本加载器"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        text = file_path.read_text(encoding='utf-8')
        filename = file_path.stem

        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        dataset_types = self.config.raw.get('dataset_types', {})
        dtype = self._detect_dataset_type(filename, dataset_types)

        for idx, para in enumerate(paragraphs):
            if len(para) < 20:
                continue

            metadata = {
                "source": dtype or "text",
                "company": filename,
                "section": f"段落_{idx}",
                "chunk_id": f"{dtype}_{filename}_{idx}",
                "file_path": str(file_path)
            }

            yield DocumentChunk(
                content=para,
                metadata=metadata,
                chunk_id=metadata["chunk_id"],
                source=dtype or "text"
            )

    def _detect_dataset_type(self, filename: str, dataset_types: Dict) -> str:
        for dtype, config in dataset_types.items():
            pattern = config.get('file_pattern', '')
            if pattern and pattern.replace('*', '') in filename:
                return dtype
        return 'unknown'


class JSONLoader(BaseLoader):
    """JSON 文件加载器（QA 对）"""

    def load(self, file_path: Path) -> Generator[DocumentChunk, None, None]:
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        filename = file_path.stem
        dataset_types = self.config.raw.get('dataset_types', {})
        dtype = 'qa'

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output = item.get('output', '')

            content = f"指令：{instruction}\n问题：{input_text}\n回答：{output}"

            category = self._classify_qa(instruction, input_text)

            metadata = {
                "source": "qa",
                "instruction": instruction,
                "input": input_text,
                "output": output,
                "category": category,
                "chunk_id": f"qa_{idx}",
                "file_path": str(file_path)
            }

            yield DocumentChunk(
                content=content,
                metadata=metadata,
                chunk_id=metadata["chunk_id"],
                source="qa"
            )

    def _classify_qa(self, instruction: str, input_text: str) -> str:
        text = (instruction + input_text).lower()
        keywords = {
            '中医': ['中医', '辨证', '方剂', '舌苔', '脉象', '气血', '阴阳'],
            '西医内科': ['心衰', '肺炎', '高血压', '糖尿病', '冠心病', '脑梗'],
            '外科': ['手术', '切除', '阑尾', '疝气', '胆结石'],
            '妇产科': ['妊娠', '产前', '胎儿', '孕妇', '分娩'],
            '儿科': ['新生儿', '婴儿', '小儿', '发热', '惊厥'],
            '药理': ['用药', '药物', '剂量', '副作用', '相互作用'],
            '医学统计': ['计算', '概率', '统计', '置信区间', 'P值'],
        }

        for cat, kws in keywords.items():
            if any(kw in text for kw in kws):
                return cat
        return '其他'


class EmbeddingModel:
    """Embedding 模型封装"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self):
        from sentence_transformers import SentenceTransformer

        logger.info(f"加载 Embedding 模型: {self.config.embedding_model}")

        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(cache_dir)

        self.model = SentenceTransformer(
            self.config.embedding_model,
            device=self.config.embedding_device,
            cache_folder=str(cache_dir)
        )

        if self.config.embedding_half_precision and self.config.embedding_device == 'cuda':
            self.model.half()
            logger.info("启用 FP16 半精度")

        logger.info(f"模型加载完成，维度: {self.model.get_embedding_dimension()}")

    def encode(self, texts: List[str]) -> List[List[float]]:
        """批量编码，自动分批避免超过模型上限"""
        MAX_ENCODE = 5000
        if len(texts) <= MAX_ENCODE:
            embeddings = self.model.encode(
                texts,
                batch_size=self.config.embedding_batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings.tolist()

        all_embeddings = []
        for start in range(0, len(texts), MAX_ENCODE):
            batch = texts[start:start + MAX_ENCODE]
            logger.info(f"  编码分批: {start+1}-{start+len(batch)}/{len(texts)}")
            emb = self.model.encode(
                batch,
                batch_size=self.config.embedding_batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            all_embeddings.extend(emb.tolist())
        return all_embeddings


class VectorDB:
    """向量数据库封装"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        import chromadb
        from chromadb.config import Settings

        persist_dir = Path(self.config.vectordb_path)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"向量库初始化: {persist_dir}/{self.config.collection_name}")

    def add(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """批量添加"""
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        """清空集合（慎用）"""
        self.client.delete_collection(self.config.collection_name)
        self.collection = self.client.create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )


class RAGProcessor:
    """RAG 数据处理主类"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.state_tracker = FileStateTracker(Path(config.state_file))

        self.embedding_model = EmbeddingModel(config)
        self.vectordb = VectorDB(config)

        self.loaders = {
            '.md': MarkdownLoader(config),
            '.txt': TextLoader(config),
            '.csv': CSVLoader(config),
            '.json': JSONLoader(config),
        }

        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'total_chunks': 0,
            'total_embeddings': 0,
            'errors': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }

    def get_loader(self, file_path: Path) -> Optional[BaseLoader]:
        """根据扩展名获取加载器"""
        return self.loaders.get(file_path.suffix.lower())

    def collect_files(self) -> List[Path]:
        """收集所有待处理文件"""
        files = []
        supported_ext = self.config.raw.get('data_sources', {}).get('supported_extensions',
                                                                   ['.md', '.txt', '.csv', '.json'])

        books_dir = Path(self.config.books_dir)
        if books_dir.exists():
            for ext in supported_ext:
                files.extend(books_dir.rglob(f'*{ext}'))

        datasets_dir = Path(self.config.datasets_dir)
        if datasets_dir.exists():
            for ext in supported_ext:
                files.extend(datasets_dir.rglob(f'*{ext}'))

        return files

    def process_file(self, file_path: Path) -> int:
        """处理单个文件，返回生成的 chunk 数"""
        loader = self.get_loader(file_path)
        if not loader:
            logger.warning(f"无加载器支持: {file_path.suffix}")
            return 0

        chunks = list(loader.load(file_path))
        if not chunks:
            logger.info(f"文件无有效内容: {file_path}")
            return 0

        BATCH = 5000
        all_ids = []
        all_docs = []
        all_embs = []
        all_metas = []

        for start in range(0, len(chunks), BATCH):
            batch = chunks[start:start + BATCH]
            texts = [c.content for c in batch]
            embs = self.embedding_model.encode(texts)
            all_ids.extend([c.chunk_id for c in batch])
            all_docs.extend(texts)
            all_embs.extend(embs)
            all_metas.extend([c.metadata for c in batch])

        # 分批写入向量库
        DB_BATCH = 5000
        for start in range(0, len(all_ids), DB_BATCH):
            self.vectordb.collection.add(
                ids=all_ids[start:start + DB_BATCH],
                documents=all_docs[start:start + DB_BATCH],
                embeddings=all_embs[start:start + DB_BATCH],
                metadatas=all_metas[start:start + DB_BATCH],
            )

        # 备份分块（JSONL）
        self._backup_chunks(chunks, file_path)

        return len(chunks)

    def _backup_chunks(self, chunks: List[DocumentChunk], source_file: Path):
        """备份分块到 JSONL"""
        chunks_dir = Path(self.config.chunks_dir)
        chunks_dir.mkdir(parents=True, exist_ok=True)

        source_type = chunks[0].source if chunks else 'unknown'
        backup_file = chunks_dir / f"{source_type}.jsonl"

        with open(backup_file, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + '\n')

    def run(self, incremental: Optional[bool] = None):
        """运行处理流程"""
        incremental = incremental if incremental is not None else self.config.incremental

        files = self.collect_files()
        self.stats['total_files'] = len(files)

        logger.info(f"发现 {len(files)} 个待处理文件")
        print(get_config_summary(self.config))

        # 过滤增量文件
        if incremental:
            files_to_process = []
            for f in files:
                if self.state_tracker.is_changed(f):
                    files_to_process.append(f)
                else:
                    self.stats['skipped_files'] += 1
            logger.info(f"增量模式: {len(files_to_process)} 个文件需处理, {self.stats['skipped_files']} 个跳过")
        else:
            files_to_process = files

        if not files_to_process:
            logger.info("无需处理文件")
            return self.stats

        # 串行处理（sentence-transformers 内部并行）
        for file_path in tqdm(files_to_process, desc="处理文件"):
            try:
                chunk_count = self.process_file(file_path)
                if chunk_count > 0:
                    self.stats['processed_files'] += 1
                    self.stats['total_chunks'] += chunk_count
                    self.state_tracker.update(file_path, chunk_count)

                    if self.stats['processed_files'] % self.config.checkpoint_interval == 0:
                        self.state_tracker.save()
                        self._save_stats()
            except Exception as e:
                error_msg = f"{file_path}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                if not self.config.raw.get('error_handling', {}).get('continue_on_error', True):
                    raise

        # 最终保存
        self.state_tracker.save()
        self.stats['end_time'] = datetime.now().isoformat()
        self._save_stats()
        self._save_metadata()

        logger.info(f"处理完成: {self.stats}")
        return self.stats

    def _save_stats(self):
        """保存处理统计"""
        stats_file = Path(self.config.raw.get('output', {}).get('stats_file',
                                                                  './storage/rag/processing_stats.json'))
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def _save_metadata(self):
        """保存元数据汇总"""
        metadata_file = Path(self.config.metadata_file)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)

        metadata = {
            'config': {
                'device': self.config.device,
                'embedding_model': self.config.embedding_model,
                'chunk_size': self.config.chunk_size,
                'chunk_overlap': self.config.chunk_overlap,
                'vectordb_path': self.config.vectordb_path,
                'collection_name': self.config.collection_name,
            },
            'stats': self.stats,
            'vectordb_count': self.vectordb.count(),
            'generated_at': datetime.now().isoformat()
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"元数据已保存: {metadata_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="RAG 数据处理脚本")
    parser.add_argument('--hardware', choices=['auto', 'r5_5600u', 'rtx_4060'],
                       default='auto', help='硬件配置预设')
    parser.add_argument('--config-dir', type=str, default='../rag-shared/config', help='配置目录')
    parser.add_argument('--incremental', action='store_true', default=True, help='增量更新')
    parser.add_argument('--full', action='store_true', help='全量重建（忽略增量）')
    parser.add_argument('--reset-db', action='store_true', help='重置向量库')
    parser.add_argument('--stats-only', action='store_true', help='仅显示统计')

    args = parser.parse_args()

    config = load_config(args.hardware, Path(args.config_dir))

    processor = RAGProcessor(config)

    if args.reset_db:
        confirm = input("确定要重置向量库吗？这将删除所有数据 (y/N): ")
        if confirm.lower() == 'y':
            processor.vectordb.reset()
            logger.info("向量库已重置")
        return

    if args.stats_only:
        print(f"向量库文档数: {processor.vectordb.count()}")
        return

    incremental = not args.full
    stats = processor.run(incremental=incremental)

    print("\n" + "=" * 50)
    print("处理完成统计:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  已处理: {stats['processed_files']}")
    print(f"  跳过: {stats['skipped_files']}")
    print(f"  总分块: {stats['total_chunks']}")
    print(f"  向量库总数: {processor.vectordb.count()}")
    print(f"  错误数: {len(stats['errors'])}")
    if stats['errors']:
        print("  错误详情:")
        for e in stats['errors'][:5]:
            print(f"    - {e}")
    print("=" * 50)


if __name__ == "__main__":
    main()