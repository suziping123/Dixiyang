#!/usr/bin/env python3
"""
RAG 向量库可视化工具
支持查看向量库统计、检索测试、数据探索
"""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加共享库路径
RAG_SHARED_PATH = Path(__file__).parent.parent / "rag-shared" / "python"
sys.path.insert(0, str(RAG_SHARED_PATH))

import chromadb
from sentence_transformers import SentenceTransformer
from rag_shared.config import load_config, get_config_summary


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def list_collections(vectordb_path: str):
    """列出所有集合"""
    client = chromadb.PersistentClient(path=vectordb_path)
    collections = client.list_collections()
    print_header("向量库集合列表")
    for col in collections:
        print(f"  - {col.name}: {col.count()} 文档")
    return client


def inspect_collection(client: chromadb.Client, collection_name: str, limit: int = 5):
    """查看集合内容"""
    col = client.get_collection(collection_name)
    print_header(f"集合详情: {collection_name}")
    print(f"  文档总数: {col.count()}")

    if col.count() == 0:
        print("  (空集合)")
        return

    # 查看前几条
    results = col.peek(limit)
    print(f"\n  前 {limit} 条样本:")
    for i, (doc_id, doc, meta) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
        print(f"\n  [{i+1}] ID: {doc_id}")
        print(f"      来源: {meta.get('source', 'N/A')}")
        print(f"      书籍: {meta.get('book_title', meta.get('company', meta.get('file', 'N/A')))}")
        print(f"      分类: {meta.get('category', meta.get('section', 'N/A'))}")
        print(f"      内容预览: {doc[:200]}...")


def search_test(client: chromadb.Client, collection_name: str, query: str, model, n_results: int = 5):
    """测试检索"""
    col = client.get_collection(collection_name)
    print_header(f"检索测试: '{query}'")
    
    query_emb = model.encode([query]).tolist()
    results = col.query(
        query_embeddings=query_emb,
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    
    for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        score = 1 - dist  # cosine similarity
        print(f"\n  [{i+1}] 相似度: {score:.4f}")
        print(f"      来源: {meta.get('source', 'N/A')}")
        print(f"      书籍: {meta.get('book_title', meta.get('company', meta.get('file', 'N/A')))}")
        print(f"      内容: {doc[:300]}...")


def stats_by_source(client: chromadb.Client, collection_name: str):
    """按来源统计文档分布"""
    col = client.get_collection(collection_name)
    if col.count() == 0:
        return
    
    # 获取所有元数据（分批）
    all_metas = []
    batch_size = 1000
    total = col.count()
    
    for offset in range(0, total, batch_size):
        results = col.get(
            limit=min(batch_size, total - offset),
            offset=offset,
            include=['metadatas']
        )
        all_metas.extend(results['metadatas'])
    
    # 统计
    source_counts = {}
    category_counts = {}
    book_counts = {}
    
    for meta in all_metas:
        src = meta.get('source', 'unknown')
        source_counts[src] = source_counts.get(src, 0) + 1
        
        cat = meta.get('category', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        book = meta.get('book_title', meta.get('company', meta.get('file', 'unknown')))
        book_counts[book] = book_counts.get(book, 0) + 1
    
    print_header("数据分布统计")
    print(f"\n  按来源类型:")
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {src}: {cnt} ({cnt/total*100:.1f}%)")
    
    print(f"\n  按分类 (Top 10):")
    for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {cat}: {cnt} ({cnt/total*100:.1f}%)")
    
    print(f"\n  按书籍/数据源 (Top 15):")
    for book, cnt in sorted(book_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"    {book}: {cnt}")


def export_metadata(client: chromadb.Client, collection_name: str, output_file: str):
    """导出所有元数据到 JSON"""
    col = client.get_collection(collection_name)
    if col.count() == 0:
        return
    
    total = col.count()
    all_data = []
    batch_size = 1000
    
    for offset in range(0, total, batch_size):
        results = col.get(
            limit=min(batch_size, total - offset),
            offset=offset,
            include=['documents', 'metadatas', 'ids']
        )
        for doc_id, doc, meta in zip(results['ids'], results['documents'], results['metadatas']):
            all_data.append({
                'id': doc_id,
                'content': doc,
                'metadata': meta
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n已导出 {len(all_data)} 条记录到: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG 向量库可视化工具")
    parser.add_argument('--hardware', choices=['auto', 'r5_5600u', 'rtx_4060'],
                       default='auto', help='硬件配置预设（决定向量库路径）')
    parser.add_argument('--config-dir', type=str, default='../rag-shared/config', help='配置目录')
    parser.add_argument('--collection', type=str, default='dixiyang_knowledge', help='集合名称')
    parser.add_argument('--vectordb-path', type=str, help='直接指定向量库路径（覆盖硬件配置）')
    parser.add_argument('--query', type=str, help='测试检索查询')
    parser.add_argument('--top-k', type=int, default=5, help='检索返回数量')
    parser.add_argument('--export', type=str, help='导出元数据到文件')
    parser.add_argument('--limit', type=int, default=5, help='预览条数')
    
    args = parser.parse_args()
    
    # 加载配置确定向量库路径
    if args.vectordb_path:
        vectordb_path = args.vectordb_path
    else:
        config = load_config(args.hardware, Path(args.config_dir))
        vectordb_path = config.vectordb_path
        print(get_config_summary(config))
    
    print(f"向量库路径: {vectordb_path}")
    
    # 连接向量库
    client = chromadb.PersistentClient(path=vectordb_path)
    
    # 列出集合
    list_collections(vectordb_path)
    
    # 检查集合是否存在
    collections = client.list_collections()
    col_names = [c.name for c in collections]
    
    if args.collection not in col_names:
        print(f"\n❌ 集合 '{args.collection}' 不存在，可用集合: {col_names}")
        return
    
    # 查看集合内容
    inspect_collection(client, args.collection, args.limit)
    
    # 统计分布
    stats_by_source(client, args.collection)
    
    # 检索测试
    if args.query:
        # 需要加载对应的 embedding 模型
        config = load_config(args.hardware, Path(args.config_dir))
        model = SentenceTransformer(config.embedding_model, device=config.device)
        search_test(client, args.collection, args.query, model, args.top_k)
    
    # 导出
    if args.export:
        export_metadata(client, args.collection, args.export)
    
    print("\n" + "="*60)
    print("完成")


if __name__ == "__main__":
    main()