import sys
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "datasets"
MODELS_DIR = PROJECT_ROOT.parent / "models"
CHROMA_DB_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "mytest"

model_path = MODELS_DIR / "bge-m3"
dataset_path = DATASETS_DIR / "华清远见.txt"

if __name__ == "__main__":
    data = TextLoader(file_path=str(dataset_path), encoding="utf-8").load()
    print(f"加载的文档内容：{data}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", "，", "！", "？"],
        length_function=len,
        keep_separator=False
    )
    documents = text_splitter.split_documents(data)
    
    embedding_model = HuggingFaceEmbeddings(model_name=str(model_path))
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=str(CHROMA_DB_DIR), 
        collection_name="col1"
    )
    print(f"向量数据库构建完成，数据库路径为：{CHROMA_DB_DIR}")
    collection = db.get()
    print(f"数据库中的文档数为：{len(collection)}")