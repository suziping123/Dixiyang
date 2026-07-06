import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "rag-shared" / "python"))

router = APIRouter(prefix="/rag", tags=["RAG 向量库"])


def get_chroma_collection():
    import chromadb
    from chromadb.config import Settings

    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./storage/vectordb_4060")
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "dixiyang_knowledge")

    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(anonymized_telemetry=False)
    )
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    model_path = os.getenv("RAG_EMBEDDING_MODEL", str(Path(__file__).parent.parent.parent.parent / "models" / "bge-m3"))
    device = "cuda" if os.getenv("RAG_DEVICE", "cuda") == "cuda" else "cpu"
    model = SentenceTransformer(model_path, device=device)
    if device == "cuda":
        model.half()
    return model


@router.get("/stats")
async def get_stats():
    try:
        collection = get_chroma_collection()
        count = collection.count()
        return {
            "total_collections": 1,
            "total_documents": count,
            "embedding_model": "BAAI/bge-m3",
            "embedding_dimension": 1024,
            "collection_details": [
                {
                    "name": collection.name,
                    "count": count,
                    "metadata": collection.metadata,
                }
            ],
            "connected": True,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/count")
async def get_count():
    try:
        collection = get_chroma_collection()
        return collection.count()
    except Exception as e:
        return {"error": str(e)}


@router.get("/documents")
async def get_documents(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    try:
        collection = get_chroma_collection()
        offset = (page - 1) * page_size
        results = collection.get(limit=page_size, offset=offset, include=["documents", "metadatas"])
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
        collection = get_chroma_collection()
        model = get_embedding_model()
        query_emb = model.encode([req.query], normalize_embeddings=True).tolist()
        results = collection.query(
            query_embeddings=query_emb,
            n_results=req.topK,
            include=["documents", "metadatas", "distances"],
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        items = []
        for i in range(len(docs)):
            items.append({
                "id": ids[i],
                "content": docs[i],
                "metadata": metas[i] if i < len(metas) else None,
                "score": 1.0 - dists[i] if i < len(dists) else None,
            })
        return {"query": req.query, "results": items}
    except Exception as e:
        return {"error": str(e)}


class EmbedRequest(BaseModel):
    text: str


@router.post("/embed")
async def embed_text(req: EmbedRequest):
    try:
        model = get_embedding_model()
        vec = model.encode([req.text], normalize_embeddings=True).tolist()[0]
        return {"embedding": vec, "dimension": len(vec)}
    except Exception as e:
        return {"error": str(e)}
