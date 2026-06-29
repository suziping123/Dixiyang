from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.timeline import Timeline
from ..schemas.timeline import TimelineCreate, TimelineUpdate
from ..utils.database import get_db
from ..utils.response import Result


class TimelineService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    def _item(self, t):
        return {
            "id": t.id,
            "novelId": t.novel_id,
            "name": t.name,
            "parentId": t.parent_id,
            "description": t.description,
            "createTime": self._dt(t.create_time),
        }

    def list_paginated(self, novel_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(Timeline).filter(Timeline.novel_id == novel_id).order_by(Timeline.create_time.desc())
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        return Result.success("获取成功", {
            "records": [self._item(t) for t in records],
            "total": total,
            "size": page_size,
            "current": page,
            "pages": (total + page_size - 1) // page_size,
        })

    def list_all(self, novel_id: int) -> dict:
        records = self.db.query(Timeline).filter(Timeline.novel_id == novel_id).order_by(Timeline.create_time.desc()).all()
        return Result.success("获取成功", [self._item(t) for t in records])

    def get_by_id(self, timeline_id: int) -> dict:
        t = self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not t:
            return Result.error("时间线不存在")
        return Result.success("获取成功", self._item(t))

    def create(self, req: TimelineCreate) -> dict:
        t = Timeline(
            novel_id=req.novel_id,
            name=req.name,
            description=req.description,
        )
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        return Result.success("创建成功", self._item(t))

    def update(self, timeline_id: int, req: TimelineUpdate) -> dict:
        t = self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not t:
            return Result.error("时间线不存在")
        if req.name is not None:
            t.name = req.name
        if req.description is not None:
            t.description = req.description
        self.db.commit()
        self.db.refresh(t)
        return Result.success("更新成功", self._item(t))

    def delete(self, timeline_id: int) -> dict:
        t = self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not t:
            return Result.error("时间线不存在")
        self.db.delete(t)
        self.db.commit()
        return Result.success("删除成功", None)
