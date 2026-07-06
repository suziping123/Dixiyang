"""
知识检索工具 — 封装 LangChain Chroma 语义检索，可供 LLM function calling 调用
对齐 Spring 版 KnowledgeSearchTool.java
"""

import logging
import os
import time

from langchain_chroma import Chroma

from .embeddings import DixiyangEmbeddings

log = logging.getLogger(__name__)

RERANKER_URL = os.getenv("RERANKER_URL", "http://localhost:8085")

_embeddings = DixiyangEmbeddings()
_vectorstore: Chroma | None = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./storage/vectordb_4060")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "dixiyang_knowledge")
        _vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=_embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def _rerank_results(query: str, documents: list[str]) -> list[int]:
    """调用 reranker 精排，返回按相关性降序排列的原始索引列表"""
    if len(documents) <= 1:
        return list(range(len(documents)))
    try:
        import httpx
        resp = httpx.post(
            f"{RERANKER_URL}/api/rag/rerank",
            json={"query": query, "documents": documents, "top_k": len(documents)},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            doc_to_idx = {d: i for i, d in enumerate(documents)}
            return [doc_to_idx[r["content"]] for r in results if r["content"] in doc_to_idx]
    except Exception as e:
        log.warning("Reranker 调用失败，回退到原始顺序: %s", e)
    return list(range(len(documents)))


def knowledge_search(query: str, top_k: int = 5, doc_type: str | None = None) -> str:
    """
    搜索小说知识库（角色/世界观/大纲/参考资料）。

    Args:
        query: 自然语言查询，如"主角的性格特点"
        top_k: 返回条数，默认 5
        doc_type: 可选类型过滤：character/worldbuilding/outline/reference

    Returns:
        格式化的检索结果文本
    """
    start = time.time()
    try:
        vectorstore = _get_vectorstore()

        # 宽召回：多取 4 倍候选，供 reranker 精排
        recall_k = min(top_k * 4, 100)
        results = vectorstore.similarity_search_with_score(query, k=recall_k)

        # 构建候选文档（带元数据）
        candidates: list[dict] = []
        for doc, _score in results:
            meta = doc.metadata
            if doc_type and not _matches_type(meta, doc_type):
                continue
            source = meta.get("book_title") or meta.get("source") or ""
            candidates.append({"doc": doc.page_content, "source": source})

        if not candidates:
            elapsed = int((time.time() - start) * 1000)
            log.info("知识检索: query=%s, type=%s, 结果数=0, 耗时=%dms", query, doc_type, elapsed)
            return "未检索到相关资料"

        # 调用 reranker 精排
        reranked = _rerank_results(query, [c["doc"] for c in candidates])

        # 按 rerank 顺序取 top_k
        filtered: list[str] = []
        for idx in reranked:
            c = candidates[idx]
            prefix = f"[{c['source']}] " if c["source"] else ""
            filtered.append(f"{prefix}{c['doc']}")

        filtered = filtered[:top_k]

        elapsed = int((time.time() - start) * 1000)
        log.info("知识检索: query=%s, type=%s, 候选数=%d, 结果数=%d, 耗时=%dms",
                 query, doc_type, len(candidates), len(filtered), elapsed)

        return "\n---\n".join(filtered)

    except Exception as e:
        log.error("知识检索失败: query=%s, %s", query, e)
        return f"检索失败: {e}"


def _matches_type(metadata: dict, doc_type: str) -> bool:
    """检查文档类型是否匹配"""
    meta_type = metadata.get("type")
    if meta_type:
        return doc_type.lower() == str(meta_type).lower()
    source = metadata.get("source", "")
    return doc_type.lower() in str(source).lower()


# ==================== OpenAI Function Calling 工具定义 ====================

KNOWLEDGE_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "knowledge_search",
        "description": (
            "搜索小说知识库（角色/世界观/大纲/参考资料）。"
            "当你需要查阅设定细节、角色信息、世界观设定、故事大纲时调用此工具。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "自然语言查询，如'主角的性格特点'、'世界观设定'等",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回条数，默认 5",
                    "default": 5,
                },
                "doc_type": {
                    "type": "string",
                    "description": "可选类型过滤：character/worldbuilding/outline/reference",
                    "enum": ["character", "worldbuilding", "outline", "reference"],
                },
            },
            "required": ["query"],
        },
    },
}
