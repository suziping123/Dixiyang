from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from FlagEmbedding import FlagReranker
import os

law_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data", "datasets", "法律数据集.csv")
embedding_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "models", "bge-m3")
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")
COLLECTION_NAME = "lawdata"
print(law_data_path)
print(embedding_model_path)

# 构建知识库 
def create_law_base():
    """
    构建法律知识库
    :return: None
    """
    loader =CSVLoader(
        file_path=law_data_path,
        encoding="utf-8",
    )
    # 加载文档
    documents = loader.load()
    print(documents)
    # 文档处理(省略)
    # 加载向量化模型
    embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_path)
    # 向量化入库
    Chroma.from_documents(
        documents=documents,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},# 元数据的配置，指定向量空间为余弦相似度
    )
    print("法律知识库构建完成")


# 检索阶段
def search_law_base(query: str) -> str:
    """
    搜索法律知识库
    :param query: 查询问题
    :return: 搜索结果
    """
    embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_path)
    chroma_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH,
    )
    retriever = chroma_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10},
    )
    docs = retriever.invoke(query)
    if not docs:
        return "未检索到相关法律条文。"
    reranker = FlagReranker("/home/lijiajia/models/bge-reranker-large", use_fp16=True)
    pairs = [[query, doc.page_content] for doc in docs]
    scores = reranker.compute_score(pairs)
    doc_with_scores = list(zip(docs, scores))
    doc_with_scores.sort(key=lambda x: x[1], reverse=True)
    top_docs = [item[0] for item in doc_with_scores[:3]]
    context = "\n\n".join([d.page_content for d in top_docs])
    return context

if __name__ == "__main__":
    create_law_base()
