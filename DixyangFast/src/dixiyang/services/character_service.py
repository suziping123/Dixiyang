import json

from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.character import NovelCharacter
from ..schemas.character import CharacterCreate, CharacterUpdate
from ..utils.database import get_db
from ..utils.response import Result
from .storage_service import save_json, load_json, delete_json, CHARACTER_DIR


class CharacterService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    @staticmethod
    def _prepare_extra(val):
        """准备 extra 数据：解析 JSON 字符串为 dict"""
        if val is None:
            return None
        if isinstance(val, dict):
            return val
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return {"content": val}

    def _item(self, c):
        """返回角色数据，extra 通过 storage_service 加载"""
        return {
            "id": c.id,
            "novelId": c.novel_id,
            "name": c.name,
            "gender": c.gender,
            "age": c.age,
            "appearance": c.appearance,
            "background": c.background,
            "personality": c.personality,
            "extra": load_json(CHARACTER_DIR, c.id, c.extra),
            "createTime": self._dt(c.create_time),
        }

    def list_paginated(self, novel_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel_id).order_by(NovelCharacter.create_time.desc())
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        return Result.success("获取成功", {
            "records": [self._item(c) for c in records],
            "total": total,
            "size": page_size,
            "current": page,
            "pages": (total + page_size - 1) // page_size,
        })

    def list_all(self, novel_id: int) -> dict:
        records = self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel_id).order_by(NovelCharacter.create_time.desc()).all()
        return Result.success("获取成功", [self._item(c) for c in records])

    def get_by_id(self, char_id: int) -> dict:
        c = self.db.query(NovelCharacter).filter(NovelCharacter.id == char_id).first()
        if not c:
            return Result.error("角色不存在")
        return Result.success("获取成功", self._item(c))

    def create(self, req: CharacterCreate) -> dict:
        c = NovelCharacter(
            novel_id=req.novel_id,
            name=req.name,
            gender=req.gender,
            age=req.age,
            appearance=req.appearance,
            background=req.background,
            personality=req.personality,
            extra=None,  # 先创建，后面单独保存 extra
        )
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        # 保存 extra 到文件
        if req.extra is not None:
            extra_data = self._prepare_extra(req.extra)
            c.extra = save_json(CHARACTER_DIR, c.id, extra_data)
            self.db.commit()
        return Result.success("创建成功", self._item(c))

    def update(self, char_id: int, req: CharacterUpdate) -> dict:
        c = self.db.query(NovelCharacter).filter(NovelCharacter.id == char_id).first()
        if not c:
            return Result.error("角色不存在")
        if req.name is not None:
            c.name = req.name
        if req.gender is not None:
            c.gender = req.gender
        if req.age is not None:
            c.age = req.age
        if req.appearance is not None:
            c.appearance = req.appearance
        if req.background is not None:
            c.background = req.background
        if req.personality is not None:
            c.personality = req.personality
        if req.extra is not None:
            # 删除旧文件
            delete_json(CHARACTER_DIR, c.id, c.extra)
            # 保存新数据
            extra_data = self._prepare_extra(req.extra)
            c.extra = save_json(CHARACTER_DIR, c.id, extra_data)
        self.db.commit()
        self.db.refresh(c)
        return Result.success("更新成功", self._item(c))

    def delete(self, char_id: int) -> dict:
        c = self.db.query(NovelCharacter).filter(NovelCharacter.id == char_id).first()
        if not c:
            return Result.error("角色不存在")
        # 删除关联文件
        delete_json(CHARACTER_DIR, c.id, c.extra)
        self.db.delete(c)
        self.db.commit()
        return Result.success("删除成功", None)

    def save_settings(self, char_id: int, settings: dict) -> dict:
        """保存角色设定（AI 提取的结构化数据）- 合并模式，不覆盖已有字段"""
        c = self.db.query(NovelCharacter).filter(NovelCharacter.id == char_id).first()
        if not c:
            return Result.error("角色不存在")
        # 加载已有设定
        existing = load_json(CHARACTER_DIR, c.id, c.extra)
        if existing is None:
            existing = {}
        elif isinstance(existing, str):
            existing = {"content": existing}
        # 合并：已有字段保留，新字段追加，同名字段用新值覆盖
        merged = {**existing, **settings}
        # 保存合并后的设定
        c.extra = save_json(CHARACTER_DIR, c.id, merged)
        self.db.commit()
        return Result.success("设定保存成功", self._item(c))
