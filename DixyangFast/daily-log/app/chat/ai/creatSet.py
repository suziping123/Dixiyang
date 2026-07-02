import os
import chromadb
from chromadb.utils import embedding_functions
import sys
from pathlib import Path

# 将 daily-log 目录添加到 sys.path（即 creatSet.py 的上上级的上级）
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent)) 

# 导入 app.config
from app.config import model_path

embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name = model_path
)

# 数据集持久化路径
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data", "mytest")
client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection("mytest", embedding_function=embedding_model)

documents = [
    "小明喜欢吃苹果",
    "小黑喜欢吃香蕉",
    "小刚喜欢吃橘子",
]

collection.add(
    documents=documents,
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"source": "小红书"} for _ in documents
    ]
)

if __name__ == "__main__":
    print(collection.count())
    print(collection.get())
