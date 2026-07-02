import sys
import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. 现场定义路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODELS_DIR = PROJECT_ROOT.parent / "models"
CHROMA_DB_DIR = PROJECT_ROOT / "app" / "chat" / "chroma_data" / "mytest"
model_path = MODELS_DIR / "bge-m3"

# 从环境变量读取 API 配置
DS_API_KEY = os.getenv("DS_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4-flash")

if __name__ == "__main__":
    question = "cc老师介绍"
    
    embedding_model = HuggingFaceEmbeddings(model_name=str(model_path))
    db = Chroma(
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_DB_DIR),
        collection_name="col1"
    )
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
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
        | prompt
        | llm
        | StrOutputParser()
    )
    response = qa_chain.invoke(question)
    print(response)