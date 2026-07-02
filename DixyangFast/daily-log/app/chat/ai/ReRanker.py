import sys
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "datasets"
MODELS_DIR = PROJECT_ROOT.parent / "models"

# 本地 Embedding 模型 (bge-m3)
model_path = str(MODELS_DIR / "bge-m3")
npz_path = DATASETS_DIR / "flag_doc.npz"
top_k = 5

# 线上重排序模型仓库名
reranker_model_path = "BAAI/bge-reranker-large" 

if __name__ == "__main__":
    npz_data = np.load(npz_path, allow_pickle=True)
    documents = npz_data["documents"]
    embeddings = npz_data["embeddings"]

    # 1. 加载 Embedding 模型并编码问题
    model = SentenceTransformer(model_path)
    question = "什么是RAG"
    question_embeddings = model.encode(question)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # 2. 计算余弦相似度并进行粗召回
    similarity = [cosine_similarity(question_embeddings, embedding) for embedding in embeddings]
    indices = np.argsort(similarity)[::-1][:top_k]

    # 3. 实例化重排序模型 (自动下载并缓存)
    print("正在加载 FlagReranker...")
    reranker_model = FlagReranker(model_name_or_path=reranker_model_path, use_fp16=True)
    
    # 4. 准备重排序输入 (注意：FlagReranker 的 compute_score 最好传入嵌套的 List，而不是 Tuple)
    pairs = [[question, documents[i]] for i in indices] 
    reranker_scores = reranker_model.compute_score(pairs)

    # 5. 合成结果并排序
    reranker_list = list(zip(indices, documents[indices], reranker_scores))
    reranker_list.sort(key=lambda x: x[2], reverse=True)
    
    print("=" * 40)
    print("重排序的结果：")
    for idx, (re_idx, doc, reranker_score) in enumerate(reranker_list):
        print(f"第{idx+1}个最相似的文档的索引:{re_idx}, 相似度得分:{reranker_score}, 文档内容：{doc}")