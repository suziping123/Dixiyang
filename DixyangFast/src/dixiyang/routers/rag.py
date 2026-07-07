import logging
import os
from collections import Counter
from typing import Optional

from fastapi import APIRouter, Depends, Query
from langchain_chroma import Chroma
from pydantic import BaseModel

from ..services.embeddings import DixiyangEmbeddings
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/rag", tags=["RAG 向量库"])

log = logging.getLogger(__name__)

_embeddings = DixiyangEmbeddings()
_vectorstore: Chroma | None = None

RERANKER_URL = os.getenv("RERANKER_URL", "http://localhost:8085")


def get_vectorstore() -> Chroma:
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


@router.get("/stats")
async def get_stats(user_id: int = Depends(get_current_user_id)):
    try:
        vectorstore = get_vectorstore()
        count = vectorstore._collection.count()

        source_counts = Counter()
        category_counts = Counter()
        book_counts = Counter()

        if count > 0:
            limit = min(count, 5000)
            results = vectorstore.get(limit=limit, include=["metadatas"])
            for meta in results.get("metadatas", []):
                if meta:
                    source = meta.get("source", "unknown")
                    source_counts[source] += 1
                    cat = meta.get("category") or source
                    category_counts[cat] += 1
                    book = (
                        meta.get("book_title")
                        or meta.get("company")
                        or meta.get("file")
                        or "unknown"
                    )
                    book_counts[book] += 1

        return Result.success(
            data={
                "total_collections": 1,
                "total_documents": count,
                "embedding_model": "BAAI/bge-m3",
                "embedding_dimension": 1024,
                "source_distribution": dict(source_counts.most_common()),
                "category_distribution": dict(category_counts.most_common(20)),
                "book_distribution": dict(book_counts.most_common(30)),
                "collection_details": [
                    {
                        "name": vectorstore._collection.name,
                        "count": count,
                        "metadata": vectorstore._collection.metadata,
                    }
                ],
                "connected": True,
            }
        )
    except Exception as e:
        log.error("RAG stats 失败: %s", e)
        return Result.error(f"获取统计失败: {e}")


@router.get("/count")
async def get_count(user_id: int = Depends(get_current_user_id)):
    try:
        vectorstore = get_vectorstore()
        return Result.success(data=vectorstore._collection.count())
    except Exception as e:
        return Result.error(f"获取计数失败: {e}")


@router.get("/documents")
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None, description="按来源筛选"),
    user_id: int = Depends(get_current_user_id),
):
    try:
        vectorstore = get_vectorstore()
        offset = (page - 1) * page_size

        where = {"source": source} if source else None
        results = vectorstore.get(
            limit=page_size,
            offset=offset,
            where=where,
            include=["documents", "metadatas"],
        )

        ids = results.get("ids", [])
        docs = results.get("documents", [])
        metas = results.get("metadatas", [])

        # 获取筛选后的总数
        if where:
            total = len(vectorstore._collection.get(where=where, include=[])["ids"])
        else:
            total = vectorstore._collection.count()

        return Result.success(
            data={
                "ids": ids,
                "documents": docs,
                "metadatas": metas,
                "page": page,
                "page_size": page_size,
                "total": total,
            }
        )
    except Exception as e:
        log.error("RAG documents 失败: %s", e)
        return Result.error(f"获取文档失败: {e}")


async def _rerank(query: str, documents: list[str]) -> list[int]:
    """调用 Python RAG 服务的 reranker 精排，返回排序后的索引"""
    try:
        import httpx

        resp = httpx.post(
            f"{RERANKER_URL}/api/rag/rerank",
            json={
                "query": query,
                "documents": documents,
                "top_k": len(documents),
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                doc_to_idx = {d: i for i, d in enumerate(documents)}
                return [
                    doc_to_idx[r["content"]]
                    for r in results
                    if r["content"] in doc_to_idx
                ]
    except Exception as e:
        log.warning("Reranker 不可用，使用原始排序: %s", e)
    return list(range(len(documents)))


@router.post("/search")
async def search(
    query: str = Query(..., description="搜索关键词"),
    topK: int = Query(5, ge=1, le=50, description="返回条数"),
    source_filter: Optional[str] = Query(None, description="按来源筛选"),
    user_id: int = Depends(get_current_user_id),
):
    try:
        vectorstore = get_vectorstore()

        recall_k = min(topK * 4, 100)
        filter_dict = {"source": source_filter} if source_filter else None
        results = vectorstore.similarity_search_with_score(
            query, k=recall_k, filter=filter_dict
        )

        candidates = [
            (doc.page_content, 1.0 - score, doc.metadata) for doc, score in results
        ]

        if not candidates:
            return Result.success(data={"query": query, "results": [], "total": 0})

        doc_texts = [c[0] for c in candidates]
        reranked_indices = await _rerank(query, doc_texts)
        reranked = [candidates[i] for i in reranked_indices[:topK]]

        items = []
        for content, score, meta in reranked:
            items.append(
                {
                    "id": meta.get("chunk_id", meta.get("id", "")),
                    "content": content[:500],
                    "metadata": meta,
                    "score": round(score, 4),
                }
            )

        return Result.success(data={"query": query, "results": items, "total": len(items)})
    except Exception as e:
        log.error("RAG search 失败: %s", e)
        return Result.error(f"搜索失败: {e}")


class EmbedRequest(BaseModel):
    text: str


@router.post("/embed")
async def embed_text(req: EmbedRequest):
    try:
        vec = _embeddings.embed_query(req.text)
        return Result.success(data={"embedding": vec, "dimension": len(vec)})
    except Exception as e:
        return Result.error(f"嵌入失败: {e}")
