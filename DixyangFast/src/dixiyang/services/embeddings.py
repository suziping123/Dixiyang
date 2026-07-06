import logging
import os
from pathlib import Path
from typing import List

from langchain_core.embeddings import Embeddings

log = logging.getLogger(__name__)


class DixiyangEmbeddings(Embeddings):
    def __init__(self):
        self._model = None

    def _get_embedding(self, text: str) -> list[float]:
        try:
            import httpx
            resp = httpx.post(
                "http://localhost:8085/api/rag/embed",
                json={"text": text},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("embedding")
        except Exception:
            pass

        try:
            if self._model is None:
                model_path = os.getenv(
                    "RAG_EMBEDDING_MODEL",
                    str(Path(__file__).parent.parent.parent.parent / "models" / "bge-m3"),
                )
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(model_path, device="cpu")
            emb = self._model.encode([text], normalize_embeddings=True).tolist()[0]
            return emb
        except Exception as e:
            raise RuntimeError(f"Embedding 生成失败: {e}") from e

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_embedding(t) for t in texts]
