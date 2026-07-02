import sys
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODELS_DIR = PROJECT_ROOT.parent / "models"
CHROMA_DB_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "mytest"
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

model_path = MODELS_DIR / "bge-m3"

if __name__ == "__main__":
    # 2. 绝对关键：强制转换为 str()
    embedding_model = HuggingFaceEmbeddings(model_name=str(model_path))
    client = Chroma(
        collection_name="col1",
        persist_directory=str(CHROMA_DB_DIR), 
        embedding_function=embedding_model
    )
    print("创建连接成功")