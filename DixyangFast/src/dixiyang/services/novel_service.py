from fastapi import Depends
from sqlalchemy.orm import Session

from sqlalchemy import func

from ..models.character import NovelCharacter
from ..models.novel import Novels
from ..models.novel_relation import NovelRelation
from ..models.story_node import StoryNode
from ..models.timeline import Timeline
from ..routers.file import delete_file_by_url
from ..schemas.novel import NovelCreate, NovelUpdate
from ..utils.database import get_db
from ..utils.response import Result


class NovelService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    def list_all(self, user_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(Novels).filter(Novels.user_id == user_id).order_by(Novels.update_time.desc())
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        data_list = []
        for n in records:
            char_count = self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == n.id).count()
            node_count = self.db.query(StoryNode).filter(StoryNode.novel_id == n.id).count()
            data_list.append({
                "id": n.id,
                "title": n.title,
                "pen_name": n.pen_name,
                "description": n.description,
                "cover_url": n.cover_url,
                "userId": n.user_id,
                "char_count": char_count,
                "node_count": node_count,
                "relation_count": 0,
                "createTime": self._dt(n.create_time),
                "updateTime": self._dt(n.update_time),
            })
        return Result.success("获取成功", {
            "records": data_list,
            "total": total,
            "size": page_size,
            "current": page,
            "pages": (total + page_size - 1) // page_size,
        })

    def get_by_id(self, novel_id: int) -> dict:
        novel = self.db.query(Novels).filter(Novels.id == novel_id).first()
        if not novel:
            return Result.error("小说不存在")
        char_count = self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel.id).count()
        node_count = self.db.query(StoryNode).filter(StoryNode.novel_id == novel.id).count()
        data = {
            "id": novel.id,
            "title": novel.title,
            "pen_name": novel.pen_name,
            "description": novel.description,
            "cover_url": novel.cover_url,
            "userId": novel.user_id,
            "char_count": char_count,
            "node_count": node_count,
            "relation_count": 0,
            "createTime": self._dt(novel.create_time),
            "updateTime": self._dt(novel.update_time),
        }
        return Result.success("获取成功", data)

    def create(self, user_id: int, req: NovelCreate) -> dict:
        exists = self.db.query(Novels).filter(Novels.user_id == user_id, Novels.title == req.title).first()
        if exists:
            return Result.error(f"当前用户已存在标题为【{req.title}】的小说，请勿重复创建")
        novel = Novels(
            user_id=user_id,
            title=req.title,
            pen_name=req.pen_name,
            description=req.description,
            cover_url=req.cover_url,
        )
        self.db.add(novel)
        self.db.commit()
        self.db.refresh(novel)
        data = {
            "id": novel.id,
            "title": novel.title,
            "pen_name": novel.pen_name,
            "description": novel.description,
            "cover_url": novel.cover_url,
            "userId": novel.user_id,
            "char_count": 0,
            "node_count": 0,
            "relation_count": 0,
            "createTime": self._dt(novel.create_time),
            "updateTime": self._dt(novel.update_time),
        }
        return Result.success("创建成功", data)

    def update(self, user_id: int, novel_id: int, req: NovelUpdate) -> dict:
        novel = self.db.query(Novels).filter(Novels.id == novel_id).first()
        if not novel:
            return Result.error("小说不存在")
        if novel.user_id != user_id:
            return Result.error("无权修改该小说")
        if req.title is not None:
            novel.title = req.title
        if req.pen_name is not None:
            novel.pen_name = req.pen_name
        if req.description is not None:
            novel.description = req.description
        if req.cover_url is not None:
            old_cover = novel.cover_url
            novel.cover_url = req.cover_url
            if old_cover and old_cover.startswith("/api/uploads/"):
                delete_file_by_url(old_cover)
        self.db.commit()
        self.db.refresh(novel)
        char_count = self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel.id).count()
        node_count = self.db.query(StoryNode).filter(StoryNode.novel_id == novel.id).count()
        data = {
            "id": novel.id,
            "title": novel.title,
            "pen_name": novel.pen_name,
            "description": novel.description,
            "cover_url": novel.cover_url,
            "userId": novel.user_id,
            "char_count": char_count,
            "node_count": node_count,
            "relation_count": 0,
            "createTime": self._dt(novel.create_time),
            "updateTime": self._dt(novel.update_time),
        }
        return Result.success("更新成功", data)

    def delete(self, user_id: int, novel_id: int) -> dict:
        novel = self.db.query(Novels).filter(Novels.id == novel_id).first()
        if not novel:
            return Result.error("小说不存在")
        if novel.user_id != user_id:
            return Result.error("无权删除该小说")
        if novel.cover_url and novel.cover_url.startswith("/api/uploads/"):
            delete_file_by_url(novel.cover_url)
        self.db.query(StoryNode).filter(StoryNode.novel_id == novel_id).delete()
        self.db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel_id).delete()
        self.db.query(NovelRelation).filter(NovelRelation.novel_id == novel_id).delete()
        self.db.query(Timeline).filter(Timeline.novel_id == novel_id).delete()
        self.db.delete(novel)
        self.db.commit()
        return Result.success("删除成功", None)
