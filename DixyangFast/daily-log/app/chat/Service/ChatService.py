import os
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import create_react_agent, AgentExecutor

from app.chat.ai.model import load_model
from app.chat.DAO.ChatDAO import ChatDAO
from app.chat.utils.GetJSONResponse import GetJSONResponse
from app.chat.ai.send_email_tool import send_email_tool


EMBEDDING_PATH = "/home/lijiajia/项目/Dixiyang/DixyangFast/models/bge-m3"
CHROMA_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "chroma_data",
)
COLLECTION_NAME = "lawdata"
RERANKER_PATH = "/home/lijiajia/models/bge-reranker-large"

_embedding: Optional[HuggingFaceEmbeddings] = None
_chroma_instance: Optional[Chroma] = None
_reranker: Optional[FlagReranker] = None


def _get_retriever():
    global _embedding, _chroma_instance
    if _chroma_instance is None:
        _embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_PATH)
        _chroma_instance = Chroma(
            embedding_function=_embedding,
            persist_directory=CHROMA_DB_PATH,
            collection_name=COLLECTION_NAME,
        )
    return _chroma_instance.as_retriever(search_kwargs={"k": 10})


def _rerank(query: str, docs: List[Document]) -> List[Document]:
    global _reranker
    if _reranker is None:
        _reranker = FlagReranker(RERANKER_PATH, use_fp16=True)
    pairs = [[query, d.page_content] for d in docs]
    scores = _reranker.compute_score(pairs)
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


REACT_TEMPLATE = """你是智能法律问答助手，你可以使用以下工具：

{tools}

工具名称：{tool_names}

使用格式：

Question: 用户的问题
Thought: 思考需要做什么
Action: 要执行的动作，必须是 [{tool_names}] 之一
Action Input: 动作的输入参数
Observation: 动作的结果
...（Thought/Action/Action Input/Observation 可以重复多次）
Thought: 我现在知道最终答案
Final Answer: 对用户的最终回答

规则：
- 用户问法律问题 → 调用 legal_rag_search 检索相关条文，再基于检索结果回答
- 用户要求发送邮件至邮箱 → 先检索相关法律条文，再调用 send_email 发送结果
- 调用 send_email 时，Action Input 必须是 JSON 字符串：{{"to": "邮箱地址", "subject": "邮件主题", "content": "邮件正文"}}
- 不要自己编造法律条文，必须通过检索获取

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


class ChatService:
    def __init__(self):
        self.dao = ChatDAO()
        self._agent = None

    def _get_agent(self) -> AgentExecutor:
        if self._agent is not None:
            return self._agent
        llm = load_model()
        tools = [legal_rag_search, send_email_tool]
        prompt = PromptTemplate.from_template(REACT_TEMPLATE)
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
        result = agent.invoke({"input": question})
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
