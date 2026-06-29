from fastapi import APIRouter, Depends

from ..schemas.timeline import TimelineCreate, TimelineUpdate
from ..services.timeline_service import TimelineService

router = APIRouter(prefix="/timeline", tags=["时间线管理模块"])


@router.get("/list/{novel_id}")
async def list_paginated(novel_id: int, page: int = 1, page_size: int = 10, svc: TimelineService = Depends()):
    return svc.list_paginated(novel_id, page, page_size)


@router.get("/all/{novel_id}")
async def list_all(novel_id: int, svc: TimelineService = Depends()):
    return svc.list_all(novel_id)


@router.get("/{timeline_id}")
async def get_by_id(timeline_id: int, svc: TimelineService = Depends()):
    return svc.get_by_id(timeline_id)


@router.post("/create")
async def create(req: TimelineCreate, svc: TimelineService = Depends()):
    return svc.create(req)


@router.post("/update/{timeline_id}")
async def update(timeline_id: int, req: TimelineUpdate, svc: TimelineService = Depends()):
    return svc.update(timeline_id, req)


@router.post("/delete/{timeline_id}")
async def delete(timeline_id: int, svc: TimelineService = Depends()):
    return svc.delete(timeline_id)
