"""Embedding 模型封装（sentence-transformers）"""
import os
import logging
from pathlib import Path
from typing import List

from .config import RAGConfig

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """封装 sentence-transformers 模型，支持 GPU/CPU、FP16/FP32"""

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
