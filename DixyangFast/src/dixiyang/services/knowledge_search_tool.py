import logging
import os
import time

from langchain_chroma import Chroma
from langchain_core.tools import tool

from .embeddings import DixiyangEmbeddings

log = logging.getLogger(__name__)

_embeddings = DixiyangEmbeddings()
_vectorstore: Chroma | None = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "dixiyang_knowledge")
        _vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=_embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def _rerank_results(query: str, documents: list[str]) -> list[int]:
    reranker_url = os.getenv("RERANKER_URL", "http://localhost:8085")
    try:
        import httpx
        resp = httpx.post(
            f"{reranker_url}/api/rerank",
            json={"query": query, "documents": documents},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            doc_to_idx = {d: i for i, d in enumerate(documents)}
            return [doc_to_idx[r["content"]] for r in results if r["content"] in doc_to_idx]
    except Exception as e:
        log.warning("Reranker 不可用，使用向量检索原始排序: %s", e)
    return list(range(len(documents)))


def _matches_type(metadata: dict, doc_type: str) -> bool:
    meta_type = metadata.get("type")
    if meta_type:
        return doc_type.lower() == str(meta_type).lower()
    source = metadata.get("source", "")
    return doc_type.lower() in str(source).lower()


@tool
def knowledge_search(query: str, top_k: int = 5, doc_type: str | None = None) -> str:
    """搜索小说知识库（角色/世界观/大纲/参考资料）。当你需要查阅设定细节、角色信息、世界观设定、故事大纲时调用此工具。"""
    start = time.time()
    try:
        vectorstore = _get_vectorstore()
        recall_k = min(top_k * 4, 100)
        results = vectorstore.similarity_search_with_score(query, k=recall_k)

        candidates = []
        for doc, _score in results:
            meta = doc.metadata
            if doc_type and not _matches_type(meta, doc_type):
                continue
            source = meta.get("book_title") or meta.get("source") or ""
            candidates.append({"doc": doc.page_content, "source": source})

        if not candidates:
            return "未找到相关结果"

        # 重排序
        doc_texts = [c["doc"] for c in candidates]
        ranked = _rerank_results(query, doc_texts)
        reranked = [candidates[i] for i in ranked[:top_k]]

        lines = []
        for i, c in enumerate(reranked, 1):
            source_info = f"（来源：{c['source']}）" if c["source"] else ""
            lines.append(f"{i}. {c['doc'][:500]}{source_info}")
        elapsed = int((time.time() - start) * 1000)
        result = "\n\n".join(lines)
        log.info("knowledge_search(query=%s, top_k=%s) 返回 %s 条，耗时 %sms", query, top_k, len(reranked), elapsed)
        return result
    except Exception as e:
        log.error("knowledge_search 检索失败: %s", e)
        return f"检索失败: {e}"
