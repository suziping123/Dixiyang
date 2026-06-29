from fastapi import APIRouter, Depends

from ..schemas.character import CharacterCreate, CharacterUpdate
from ..services.character_service import CharacterService

router = APIRouter(prefix="/novelCharacter", tags=["角色管理模块"])


@router.get("/list/{novel_id}")
async def list_paginated(novel_id: int, page: int = 1, page_size: int = 10, svc: CharacterService = Depends()):
    return svc.list_paginated(novel_id, page, page_size)


@router.get("/all/{novel_id}")
async def list_all(novel_id: int, svc: CharacterService = Depends()):
    return svc.list_all(novel_id)


@router.get("/{char_id}")
async def get_by_id(char_id: int, svc: CharacterService = Depends()):
    return svc.get_by_id(char_id)


@router.post("/create")
async def create(req: CharacterCreate, svc: CharacterService = Depends()):
    return svc.create(req)


@router.post("/update/{char_id}")
async def update(char_id: int, req: CharacterUpdate, svc: CharacterService = Depends()):
    return svc.update(char_id, req)


@router.post("/delete/{char_id}")
async def delete(char_id: int, svc: CharacterService = Depends()):
    return svc.delete(char_id)
