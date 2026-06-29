from fastapi import APIRouter, Depends

from ..schemas.story_node import StoryNodeCreate, StoryNodeUpdate
from ..services.story_node_service import StoryNodeService

router = APIRouter(prefix="/storyNode", tags=["故事节点管理模块"])


@router.get("/all/{novel_id}")
async def list_all(novel_id: int, svc: StoryNodeService = Depends()):
    return svc.list_all(novel_id)


@router.get("/list/{novel_id}")
async def list_paginated(novel_id: int, page: int = 1, page_size: int = 10, svc: StoryNodeService = Depends()):
    return svc.list_paginated(novel_id, page, page_size)


@router.get("/timeline/{timeline_id}")
async def list_by_timeline(timeline_id: int, svc: StoryNodeService = Depends()):
    return svc.list_by_timeline(timeline_id)


@router.get("/{node_id}")
async def get_by_id(node_id: int, svc: StoryNodeService = Depends()):
    return svc.get_by_id(node_id)


@router.post("/create")
async def create(req: StoryNodeCreate, svc: StoryNodeService = Depends()):
    return svc.create(req)


@router.post("/update/{node_id}")
async def update(node_id: int, req: StoryNodeUpdate, svc: StoryNodeService = Depends()):
    return svc.update(node_id, req)


@router.post("/delete/{node_id}")
async def delete(node_id: int, svc: StoryNodeService = Depends()):
    return svc.delete(node_id)
