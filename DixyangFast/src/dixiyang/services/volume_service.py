from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.volume import Volume
from ..schemas.volume import VolumeCreate, VolumeUpdate
from ..utils.database import get_db
from ..utils.response import Result


class VolumeService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _to_vo(self, v: Volume) -> dict:
        return {
            "id": v.id,
            "novel_id": v.novel_id,
            "title": v.title,
            "sort_order": v.sort_order,
            "description": v.description,
            "create_time": v.create_time.isoformat() if v.create_time else None,
            "update_time": v.update_time.isoformat() if v.update_time else None,
        }

    def _check_novel_access(self, novel_id: int, user_id: int) -> str | None:
        from ..models.novel import Novels
        novel = self.db.query(Novels).filter(Novels.id == novel_id).first()
        if not novel:
            return "小说不存在"
        if novel.user_id != user_id:
            return "无权操作该小说"
        return None

    def list_volumes(self, novel_id: int, user_id: int) -> dict:
        err = self._check_novel_access(novel_id, user_id)
        if err:
            return Result.error(err)
        volumes = self.db.query(Volume).filter(Volume.novel_id == novel_id).order_by(Volume.sort_order).all()
        return Result.success("获取成功", [self._to_vo(v) for v in volumes])

    def get_volume(self, volume_id: int, user_id: int) -> dict:
        v = self.db.query(Volume).filter(Volume.id == volume_id).first()
        if not v:
            return Result.error("卷不存在")
        err = self._check_novel_access(v.novel_id, user_id)
        if err:
            return Result.error(err)
        return Result.success("获取成功", self._to_vo(v))

    def create_volume(self, novel_id: int, req: VolumeCreate, user_id: int) -> dict:
        err = self._check_novel_access(novel_id, user_id)
        if err:
            return Result.error(err)
        max_order = self.db.query(Volume.sort_order).filter(Volume.novel_id == novel_id).order_by(Volume.sort_order.desc()).first()
        next_order = (max_order[0] + 1) if max_order else 1
        v = Volume(
            novel_id=novel_id,
            title=req.title,
            sort_order=req.sort_order or next_order,
            description=req.description,
        )
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return Result.success("创建成功", self._to_vo(v))

    def update_volume(self, volume_id: int, req: VolumeUpdate, user_id: int) -> dict:
        v = self.db.query(Volume).filter(Volume.id == volume_id).first()
        if not v:
            return Result.error("卷不存在")
        err = self._check_novel_access(v.novel_id, user_id)
        if err:
            return Result.error(err)
        if req.title is not None:
            v.title = req.title
        if req.sort_order is not None:
            v.sort_order = req.sort_order
        if req.description is not None:
            v.description = req.description
        self.db.commit()
        self.db.refresh(v)
        return Result.success("更新成功", self._to_vo(v))

    def delete_volume(self, volume_id: int, user_id: int) -> dict:
        v = self.db.query(Volume).filter(Volume.id == volume_id).first()
        if not v:
            return Result.error("卷不存在")
        err = self._check_novel_access(v.novel_id, user_id)
        if err:
            return Result.error(err)
        # 卷下章节改为无卷，不删除章节
        from ..models.chapter import Chapter
        self.db.query(Chapter).filter(Chapter.volume_id == volume_id).update({"volume_id": None})
        self.db.delete(v)
        self.db.commit()
        return Result.success("删除成功", None)

    def reorder_volumes(self, novel_id: int, volume_ids: list[int], user_id: int) -> dict:
        err = self._check_novel_access(novel_id, user_id)
        if err:
            return Result.error(err)
        for idx, vid in enumerate(volume_ids):
            v = self.db.query(Volume).filter(Volume.id == vid, Volume.novel_id == novel_id).first()
            if v:
                v.sort_order = idx + 1
        self.db.commit()
        return Result.success("排序成功", None)
