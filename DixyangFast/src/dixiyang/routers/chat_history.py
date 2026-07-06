from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..utils.auth_deps import get_current_user_id
from ..utils.database import get_db
from ..services.chat_history_service import ChatHistoryService
from ..schemas.chat_history import CreateSessionRequest, BatchSaveRequest, EditMessageRequest
from ..utils.response import Result

router = APIRouter(prefix="/chatHistory", tags=["聊天历史模块"])


@router.get("/sessions")
async def get_sessions(novelId: int | None = Query(default=None, alias="novelId"), user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.get_sessions(user_id, novelId)


@router.post("/createSession")
async def create_session(req: CreateSessionRequest, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.create_session(user_id, req.novel_id, req.title)


@router.get("/session/{session_id}")
async def get_session(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.get_session_messages(user_id, session_id)


@router.post("/batchSave")
async def batch_save(req: BatchSaveRequest, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.batch_save(user_id, req.session_id, req.novel_id, req.messages)


@router.put("/message/{session_id}")
async def edit_message(session_id: str, req: EditMessageRequest, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    if req.message_index < 0 or not req.content:
        return Result.error("参数不完整")
    return svc.edit_message(user_id, session_id, req.message_index, req.role, req.content)


@router.post("/generate-title/{session_id}")
async def generate_title(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.generate_title(user_id, session_id)


@router.delete("/session/{session_id}")
async def delete_session(session_id: str, user_id: int = Depends(get_current_user_id), svc: ChatHistoryService = Depends()):
    return svc.delete_session(user_id, session_id)
