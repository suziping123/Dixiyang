from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..utils.auth_deps import get_current_user_id
from ..utils.database import get_db
from ..services.chat_history_service import ChatHistoryService
from ..utils.response import Result

router = APIRouter(prefix="/chatHistory", tags=["聊天历史模块"])


@router.get("/sessions")
async def get_sessions(novelId: int | None = Query(default=None, alias="novelId"), user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.get_sessions(user_id, novelId)


@router.post("/createSession")
async def create_session(body: dict, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    novel_id = body.get("novelId")
    title = body.get("title", "新对话")
    return svc.create_session(user_id, novel_id, title)


@router.get("/session/{session_id}")
async def get_session(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.get_session_messages(user_id, session_id)


@router.post("/batchSave")
async def batch_save(body: dict, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    session_id = body.get("sessionId")
    novel_id = body.get("novelId")
    messages = body.get("messages")
    if not session_id or messages is None:
        return Result.error("参数不完整")
    return svc.batch_save(user_id, session_id, novel_id, messages)


@router.put("/message/{session_id}")
async def edit_message(session_id: str, body: dict, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    message_index = body.get("messageIndex", -1)
    role = body.get("role", "user")
    content = body.get("content", "")
    if message_index < 0 or not content:
        return Result.error("参数不完整")
    return svc.edit_message(user_id, session_id, message_index, role, content)


@router.post("/generate-title/{session_id}")
async def generate_title(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.generate_title(user_id, session_id)


@router.delete("/session/{session_id}")
async def delete_session(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.delete_session(user_id, session_id)
