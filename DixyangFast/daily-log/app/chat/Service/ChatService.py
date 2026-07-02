from app.chat.ai.model import load_model
from app.chat.DAO.ChatDAO import ChatDAO
from app.chat.utils.GetJSONResponse import GetJSONResponse


class ChatService:
    def __init__(self):
        self.dao = ChatDAO()

    def chatInvoke(self, question: str):
        model = load_model()
        response = model.invoke(question)
        print(response)
        if response:
            self.dao.save_chat_record(question, response.content)
            return GetJSONResponse.success(data={"data": response.content})
        return GetJSONResponse.error(msg="请求失败")

    def chat(self, question: str):
        model = load_model()
        response = model.invoke(question)
        self.dao.save_chat_record(question, response.content)
        return response.content

    def stream_chat(self, question: str):
        model = load_model()
        full_answer = ""
        for chunk in model.stream(question):
            full_answer += chunk.content
            yield chunk.content
        self.dao.save_chat_record(question, full_answer)