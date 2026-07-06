from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..models.user_config import UserConfig
from ..utils.database import get_db
from ..utils.response import Result
from ..services.user_config_service import UserConfigService

router = APIRouter(prefix="/userConfig", tags=["用户配置模块"])


@router.get("/background")
async def get_background(userId: int = Query(..., alias="userId"), svc: UserConfigService = Depends()):
    return svc.get_background(userId)


@router.post("/background")
async def update_background(dto: dict, svc: UserConfigService = Depends()):
    user_id = dto.get("userId")
    if not user_id or user_id <= 0:
        return Result.error("无效的userId")
    return svc.update_background(user_id, dto.get("backgroundId"), dto.get("customBgs"))


@router.get("/fontColors")
async def get_font_colors(userId: int = Query(..., alias="userId"), svc: UserConfigService = Depends()):
    return svc.get_font_colors(userId)


@router.post("/fontColors")
async def update_font_colors(body: dict, svc: UserConfigService = Depends()):
    user_id = body.get("userId")
    colors = body.get("colors")
    if not user_id or colors is None:
        return Result.error("参数不完整")
    return svc.update_font_colors(user_id, colors)
