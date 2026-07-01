"""
RAG Embedding 服务
为 Java 后端提供向量化接口，同时代理 ChromaDB 查询

启动方式:
  1. 先启动 ChromaDB: chroma run --path storage/vectordb_4060 --port 8000
  2. 再启动本服务: python python_api/main.py
  3. 或一键启动: python python_api/start.py
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

# 加载 embedding 模型
MODEL_NAME = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMADB_PORT", "8000"))
COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "dixiyang_knowledge")

_model = None
_chroma_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载模型"""
    global _model
    from sentence_transformers import SentenceTransformer

    cache_dir = str(Path(__file__).parent.parent / "models" / "cache")
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    # 优先使用本地已下载的模型路径
    local_model_path = str(Path(__file__).parent.parent / "models" / "bge-m3")
    model_path = local_model_path if Path(local_model_path).exists() else MODEL_NAME

    print(f"加载 Embedding 模型: {model_path} ...")
    _model = SentenceTransformer(model_path, cache_folder=cache_dir)
    print(f"模型加载完成，维度: {_model.get_sentence_embedding_dimension()}")
    yield


app = FastAPI(title="RAG Embedding Service", lifespan=lifespan)


class EmbedRequest(BaseModel):
    text: str


class EmbedBatchRequest(BaseModel):
    texts: list[str]


@app.post("/api/rag/embed")
async def embed(req: EmbedRequest):
    """单条文本向量化"""
    emb = _model.encode([req.text], normalize_embeddings=True)
    return {"embedding": emb[0].tolist()}


@app.post("/api/rag/embed/batch")
async def embed_batch(req: EmbedBatchRequest):
    """批量文本向量化"""
    embs = _model.encode(req.texts, normalize_embeddings=True)
    return {"embeddings": embs.tolist()}


@app.get("/api/rag/health")
async def health():
    """健康检查"""
    chroma_ok = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{_chroma_url}/api/v2/heartbeat", timeout=3)
            chroma_ok = resp.status_code == 200
    except Exception:
        pass
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "dimension": _model.get_sentence_embedding_dimension() if _model else 0,
        "chromadb_connected": chroma_ok,
    }


# ========== 代理 ChromaDB 接口（供 Java RagService 调用） ==========


@app.get("/api/v2/heartbeat")
async def chroma_heartbeat():
    """代理 ChromaDB heartbeat"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_chroma_url}/api/v2/heartbeat")
        return resp.json()


@app.get("/api/v2/tenants/{tenant}/databases/{database}/collections")
async def chroma_list_collections(tenant: str, database: str):
    """代理列出 collections"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections"
        )
        return resp.json()


@app.post("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/count")
async def chroma_count(tenant: str, database: str, col_id: str):
    """代理 collection count"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/count"
        )
        return resp.json()


@app.post("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/query")
async def chroma_query(tenant: str, database: str, col_id: str, body: dict):
    """代理 collection query（向量检索）"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/query",
            json=body,
        )
        return resp.json()


@app.post("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/get")
async def chroma_get(tenant: str, database: str, col_id: str, body: dict):
    """代理 collection get"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/get",
            json=body,
        )
        return resp.json()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("RAG_SERVICE_PORT", "8085"))
    print(f"启动 RAG Embedding 服务: http://0.0.0.0:{port}")
    print(f"  Embedding 模型: {MODEL_NAME}")
    print(f"  ChromaDB 地址: {_chroma_url}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
