"""
RAG Embedding 服务
为 Java 后端提供向量化接口，同时代理 ChromaDB 查询

启动方式:
  1. 先启动 ChromaDB: chroma run --path storage/vectordb_4060 --port 8000
  2. 再启动本服务: python python_api/main.py
  3. 或一键启动: bash start_rag.sh

前端可视化: http://localhost:8085/rag
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from collections import Counter

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 加载 embedding 模型
MODEL_NAME = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMADB_PORT", "8000"))
COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "dixiyang_knowledge")

_model = None
_reranker = None
_chroma_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载模型"""
    global _model, _reranker
    from sentence_transformers import SentenceTransformer

    cache_dir = str(Path(__file__).parent.parent / "models" / "cache")
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    local_model_path = str(Path(__file__).parent.parent / "models" / "bge-m3")
    model_path = local_model_path if Path(local_model_path).exists() else MODEL_NAME

    print(f"加载 Embedding 模型: {model_path} ...")
    _model = SentenceTransformer(model_path, cache_folder=cache_dir)
    print(f"模型加载完成，维度: {_model.get_sentence_embedding_dimension()}")

    # 加载 Reranker 模型（可选）
    use_reranker = os.getenv("RAG_USE_RERANKER", "true").lower() == "true"
    if use_reranker:
        reranker_path = os.getenv("RAG_RERANKER_MODEL", "/home/lijiajia/models/bge-reranker-large")
        if Path(reranker_path).exists():
            try:
                from FlagEmbedding import FlagReranker
                print(f"加载 Reranker 模型: {reranker_path} ...")
                _reranker = FlagReranker(reranker_path, use_fp16=False)
                print("Reranker 模型加载完成")
            except Exception as e:
                print(f"Reranker 加载失败: {e}")
        else:
            print(f"Reranker 模型不存在: {reranker_path}，跳过")

    yield


app = FastAPI(title="RAG Service", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class EmbedRequest(BaseModel):
    text: str

class EmbedBatchRequest(BaseModel):
    texts: list[str]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_filter: str | None = None

class RerankRequest(BaseModel):
    query: str
    documents: list[str]
    top_k: int = 5


# ========== Embedding 接口 ==========

@app.post("/api/rag/embed")
async def embed(req: EmbedRequest):
    emb = _model.encode([req.text], normalize_embeddings=True)
    return {"embedding": emb[0].tolist()}

@app.post("/api/rag/embed/batch")
async def embed_batch(req: EmbedBatchRequest):
    embs = _model.encode(req.texts, normalize_embeddings=True)
    return {"embeddings": embs.tolist()}

@app.post("/api/rag/rerank")
async def rerank(req: RerankRequest):
    """重排序：对候选文档按 (query, doc) 相关性精排"""
    if _reranker is None:
        return {"error": "Reranker 模型未加载", "results": []}
    if not req.documents:
        return {"results": []}

    pairs = [[req.query, doc] for doc in req.documents]
    scores = _reranker.compute_score(pairs)
    if isinstance(scores, (int, float)):
        scores = [scores]

    ranked = sorted(zip(req.documents, scores), key=lambda x: x[1], reverse=True)
    return {
        "results": [
            {"content": d, "score": round(float(s), 4)}
            for d, s in ranked[:req.top_k]
        ]
    }

@app.get("/api/rag/health")
async def health():
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


# ========== RAG 可视化 API ==========

COLLECTIONS_URL = f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections"


async def _get_collection():
    """获取 ChromaDB collection (name, id)"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(COLLECTIONS_URL)
        cols = resp.json()
        if not cols:
            return None, None
        col = next((c for c in cols if c["name"] == COLLECTION_NAME), cols[0] if cols else None)
        if not col:
            return None, None
        return col["name"], col["id"]


@app.get("/api/rag/stats")
async def rag_stats():
    """向量库统计"""
    # 先检查 ChromaDB 是否可达
    chroma_ok = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{_chroma_url}/api/v2/heartbeat", timeout=3)
            chroma_ok = resp.status_code == 200
    except Exception:
        pass

    if not chroma_ok:
        return {"error": "ChromaDB 无法连接", "connected": False}

    col_name, col_id = await _get_collection()
    if not col_id:
        return {
            "connected": True,
            "collection_name": None,
            "total_documents": 0,
            "source_distribution": {},
            "category_distribution": {},
            "book_distribution": {},
            "embedding_model": MODEL_NAME,
            "embedding_dimension": _model.get_sentence_embedding_dimension() if _model else 0,
            "message": "ChromaDB 已连接，但集合为空。请先在 Windows 上构建向量库并传到此目录。",
        }

    total = 0
    source_counts = Counter()
    category_counts = Counter()
    book_counts = Counter()

    async with httpx.AsyncClient() as client:
        try:
            count_resp = await client.get(
                f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{col_id}/count"
            )
            total = count_resp.json()
        except Exception:
            total = 0

        if total > 0:
            try:
                get_resp = await client.post(
                    f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{col_id}/get",
                    json={"limit": min(total, 5000), "include": ["metadatas"]}
                )
                data = get_resp.json()
                for meta in data.get("metadatas", []):
                    if meta:
                        source_counts[meta.get("source", "unknown")] += 1
                        category_counts[meta.get("category", "unknown")] += 1
                        book = meta.get("book_title") or meta.get("company") or meta.get("file") or "unknown"
                        book_counts[book] += 1
            except Exception:
                pass

    return {
        "connected": True,
        "collection_name": col_name,
        "total_documents": total,
        "source_distribution": dict(source_counts.most_common()),
        "category_distribution": dict(category_counts.most_common(20)),
        "book_distribution": dict(book_counts.most_common(30)),
        "embedding_model": MODEL_NAME,
        "embedding_dimension": _model.get_sentence_embedding_dimension() if _model else 0,
    }


@app.post("/api/rag/search")
async def rag_search(req: SearchRequest):
    """检索测试（宽召回 + reranker 精排）"""
    col_name, col_id = await _get_collection()
    if not col_id:
        return {"error": "集合不存在"}

    emb = _model.encode([req.query], normalize_embeddings=True).tolist()

    where = None
    if req.source_filter:
        where = {"source": req.source_filter}

    # 宽召回：多取 4 倍候选
    recall_k = min(req.top_k * 4, 100)
    body = {
        "query_embeddings": emb,
        "n_results": recall_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        body["where"] = where

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{col_id}/query",
            json=body,
        )
        data = resp.json()
        results = []
        doc_texts = []
        if data.get("documents") and data["documents"][0]:
            docs = data["documents"][0]
            metas = data["metadatas"][0] if data.get("metadatas") else [None] * len(docs)
            dists = data["distances"][0] if data.get("distances") else [0] * len(docs)
            ids = data["ids"][0] if data.get("ids") else [""] * len(docs)
            for i in range(len(docs)):
                meta = metas[i] if i < len(metas) else {}
                doc_texts.append(docs[i])
                results.append({
                    "id": ids[i] if i < len(ids) else "",
                    "content": docs[i][:500],
                    "metadata": meta,
                    "score": round(1.0 - (dists[i] if dists[i] else 0), 4),
                })

        # 调用 reranker 精排
        if results and _reranker is not None:
            pairs = [[req.query, doc] for doc in doc_texts]
            scores = _reranker.compute_score(pairs)
            if isinstance(scores, (int, float)):
                scores = [scores]

            # 按 rerank 分数降序排列
            ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            results = [results[i] for i in ranked_indices[:req.top_k]]
            for r in results:
                r["reranked"] = True

        return {"query": req.query, "results": results, "total": len(results)}


@app.get("/api/rag/documents")
async def rag_documents(page: int = 1, page_size: int = 20, source: str | None = None):
    """浏览文档列表"""
    col_name, col_id = await _get_collection()
    if not col_id:
        return {"error": "集合不存在"}

    where = {"source": source} if source else None
    body = {
        "limit": page_size,
        "offset": (page - 1) * page_size,
        "include": ["documents", "metadatas", "ids"],
    }
    if where:
        body["where"] = where

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{col_id}/get",
            json=body,
        )
        data = resp.json()
        docs = data.get("documents", [])
        metas = data.get("metadatas", [])
        ids = data.get("ids", [])
        items = []
        for i in range(len(docs)):
            meta = metas[i] if i < len(metas) else {}
            items.append({
                "id": ids[i] if i < len(ids) else "",
                "content": docs[i][:300] + ("..." if len(docs[i]) > 300 else ""),
                "metadata": meta,
            })

        count_resp = await client.get(
            f"{_chroma_url}/api/v2/tenants/default_tenant/databases/default_database/collections/{col_id}/count"
        )
        total = count_resp.json()

        return {"documents": items, "total": total, "page": page, "page_size": page_size}


# ========== 前端可视化页面 ==========

@app.get("/rag", response_class=HTMLResponse)
async def rag_ui():
    return RAG_UI_HTML


RAG_UI_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RAG 向量库可视化</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, 'Segoe UI', sans-serif; background:#0f1117; color:#e0e0e0; }
.header { background:linear-gradient(135deg,#1a1b2e,#2d1b4e); padding:20px 30px; border-bottom:1px solid #333; }
.header h1 { font-size:22px; color:#fff; }
.header .sub { color:#888; font-size:13px; margin-top:4px; }
.container { max-width:1200px; margin:0 auto; padding:20px; }
.tabs { display:flex; gap:8px; margin-bottom:20px; }
.tab { padding:8px 20px; border-radius:8px; cursor:pointer; background:#1e1f2e; border:1px solid #333; color:#aaa; font-size:14px; transition:all .2s; }
.tab.active { background:#6c5ce7; color:#fff; border-color:#6c5ce7; }
.tab:hover { background:#2d2e42; }
.panel { display:none; }
.panel.active { display:block; }
.card { background:#1a1b2e; border:1px solid #2a2b3e; border-radius:12px; padding:20px; margin-bottom:16px; }
.card h3 { color:#a78bfa; margin-bottom:12px; font-size:15px; }
.stat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; }
.stat-box { background:#12131f; border-radius:8px; padding:16px; text-align:center; }
.stat-num { font-size:28px; font-weight:700; color:#6c5ce7; }
.stat-label { font-size:12px; color:#888; margin-top:4px; }
.bar-chart { margin-top:12px; }
.bar-row { display:flex; align-items:center; margin:4px 0; font-size:13px; }
.bar-label { width:180px; text-align:right; padding-right:10px; color:#aaa; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bar-fill { height:22px; background:linear-gradient(90deg,#6c5ce7,#a78bfa); border-radius:4px; min-width:2px; transition:width .3s; }
.bar-count { margin-left:8px; color:#888; min-width:40px; }
.search-box { display:flex; gap:8px; margin-bottom:16px; }
.search-box input { flex:1; padding:10px 14px; border-radius:8px; border:1px solid #333; background:#12131f; color:#fff; font-size:14px; outline:none; }
.search-box input:focus { border-color:#6c5ce7; }
.search-box select { padding:10px; border-radius:8px; border:1px solid #333; background:#12131f; color:#fff; font-size:13px; }
.btn { padding:10px 20px; border-radius:8px; border:none; background:#6c5ce7; color:#fff; cursor:pointer; font-size:14px; }
.btn:hover { background:#5a4bd1; }
.result-item { background:#12131f; border:1px solid #2a2b3e; border-radius:8px; padding:14px; margin-bottom:10px; }
.result-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.result-score { background:#6c5ce7; color:#fff; padding:2px 10px; border-radius:12px; font-size:12px; }
.result-meta { color:#888; font-size:12px; }
.result-content { color:#ccc; font-size:13px; line-height:1.6; white-space:pre-wrap; word-break:break-all; }
.doc-table { width:100%; border-collapse:collapse; font-size:13px; }
.doc-table th { text-align:left; padding:8px; border-bottom:1px solid #333; color:#a78bfa; }
.doc-table td { padding:8px; border-bottom:1px solid #1e1f2e; color:#ccc; }
.doc-table tr:hover { background:#1e1f2e; }
.doc-source { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; }
.source-book { background:#2d1b4e; color:#a78bfa; }
.source-law { background:#1b3a2d; color:#4ade80; }
.source-qa { background:#3a2d1b; color:#fbbf24; }
.source-cars { background:#1b2d3a; color:#60a5fa; }
.source-company { background:#3a1b2d; color:#f472b6; }
.loading { text-align:center; padding:40px; color:#666; }
.empty { text-align:center; padding:40px; color:#666; font-size:14px; }
.page-btns { display:flex; gap:6px; justify-content:center; margin-top:16px; }
.page-btn { padding:6px 12px; border-radius:6px; border:1px solid #333; background:#1e1f2e; color:#aaa; cursor:pointer; font-size:13px; }
.page-btn.active { background:#6c5ce7; color:#fff; border-color:#6c5ce7; }
</style>
</head>
<body>
<div class="header">
  <h1>RAG 向量库可视化</h1>
  <div class="sub" id="healthInfo">加载中...</div>
</div>
<div class="container">
  <div class="tabs">
    <div class="tab active" onclick="switchTab('stats')">统计概览</div>
    <div class="tab" onclick="switchTab('search')">检索测试</div>
    <div class="tab" onclick="switchTab('browse')">浏览文档</div>
  </div>

  <div id="stats" class="panel active">
    <div class="card">
      <h3>基本信息</h3>
      <div class="stat-grid" id="statGrid"><div class="loading">加载中...</div></div>
    </div>
    <div class="card">
      <h3>按来源分布</h3>
      <div class="bar-chart" id="sourceChart"></div>
    </div>
    <div class="card">
      <h3>按分类分布</h3>
      <div class="bar-chart" id="categoryChart"></div>
    </div>
    <div class="card">
      <h3>按书籍分布 (Top 20)</h3>
      <div class="bar-chart" id="bookChart"></div>
    </div>
  </div>

  <div id="search" class="panel">
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="输入查询，如：三体讲了什么" onkeydown="if(event.key==='Enter')doSearch()">
      <select id="sourceFilter">
        <option value="">全部来源</option>
        <option value="book">书籍</option>
        <option value="law">法律</option>
        <option value="qa">医学QA</option>
        <option value="cars">二手车</option>
        <option value="company">公司</option>
      </select>
      <button class="btn" onclick="doSearch()">检索</button>
    </div>
    <div id="searchResults"></div>
  </div>

  <div id="browse" class="panel">
    <div class="search-box">
      <select id="browseFilter" onchange="loadDocs(1)">
        <option value="">全部来源</option>
        <option value="book">书籍</option>
        <option value="law">法律</option>
        <option value="qa">医学QA</option>
        <option value="cars">二手车</option>
        <option value="company">公司</option>
      </select>
    </div>
    <div class="card">
      <table class="doc-table">
        <thead><tr><th style="width:60px">#</th><th style="width:80px">来源</th><th>内容预览</th><th style="width:140px">书名/分类</th></tr></thead>
        <tbody id="docBody"><tr><td colspan="4" class="loading">加载中...</td></tr></tbody>
      </table>
      <div class="page-btns" id="pageBtns"></div>
    </div>
  </div>
</div>

<script>
const API = '';
let currentPage = 1;

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`.tab[onclick="switchTab('${name}')"]`).classList.add('active');
  document.getElementById(name).classList.add('active');
  if (name === 'stats') loadStats();
  if (name === 'browse') loadDocs(1);
}

function sourceColor(s) {
  const m = {book:'source-book',law:'source-law',qa:'source-qa',cars:'source-cars',company:'source-company'};
  return m[s] || 'source-book';
}

function renderBar(containerId, data) {
  const el = document.getElementById(containerId);
  if (!data || Object.keys(data).length === 0) { el.innerHTML = '<div class="empty">暂无数据</div>'; return; }
  const max = Math.max(...Object.values(data));
  el.innerHTML = Object.entries(data).slice(0,25).map(([k,v]) =>
    `<div class="bar-row"><div class="bar-label" title="${k}">${k}</div><div class="bar-fill" style="width:${Math.max(v/max*100,2)}%"></div><div class="bar-count">${v}</div></div>`
  ).join('');
}

async function loadStats() {
  try {
    const r = await fetch(API+'/api/rag/stats');
    const d = await r.json();
    if (d.error) { document.getElementById('statGrid').innerHTML = `<div class="empty">${d.error}</div>`; return; }
    document.getElementById('healthInfo').textContent =
      `模型: ${d.embedding_model} | 维度: ${d.embedding_dimension} | 集合: ${d.collection_name} | 连接: ChromaDB ✓`;
    document.getElementById('statGrid').innerHTML = `
      <div class="stat-box"><div class="stat-num">${d.total_documents.toLocaleString()}</div><div class="stat-label">总文档数</div></div>
      <div class="stat-box"><div class="stat-num">${Object.keys(d.source_distribution||{}).length}</div><div class="stat-label">来源类型</div></div>
      <div class="stat-box"><div class="stat-num">${Object.keys(d.book_distribution||{}).length}</div><div class="stat-label">书籍/数据源</div></div>
      <div class="stat-box"><div class="stat-num">${d.embedding_dimension}</div><div class="stat-label">向量维度</div></div>`;
    renderBar('sourceChart', d.source_distribution);
    renderBar('categoryChart', d.category_distribution);
    renderBar('bookChart', d.book_distribution);
  } catch(e) { document.getElementById('statGrid').innerHTML = `<div class="empty">加载失败: ${e.message}</div>`; }
}

async function doSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  const s = document.getElementById('searchResults');
  s.innerHTML = '<div class="loading">检索中...</div>';
  try {
    const r = await fetch(API+'/api/rag/search', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({query:q, top_k:10, source_filter:document.getElementById('sourceFilter').value||null})
    });
    const d = await r.json();
    if (d.error) { s.innerHTML = `<div class="empty">${d.error}</div>`; return; }
    if (!d.results.length) { s.innerHTML = '<div class="empty">无匹配结果</div>'; return; }
    s.innerHTML = d.results.map((r,i) => {
      const meta = r.metadata || {};
      const label = meta.book_title || meta.company || meta.file || meta.source || '';
      const cat = meta.category || meta.section || '';
      return `<div class="result-item">
        <div class="result-header">
          <span><span class="doc-source ${sourceColor(meta.source)}">${meta.source||'?'}</span> ${label} ${cat?'· '+cat:''}</span>
          <span class="result-score">相似度 ${(r.score*100).toFixed(1)}%</span>
        </div>
        <div class="result-content">${escHtml(r.content)}</div>
      </div>`;
    }).join('');
  } catch(e) { s.innerHTML = `<div class="empty">检索失败: ${e.message}</div>`; }
}

async function loadDocs(page) {
  currentPage = page;
  const source = document.getElementById('browseFilter').value;
  const tbody = document.getElementById('docBody');
  tbody.innerHTML = '<tr><td colspan="4" class="loading">加载中...</td></tr>';
  try {
    const url = API+`/api/rag/documents?page=${page}&page_size=20` + (source?`&source=${source}`:'');
    const r = await fetch(url);
    const d = await r.json();
    if (d.error) { tbody.innerHTML = `<tr><td colspan="4" class="empty">${d.error}</td></tr>`; return; }
    if (!d.documents.length) { tbody.innerHTML = '<tr><td colspan="4" class="empty">无文档</td></tr>'; return; }
    tbody.innerHTML = d.documents.map((doc,i) => {
      const m = doc.metadata || {};
      const label = m.book_title || m.company || m.file || '';
      const cat = m.category || m.section || '';
      return `<tr>
        <td style="color:#666">${(page-1)*20+i+1}</td>
        <td><span class="doc-source ${sourceColor(m.source)}">${m.source||'?'}</span></td>
        <td style="max-width:500px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${escHtml(doc.content)}">${escHtml(doc.content)}</td>
        <td style="color:#888;font-size:12px">${label} ${cat?'· '+cat:''}</td>
      </tr>`;
    }).join('');
    const totalPages = Math.ceil(d.total/20);
    let btns = '';
    for (let p=1; p<=Math.min(totalPages,20); p++) {
      btns += `<div class="page-btn ${p===page?'active':''}" onclick="loadDocs(${p})">${p}</div>`;
    }
    document.getElementById('pageBtns').innerHTML = btns;
  } catch(e) { tbody.innerHTML = `<tr><td colspan="4" class="empty">加载失败: ${e.message}</td></tr>`; }
}

function escHtml(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

loadStats();
</script>
</body>
</html>"""


# ========== 代理 ChromaDB 接口 ==========

@app.get("/api/v2/heartbeat")
async def chroma_heartbeat():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_chroma_url}/api/v2/heartbeat")
        return resp.json()

@app.get("/api/v2/tenants/{tenant}/databases/{database}/collections")
async def chroma_list_collections(tenant: str, database: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections")
        return resp.json()

@app.get("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/count")
async def chroma_count(tenant: str, database: str, col_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/count")
        return resp.json()

@app.post("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/query")
async def chroma_query(tenant: str, database: str, col_id: str, body: dict):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/query", json=body)
        return resp.json()

@app.post("/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/get")
async def chroma_get(tenant: str, database: str, col_id: str, body: dict):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{_chroma_url}/api/v2/tenants/{tenant}/databases/{database}/collections/{col_id}/get", json=body)
        return resp.json()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("RAG_SERVICE_PORT", "8085"))
    print(f"启动 RAG 服务: http://0.0.0.0:{port}")
    print(f"  可视化面板: http://localhost:{port}/rag")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
