from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.chat.Service.ChatService import ChatService

router = APIRouter(prefix="/api")
chat_service = ChatService()


@router.get("/chat")
def chat(question: str = Query(...)):
    return chat_service.chatInvoke(question)


@router.get("/chat/stream")
def chat_stream(question: str = Query(...)):
    def stream_chat():
        for chunk in chat_service.stream_chat(question):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(stream_chat(), media_type="text/event-stream")