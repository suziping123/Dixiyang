"""向量数据库封装（ChromaDB）"""
import logging
from pathlib import Path
from typing import List

from .config import RAGConfig
from .loaders import DocumentChunk

logger = logging.getLogger(__name__)


class VectorDB:
    """封装 ChromaDB PersistentClient，提供向量存储与检索"""

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
