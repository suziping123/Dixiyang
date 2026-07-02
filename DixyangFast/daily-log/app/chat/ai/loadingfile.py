import sys
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "datasets"
MODELS_DIR = PROJECT_ROOT.parent / "models"

model_path = MODELS_DIR / "bge-m3"
npz_path = DATASETS_DIR / "flag_doc.npz"
top_k = 5

if __name__ == "__main__":
    npz_data = np.load(npz_path, allow_pickle=True)
    documents = npz_data["documents"]
    embeddings = npz_data["embeddings"]

    # 2. 绝对关键：强制转换为 str()
    model = SentenceTransformer(str(model_path))
    question = "什么是RAG"
    question_embeddings = model.encode(question)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    similarity = [cosine_similarity(question_embeddings, embedding) for embedding in embeddings]
    indices = np.argsort(similarity)[::-1][:top_k]
    print(f"前{top_k}个最相似的文档的索引:{indices}")

    for idx, doc_idx in enumerate(indices):
        print(f"第{idx+1}个最相似的文档的索引:{doc_idx}, 相似度得分:{similarity[doc_idx]},文档内容：{documents[doc_idx]}")