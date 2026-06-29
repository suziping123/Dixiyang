import json

from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.character import NovelCharacter
from ..schemas.character import CharacterCreate, CharacterUpdate
from ..utils.database import get_db
from ..utils.response import Result


class CharacterService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    @staticmethod
    def _prepare_extra(val):
        if val is None:
            return None
        if isinstance(val, dict):
            return val
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return {"content": val}

    def _item(self, c):
        return {
            "id": c.id,
            "novelId": c.novel_id,
            "name": c.name,
            "gender": c.gender,
            "age": c.age,
            "appearance": c.appearance,
            "background": c.background,
            "personality": c.personality,
            "extra": c.extra,
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
            extra=self._prepare_extra(req.extra),
        )
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
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
            c.extra = self._prepare_extra(req.extra)
        self.db.commit()
        self.db.refresh(c)
        return Result.success("更新成功", self._item(c))

    def delete(self, char_id: int) -> dict:
        c = self.db.query(NovelCharacter).filter(NovelCharacter.id == char_id).first()
        if not c:
            return Result.error("角色不存在")
        self.db.delete(c)
        self.db.commit()
        return Result.success("删除成功", None)
