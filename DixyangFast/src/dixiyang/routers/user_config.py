from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..models.user_config import UserConfig
from ..utils.database import get_db
from ..utils.response import Result

router = APIRouter(prefix="/userConfig", tags=["用户配置模块"])


@router.get("/background")
async def get_background(userId: int = Query(..., alias="userId"), db: Session = Depends(get_db)):
    config = db.query(UserConfig).filter(UserConfig.user_id == userId).first()
    if not config:
        config = UserConfig(user_id=userId)
        db.add(config)
        db.commit()
        db.refresh(config)
    return Result.success(data=config)


@router.post("/background")
async def update_background(dto: dict, db: Session = Depends(get_db)):
    user_id = dto.get("userId")
    if not user_id or user_id <= 0:
        return Result.error("无效的userId")
    config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
    if not config:
        config = UserConfig(user_id=user_id)
        db.add(config)
    if dto.get("backgroundId") is not None:
        config.background_id = str(dto["backgroundId"])
    if dto.get("customBgs") is not None:
        config.custom_bgs = dto["customBgs"] if isinstance(dto["customBgs"], list) else str(dto["customBgs"])
    db.commit()
    db.refresh(config)
    return Result.success("更新成功", config)
