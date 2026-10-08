from fastapi import APIRouter, Depends

from ..schemas.volume import VolumeCreate, VolumeUpdate
from ..services.volume_service import VolumeService
from ..utils.auth_deps import get_current_user_id

router = APIRouter(prefix="/volumes", tags=["卷管理"])


@router.get("/novel/{novel_id}")
async def list_volumes(
    novel_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.list_volumes(novel_id, user_id)


@router.get("/{volume_id}")
async def get_volume(
    volume_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.get_volume(volume_id, user_id)


@router.post("/novel/{novel_id}")
async def create_volume(
    novel_id: int,
    req: VolumeCreate,
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.create_volume(novel_id, req, user_id)


@router.post("/{volume_id}")
async def update_volume(
    volume_id: int,
    req: VolumeUpdate,
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.update_volume(volume_id, req, user_id)


@router.delete("/{volume_id}")
async def delete_volume(
    volume_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.delete_volume(volume_id, user_id)


@router.post("/novel/{novel_id}/reorder")
async def reorder_volumes(
    novel_id: int,
    volume_ids: list[int],
    user_id: int = Depends(get_current_user_id),
    svc: VolumeService = Depends(),
):
    return svc.reorder_volumes(novel_id, volume_ids, user_id)
