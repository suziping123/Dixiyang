from langchain_community.document_loaders import CSVLoader
import os
from langchain.prompts import PromptTemplate
# os.path.dirname(__file__)表示当前文件或文件夹所在的目录，join表示拼接路径组件
law_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data", "datasets", "法律数据集.csv")
embedding_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "models", "bge-m3")
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")
COLLECTION_NAME = "lawdata"
reranker = FlagReranker("/home/lijiajia/models/bge-reranker-large", use_fp16=True)
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


o
# 检索阶段
def search_law_base(query: str) -> str:
    """
    搜索法律知识库
    :param query: 查询问题
    :return: 搜索结果
    """
    embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_path)
    # 连接数据库
    chroma_db=Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH,
    )
    # 构造检索器
    retriever = vector_store.as_retriever(# 
        search_type="similarity",  # 相似度搜索
        search_kwargs={"k": 10},    # 返回前 10 个结果
    )
    # 问题向量化
    # 粗召回
    # 重排序

    # 拼接提示词
    template = f"""
        你是一个专业的知识库问答助手。你的任务是基于给定的【参考上下文】来准确回答用户的【问题】。
        不要捏造事情，请根据实际结果回答，如果没有检索到相关的内容，就给出一个友好的回复
        如果检索到相关内容，就基于相关内容生成一个友好回复
        - 参考上下文: {context}
        - 用户问题: {question}
    """ 
    prompt = PromptTemplate.from_template(template, input_variables=["context", "question"])
    # 调用大模型
    # 生成响应结果
if __name__ == "__main__":
    create_law_base()
