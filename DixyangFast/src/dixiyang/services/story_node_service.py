from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.story_node import StoryNode
from ..schemas.story_node import StoryNodeCreate, StoryNodeUpdate
from ..utils.database import get_db
from ..utils.response import Result


class StoryNodeService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    @staticmethod
    def _norm(val):
        if isinstance(val, list):
            return ",".join(val)
        return val

    def _item(self, n):
        return {
            "id": n.id,
            "novelId": n.novel_id,
            "timelineId": n.timeline_id,
            "title": n.title,
            "content": n.content,
            "eventDate": n.event_date,
            "eventType": n.event_type,
            "importance": n.importance,
            "characterNames": self._norm(n.character_names),
            "tags": self._norm(n.tags),
            "vectorId": n.vector_id,
            "createTime": self._dt(n.create_time),
        }

    def list_all(self, novel_id: int) -> dict:
        records = self.db.query(StoryNode).filter(StoryNode.novel_id == novel_id).order_by(StoryNode.event_date.asc()).all()
        return Result.success("获取成功", [self._item(n) for n in records])

    def list_paginated(self, novel_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(StoryNode).filter(StoryNode.novel_id == novel_id).order_by(StoryNode.event_date.asc())
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        return Result.success("获取成功", {
            "records": [self._item(n) for n in records],
            "total": total,
            "size": page_size,
            "current": page,
            "pages": (total + page_size - 1) // page_size,
        })

    def list_by_timeline(self, timeline_id: int) -> dict:
        records = self.db.query(StoryNode).filter(StoryNode.timeline_id == timeline_id).order_by(StoryNode.event_date.asc()).all()
        return Result.success("获取成功", [self._item(n) for n in records])

    def get_by_id(self, node_id: int) -> dict:
        n = self.db.query(StoryNode).filter(StoryNode.id == node_id).first()
        if not n:
            return Result.error("节点不存在")
        return Result.success("获取成功", self._item(n))

    def create(self, req: StoryNodeCreate) -> dict:
        n = StoryNode(
            novel_id=req.novel_id,
            timeline_id=req.timeline_id,
            title=req.title,
            content=req.content,
            event_date=req.event_date,
            event_type=req.event_type,
            importance=req.importance,
            character_names=req.character_names,
            tags=req.tags,
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return Result.success("创建成功", self._item(n))

    def update(self, node_id: int, req: StoryNodeUpdate) -> dict:
        n = self.db.query(StoryNode).filter(StoryNode.id == node_id).first()
        if not n:
            return Result.error("节点不存在")
        if req.timeline_id is not None:
            n.timeline_id = req.timeline_id
        if req.title is not None:
            n.title = req.title
        if req.content is not None:
            n.content = req.content
        if req.event_date is not None:
            n.event_date = req.event_date
        if req.event_type is not None:
            n.event_type = req.event_type
        if req.importance is not None:
            n.importance = req.importance
        if req.character_names is not None:
            n.character_names = req.character_names
        if req.tags is not None:
            n.tags = req.tags
        self.db.commit()
        self.db.refresh(n)
        return Result.success("更新成功", self._item(n))

    def delete(self, node_id: int) -> dict:
        n = self.db.query(StoryNode).filter(StoryNode.id == node_id).first()
        if not n:
            return Result.error("节点不存在")
        self.db.delete(n)
        self.db.commit()
        return Result.success("删除成功", None)
