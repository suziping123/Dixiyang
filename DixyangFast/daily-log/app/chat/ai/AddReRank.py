import sys
import os
from pathlib import Path
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from FlagEmbedding import FlagReranker

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODELS_DIR = PROJECT_ROOT.parent / "models"
CHROMA_DB_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "mytest"
model_path = MODELS_DIR / "bge-m3"

# 2. 环境变量读取与保护（防止没有设置环境变量导致 None 报错）
DS_API_KEY = os.getenv("DS_API_KEY")
# 如果不设置，给个默认值防报错。BASE_URL和MODEL_NAME替换成你实际用的就行
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")  
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4-flash")    

if __name__ == "__main__":
    question = "曾老师介绍"
    
    embedding_model = HuggingFaceEmbeddings(model_name=str(model_path))
    db = Chroma(
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_DB_DIR),
        collection_name="col1"
    )
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # 实例化重排模型
    print("正在加载 FlagReranker 模型...")
    reranker = FlagReranker("BAAI/bge-reranker-large", use_fp16=True)
    
    def rerank_docs(input_dict: dict) -> List[Document]:
        docs: List[Document] = input_dict["context"]
        query: str = input_dict["question"]
        
        pairs = [[query, doc.page_content] for doc in docs]
        
        print("\n开始重排序计算... (计算任务较重，若为 CPU 环境可能需要等待几十秒，请耐心等待)")
        scores = reranker.compute_score(pairs)
        print("重排序计算完成！")

        doc_with_scores = list(zip(docs, scores))
        doc_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        top_docs = [item[0] for item in doc_with_scores[:3]]
        return top_docs

    
    llm = ChatOpenAI(api_key=DS_API_KEY, base_url=BASE_URL, model=MODEL_NAME)
    
    template = """
                你是一个专业的知识库问答助手。你的任务是基于给定的【参考上下文】来准确回答用户的【问题】。
                不要捏造事情，请根据实际结果回答，如果没有检索到相关的内容，就给出一个友好的回复。
                如果检索到相关内容，就基于相关内容生成一个友好回复。
                - 参考上下文: {context}
                - 用户问题: {question}
            """
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    qa_chain = (
        RunnableParallel({
            "context": retriever,
            "question": RunnablePassthrough()
        })
        | RunnableLambda(rerank_docs) 
        | RunnableParallel({
            "context": RunnablePassthrough(),
            "question": lambda x: question
        })
        | prompt
        | llm
        | StrOutputParser()
    )
    print("开始检索与问答...")
    response = qa_chain.invoke(question)
    print("=" * 40)
    print(f"最终回答：\n{response}")