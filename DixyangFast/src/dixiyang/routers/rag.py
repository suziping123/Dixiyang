import os
from typing import Optional

from fastapi import APIRouter, Depends, Query
from langchain_chroma import Chroma
from pydantic import BaseModel

from ..services.embeddings import DixiyangEmbeddings
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/rag", tags=["RAG 向量库"])

_embeddings = DixiyangEmbeddings()
_vectorstore: Chroma | None = None


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
        return Result.success(data={
            "total_collections": 1,
            "total_documents": count,
            "embedding_model": "BAAI/bge-m3",
            "embedding_dimension": 1024,
            "collection_details": [
                {
                    "name": vectorstore._collection.name,
                    "count": count,
                    "metadata": vectorstore._collection.metadata,
                }
            ],
            "connected": True,
        })
    except Exception as e:
        return Result.error(f"获取统计失败: {e}")


@router.get("/count")
async def get_count(user_id: int = Depends(get_current_user_id)):
    try:
        vectorstore = get_vectorstore()
        return Result.success(data=vectorstore._collection.count())
    except Exception as e:
        return Result.error(f"获取计数失败: {e}")


@router.get("/documents")
async def get_documents(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        user_id: int = Depends(get_current_user_id)):
    try:
        vectorstore = get_vectorstore()
        offset = (page - 1) * page_size
        results = vectorstore.get(limit=page_size, offset=offset, include=["documents", "metadatas"])
        return Result.success(data={
            "ids": results.get("ids", []),
            "documents": results.get("documents", []),
            "metadatas": results.get("metadatas", []),
            "page": page,
            "page_size": page_size,
        })
    except Exception as e:
        return Result.error(f"获取文档失败: {e}")


@router.post("/search")
async def search(query: str = Query(..., description="搜索关键词"),
                 topK: int = Query(5, ge=1, le=50, description="返回条数"),
                 user_id: int = Depends(get_current_user_id)):
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search_with_score(query, k=topK)
        items = []
        for doc, score in results:
            items.append({
                "id": doc.metadata.get("id", ""),
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": 1.0 - score,
            })
        return Result.success(data={"query": query, "results": items})
    except Exception as e:
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
