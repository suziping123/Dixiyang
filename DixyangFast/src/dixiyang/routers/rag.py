import os
from typing import Optional

from fastapi import APIRouter, Query
from langchain_chroma import Chroma
from pydantic import BaseModel

from ..services.embeddings import DixiyangEmbeddings

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
async def get_stats():
    try:
        vectorstore = get_vectorstore()
        ids = vectorstore.get()["ids"]
        return {
            "total_collections": 1,
            "total_documents": len(ids),
            "embedding_model": "BAAI/bge-m3",
            "embedding_dimension": 1024,
            "collection_details": [
                {
                    "name": vectorstore._collection.name,
                    "count": len(ids),
                    "metadata": vectorstore._collection.metadata,
                }
            ],
            "connected": True,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/count")
async def get_count():
    try:
        vectorstore = get_vectorstore()
        return len(vectorstore.get()["ids"])
    except Exception as e:
        return {"error": str(e)}


@router.get("/documents")
async def get_documents(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    try:
        vectorstore = get_vectorstore()
        offset = (page - 1) * page_size
        results = vectorstore.get(limit=page_size, offset=offset, include=["documents", "metadatas"])
        return {
            "ids": results.get("ids", []),
            "documents": results.get("documents", []),
            "metadatas": results.get("metadatas", []),
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        return {"error": str(e)}


class SearchRequest(BaseModel):
    query: str
    topK: int = 5


@router.post("/search")
async def search(req: SearchRequest):
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search_with_score(req.query, k=req.topK)
        items = []
        for doc, score in results:
            items.append({
                "id": doc.metadata.get("id", ""),
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": 1.0 - score,
            })
        return {"query": req.query, "results": items}
    except Exception as e:
        return {"error": str(e)}


class EmbedRequest(BaseModel):
    text: str


@router.post("/embed")
async def embed_text(req: EmbedRequest):
    try:
        vec = _embeddings.embed_query(req.text)
        return {"embedding": vec, "dimension": len(vec)}
    except Exception as e:
        return {"error": str(e)}
