import sys
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 1. 现场定义路径 (绕过 app.config)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = PROJECT_ROOT/ "app" / "chat" / "chroma_data" / "datasets"
MODELS_DIR = PROJECT_ROOT.parent / "models"

# 2. 定义您真实的模型路径 (bge-m3)
model_path = MODELS_DIR / "bge-m3"
npz_path = DATASETS_DIR / "flag_doc.npz"

documents = [
    "FlagEmbedding 是一个由北京智源人工智能研究院开发的文本嵌入模型。",
    "它可以讲文本转换为高维向量，用于计算语义相似度。",
    "BGE 模型在 Massive Text Embedding Benchmark (MTEB) 排行榜上取得了优异的成绩。",
    "RAG (检索增强生成) 是一种利用外部知识库来增强大模型问答能力的技术。",
    "苹果公司由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗纳德·韦恩于 1976 年创立。",
    "苹果最新款的智能手机是 iPhone 15 系列，搭载了 A17 Pro 芯片。",
    "熊猫是中国的国宝，主要栖息地是四川、陕西和甘肃的山区。",
    "深度学习是机器学习的一个分支，它基于深层神经网络。",
]

if __name__ == "__main__":
    # 3. 绝对关键：强制转换为 str()，防止 TypeError
    model = SentenceTransformer(str(model_path)) 
    embeddings = model.encode(documents)
    print(embeddings)
    print(type(embeddings))
    print(embeddings.shape)
    np.savez(npz_path, embeddings=embeddings, documents=documents)
    print(f"已成功保存到：{npz_path}")