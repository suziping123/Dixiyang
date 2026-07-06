"""RAG 数据处理主流程编排"""
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from tqdm import tqdm

from .config import load_config, get_config_summary, RAGConfig
from .tracker import FileStateTracker
from .loaders import DocumentChunk, MarkdownLoader, CSVLoader, TextLoader, JSONLoader
from .embeddings import EmbeddingModel
from .vectordb import VectorDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGProcessor:
    """RAG 数据处理主类：编排文件收集 → 加载切分 → Embedding → 写入向量库"""

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

    def get_loader(self, file_path: Path):
        return self.loaders.get(file_path.suffix.lower())

    def collect_files(self) -> List[Path]:
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

        # 分批编码
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

        self._backup_chunks(chunks, file_path)
        return len(chunks)

    def _backup_chunks(self, chunks: List[DocumentChunk], source_file: Path):
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

        self.state_tracker.save()
        self.stats['end_time'] = datetime.now().isoformat()
        self._save_stats()
        self._save_metadata()

        logger.info(f"处理完成: {self.stats}")
        return self.stats

    def _save_stats(self):
        stats_file = Path(self.config.raw.get('output', {}).get('stats_file',
                                                                  './storage/rag/processing_stats.json'))
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def _save_metadata(self):
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
