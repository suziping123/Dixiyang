from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.chapter import Chapter
from ..schemas.chapter import ChapterCreate, ChapterUpdate
from ..utils.database import get_db
from ..utils.response import Result


class ChapterService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    def _to_vo(self, c: Chapter) -> dict:
        return {
            "id": c.id,
            "novel_id": c.novel_id,
            "volume_id": c.volume_id,
            "title": c.title,
            "sort_order": c.sort_order,
            "content_path": c.content_path,
            "content_hash": c.content_hash,
            "content_size": c.content_size,
            "version": c.version,
            "local_version": c.local_version,
            "word_count": c.word_count,
            "create_time": self._dt(c.create_time),
            "update_time": self._dt(c.update_time),
        }

    def _check_novel_access(self, novel_id: int, user_id: int) -> str | None:
        from ..models.novel import Novels
        novel = self.db.query(Novels).filter(Novels.id == novel_id).first()
        if not novel:
            return "小说不存在"
        if novel.user_id != user_id:
            return "无权操作该小说"
        return None

    def get_owned_chapter(self, chapter_id: int, user_id: int) -> dict:
        """按 id 查章节并校验归属，越权/不存在返回错误 Result"""
        c = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not c:
            return Result.error("章节不存在")
        err = self._check_novel_access(c.novel_id, user_id)
        if err:
            return Result.error(err)
        return Result.success("获取成功", self._to_vo(c))

    def list_chapters(self, novel_id: int, user_id: int) -> dict:
        err = self._check_novel_access(novel_id, user_id)
        if err:
            return Result.error(err)
        chapters = (
            self.db.query(Chapter)
            .filter(Chapter.novel_id == novel_id)
            .order_by(Chapter.volume_id.is_(None).desc(), Chapter.volume_id, Chapter.sort_order)
            .all()
        )
        return Result.success("获取成功", [self._to_vo(c) for c in chapters])

    def get_chapter(self, chapter_id: int, user_id: int) -> dict:
        return self.get_owned_chapter(chapter_id, user_id)

    def create_chapter(self, user_id: int, req: ChapterCreate) -> dict:
        from ..models.novel import Novels
        novel = self.db.query(Novels).filter(Novels.id == req.novel_id).first()
        if not novel:
            return Result.error("小说不存在")
        if novel.user_id != user_id:
            return Result.error("无权操作该小说")

        next_order = self._next_sort_order(req.novel_id, req.volume_id)
        c = Chapter(
            novel_id=req.novel_id,
            volume_id=req.volume_id,
            title=req.title,
            sort_order=req.sort_order or next_order,
        )
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return Result.success("创建成功", self._to_vo(c))

    def update_chapter(self, user_id: int, chapter_id: int, req: ChapterUpdate) -> dict:
        c = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not c:
            return Result.error("章节不存在")
        err = self._check_novel_access(c.novel_id, user_id)
        if err:
            return Result.error(err)
        if req.title is not None:
            c.title = req.title
        if req.sort_order is not None:
            c.sort_order = req.sort_order
        if req.volume_id is not None:
            c.volume_id = req.volume_id
        self.db.commit()
        self.db.refresh(c)
        return Result.success("更新成功", self._to_vo(c))

    def delete_chapter(self, user_id: int, chapter_id: int) -> dict:
        c = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not c:
            return Result.error("章节不存在")
        err = self._check_novel_access(c.novel_id, user_id)
        if err:
            return Result.error(err)

        # 删除正文文件
        if c.content_path:
            from .chapter_content_service import ChapterContentService
            ChapterContentService.delete_content(c.content_path)

        self.db.delete(c)
        self.db.commit()
        return Result.success("删除成功", None)

    def reorder_chapters(self, novel_id: int, chapter_ids: list[int], user_id: int) -> dict:
        err = self._check_novel_access(novel_id, user_id)
        if err:
            return Result.error(err)
        for idx, cid in enumerate(chapter_ids):
            c = self.db.query(Chapter).filter(Chapter.id == cid, Chapter.novel_id == novel_id).first()
            if c:
                c.sort_order = idx + 1
        self.db.commit()
        return Result.success("排序成功", None)

    def _next_sort_order(self, novel_id: int, volume_id: int | None) -> int:
        q = self.db.query(Chapter.sort_order).filter(Chapter.novel_id == novel_id)
        if volume_id:
            q = q.filter(Chapter.volume_id == volume_id)
        else:
            q = q.filter(Chapter.volume_id.is_(None))
        row = q.order_by(Chapter.sort_order.desc()).first()
        return (row[0] + 1) if row else 1
