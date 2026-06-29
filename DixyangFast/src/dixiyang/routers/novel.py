from fastapi import APIRouter, Depends

from ..schemas.novel import NovelCreate, NovelUpdate
from ..services.novel_service import NovelService
from ..utils.auth_deps import get_current_user_id

router = APIRouter(prefix="/novel", tags=["小说相关模块"])


@router.get("/listall")
async def list_all(page: int = 1, page_size: int = 10, user_id: int = Depends(get_current_user_id), svc: NovelService = Depends()):
    return svc.list_all(user_id, page, page_size)


@router.get("/{novel_id}")
async def get_by_id(novel_id: int, svc: NovelService = Depends()):
    return svc.get_by_id(novel_id)


@router.post("/create")
async def create(req: NovelCreate, user_id: int = Depends(get_current_user_id), svc: NovelService = Depends()):
    return svc.create(user_id, req)


@router.post("/update/{novel_id}")
async def update(novel_id: int, req: NovelUpdate, user_id: int = Depends(get_current_user_id), svc: NovelService = Depends()):
    return svc.update(user_id, novel_id, req)


@router.post("/delete/{novel_id}")
async def delete(novel_id: int, user_id: int = Depends(get_current_user_id), svc: NovelService = Depends()):
    return svc.delete(user_id, novel_id)
