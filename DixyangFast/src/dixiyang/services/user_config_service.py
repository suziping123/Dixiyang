"""
用户配置服务 - 使用 storage_service 存储 JSON
对齐 Java 端 UserConfigController
"""
import json
import logging
from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.user_config import UserConfig
from ..utils.database import get_db
from ..utils.response import Result
from .storage_service import save_json, load_json, delete_json

log = logging.getLogger(__name__)

USER_SUBDIR = "user"


class UserConfigService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _get_or_create(self, user_id: int) -> UserConfig:
        config = self.db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
        if not config:
            config = UserConfig(user_id=user_id)
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config

    def get_background(self, user_id: int) -> dict:
        config = self._get_or_create(user_id)
        # 加载 custom_bgs 实际数据，返回 JSON 字符串（前端需要 JSON.parse 解析）
        custom_bgs_data = load_json(f"{USER_SUBDIR}/customBgs", user_id, config.custom_bgs)
        custom_bgs_str = json.dumps(custom_bgs_data, ensure_ascii=False) if custom_bgs_data is not None else None
        data = {
            "id": config.id,
            "userId": config.user_id,
            "preset": config.preset,
            "animEnabled": config.anim_enabled,
            "intensity": config.intensity,
            "colorTheme": config.color_theme,
            "customImageUrl": config.custom_image_url,
            "backgroundId": config.background_id,
            "customBgs": custom_bgs_str,
            "fontColorsJson": config.font_colors_json,
        }
        return Result.success(data=data)

    def update_background(self, user_id: int, background_id: str | None, custom_bgs) -> dict:
        config = self._get_or_create(user_id)
        if background_id is not None:
            config.background_id = background_id
        if custom_bgs is not None:
            # custom_bgs 可能是 list 或 str，存文件
            if isinstance(custom_bgs, list):
                data = custom_bgs
            elif isinstance(custom_bgs, str):
                try:
                    parsed = json.loads(custom_bgs)
                    data = parsed if isinstance(parsed, (dict, list)) else {"content": custom_bgs}
                except json.JSONDecodeError:
                    data = {"content": custom_bgs}
            elif isinstance(custom_bgs, dict):
                data = custom_bgs
            else:
                data = {"content": str(custom_bgs)}
            ref = save_json(f"{USER_SUBDIR}/customBgs", user_id, data)
            config.custom_bgs = ref
        self.db.commit()
        self.db.refresh(config)
        return Result.success("更新成功")

    def get_font_colors(self, user_id: int) -> dict:
        config = self._get_or_create(user_id)
        data = load_json(f"{USER_SUBDIR}/fontColors", user_id, config.font_colors_json)
        return Result.success(data=data)

    def update_font_colors(self, user_id: int, colors: dict) -> dict:
        config = self._get_or_create(user_id)
        delete_json(f"{USER_SUBDIR}/fontColors", user_id, config.font_colors_json)
        ref = save_json(f"{USER_SUBDIR}/fontColors", user_id, colors)
        config.font_colors_json = ref
        self.db.commit()
        self.db.refresh(config)
        return Result.success("更新成功")
