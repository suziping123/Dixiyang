import os
from typing import List

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_react_agent, AgentExecutor

from app.chat.ai.model import load_model
from app.chat.DAO.ChatDAO import ChatDAO
from app.chat.utils.GetJSONResponse import GetJSONResponse
from app.chat.ai.send_email_tool import send_email_tool


EMBEDDING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "models", "bge-m3",
)
CHROMA_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "chroma_data",
)
COLLECTION_NAME = "lawdata"
RERANKER_PATH = "/home/lijiajia/models/bge-reranker-large"


def _get_retriever():
    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_PATH)
    db = Chroma(
        embedding_function=embedding,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME,
    )
    return db.as_retriever(search_kwargs={"k": 10})


def _rerank(query: str, docs: List[Document]) -> List[Document]:
    reranker = FlagReranker(RERANKER_PATH, use_fp16=True)
    pairs = [[query, d.page_content] for d in docs]
    scores = reranker.compute_score(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [item[0] for item in ranked[:3]]


@tool
def legal_rag_search(query: str) -> str:
    """在法律知识库中检索与 query 相关的法律条文，返回最相关的条文内容。"""
    retriever = _get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "未检索到相关法律条文。"
    top_docs = _rerank(query, docs)
    return "\n\n".join([d.page_content for d in top_docs])


SYSTEM_PROMPT = """你是智能法律问答助手，你可以使用以下工具：

{tools}

使用规则：
- 法律问题 → 调用 legal_rag_search 检索相关条文，基于检索结果回答
- 通用问题 → 依靠自身知识回答
- 用户要求发送邮件 → 先检索/回答，再调用 send_email(to, subject, content)

工具名称：{tool_names}
"""


class ChatService:
    def __init__(self):
        self.dao = ChatDAO()
        self._agent = None

    def _get_agent(self) -> AgentExecutor:
        if self._agent is not None:
            return self._agent
        llm = load_model()
        tools = [legal_rag_search, send_email_tool]
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_react_agent(llm, tools, prompt)
        self._agent = AgentExecutor(
            agent=agent,
            tools=tools,
            handle_parsing_errors=True,
            verbose=True,
        )
        return self._agent

    def _invoke(self, question: str) -> str:
        agent = self._get_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        if isinstance(result, dict) and "messages" in result:
            return result["messages"][-1].content
        if isinstance(result, dict) and "output" in result:
            return result["output"]
        return str(result)

    def chatInvoke(self, question: str):
        answer = self._invoke(question)
        self.dao.save_chat_record(question, answer)
        return GetJSONResponse.success(data={"data": answer})

    def chat(self, question: str):
        answer = self._invoke(question)
        self.dao.save_chat_record(question, answer)
        return answer

    def stream_chat(self, question: str):
        answer = self._invoke(question)
        self.dao.save_chat_record(question, answer)
        yield answer
