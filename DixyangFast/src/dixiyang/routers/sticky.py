"""便利贴灵感路由 /api/sticky/*（全站悬浮便签 + AI 补全素材池）"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..schemas.sticky import NoteCreate, NoteUpdate
from ..services import sticky_service
from ..utils.auth_deps import get_current_user_id
from ..utils.database import get_db

router = APIRouter(prefix="/sticky", tags=["便利贴灵感墙"])


@router.get("/notes")
async def list_notes(
    in_pool: bool | None = Query(default=None, alias="inPool"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """我的全部便签（含正文/图片，一次拉全量供悬浮层渲染）"""
    return sticky_service.list_notes(db, user_id, in_pool)


@router.post("/notes")
async def create_note(
    req: NoteCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return sticky_service.create_note(db, user_id, req)


@router.put("/notes/{note_id}")
async def update_note(
    note_id: int,
    req: NoteUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return sticky_service.update_note(db, user_id, note_id, req)


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return sticky_service.delete_note(db, user_id, note_id)


@router.get("/pool")
async def pool(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """已投喂的灵感素材池（编辑器 AI 补全勾选用，只拉池子不拉全量）"""
    return sticky_service.list_notes(db, user_id, in_pool=True)
