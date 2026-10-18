"""管理后台内容管理：广场帖子（列表/详情/下架恢复/硬删除/评论）+ 灵感墙便签（列表/删除）

- 全部由 /api/admin/* 路由调用（require_admin 后台会话鉴权）
- 硬删除做级联清理：附件文件、正文文件、本地上传配图文件、评论/点赞/收藏/标签行
- 平台下架置 admin_removed=1（作者侧 restore 已拦截），管理端恢复清 0
"""
import logging
import os

from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR
from ..models.idea import (
    IdeaAttachment, IdeaCollect, IdeaComment, IdeaLike, IdeaPost, IdeaPostImage, IdeaPostTag,
)
from ..models.sticky import StickyNote
from ..models.user import AppUser
from ..utils.database import get_db
from ..utils.response import Result
from .idea_cache import cache
from .idea_export import delete_community_json, read_community_json
from .idea_service import CATEGORIES, HOT_W, IMG_URL_PREFIX, IdeaService
from .sticky_service import _load_body as sticky_load_body
from .sticky_service import _subdir as sticky_subdir
from .storage_service import delete_json

log = logging.getLogger(__name__)

PAGE_SIZE = 20


class AdminContentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ---------- 公共 ----------

    def _user_names(self, ids: set[int]) -> dict[int, str]:
        if not ids:
            return {}
        rows = self.db.query(AppUser.id, AppUser.username, AppUser.nickname).filter(
            AppUser.id.in_(ids)
        ).all()
        return {r[0]: (r[2] or r[1] or f"用户{r[0]}") for r in rows}

    # ---------- 广场帖子 ----------

    def list_posts(self, page: int, page_size: int, status: str | None,
                   category: str | None, keyword: str | None) -> dict:
        q = self.db.query(IdeaPost)
        if status in ("published", "removed"):
            q = q.filter(IdeaPost.status == status)
        if category in CATEGORIES:
            q = q.filter(IdeaPost.category == category)
        if keyword:
            like = f"%{keyword.strip()}%"
            q = q.filter(or_(IdeaPost.title.like(like), IdeaPost.summary.like(like)))
        total = q.count()
        rows = q.order_by(IdeaPost.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        names = self._user_names({p.user_id for p in rows})
        return Result.success("获取成功", {
            "total": total,
            "list": [self._post_item(p, names) for p in rows],
        })

    def get_post(self, post_id: int) -> dict:
        p = self.db.get(IdeaPost, post_id)
        if p is None:
            return Result.error("帖子不存在")
        names = self._user_names({p.user_id})
        body = read_community_json(p.body_path)
        data = body if isinstance(body, dict) else {}
        images = [
            r.url for r in self.db.query(IdeaPostImage)
            .filter(IdeaPostImage.post_id == post_id).order_by(IdeaPostImage.sort).all()
        ]
        tags = [
            r.tag for r in self.db.query(IdeaPostTag)
            .filter(IdeaPostTag.post_id == post_id).all()
        ]
        attach = self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id == post_id).first()
        item = self._post_item(p, names)
        item.update({
            "content": data.get("content", ""),
            "images": images,
            "tags": tags,
            "attachment": {"type": attach.type, "meta": attach.attach_meta} if attach else None,
            "updateTime": p.update_time.strftime("%Y-%m-%d %H:%M:%S") if p.update_time else "",
        })
        return Result.success("获取成功", item)

    def _post_item(self, p: IdeaPost, names: dict[int, str]) -> dict:
        return {
            "id": p.id,
            "category": p.category,
            "title": p.title,
            "summary": p.summary,
            "authorId": p.user_id,
            "authorName": names.get(p.user_id, f"用户{p.user_id}"),
            "status": p.status,
            "adminRemoved": bool(getattr(p, "admin_removed", 0)),
            "viewCount": p.view_count,
            "likeCount": p.like_count,
            "commentCount": p.comment_count,
            "collectCount": p.collect_count,
            "createTime": p.create_time.strftime("%Y-%m-%d %H:%M:%S") if p.create_time else "",
        }

    def set_post_status(self, post_id: int, status: str) -> dict:
        if status not in ("published", "removed"):
            return Result.error("状态只能是 published 或 removed")
        p = self.db.get(IdeaPost, post_id)
        if p is None:
            return Result.error("帖子不存在")
        if status == "removed":
            p.status = "removed"
            p.admin_removed = 1  # 平台下架：作者不可自行恢复
        else:
            p.status = "published"
            p.admin_removed = 0
        self.db.commit()
        return Result.success("已下架" if status == "removed" else "已恢复上架", {
            "id": p.id, "status": p.status, "adminRemoved": bool(p.admin_removed),
        })

    def delete_post(self, post_id: int) -> dict:
        """硬删除：级联清理附件/正文/配图文件 + 评论/点赞/收藏/标签行"""
        p = self.db.get(IdeaPost, post_id)
        if p is None:
            return Result.error("帖子不存在")

        for a in self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id == post_id).all():
            delete_community_json(a.attach_path)
            self.db.delete(a)
        for img in self.db.query(IdeaPostImage).filter(IdeaPostImage.post_id == post_id).all():
            self._delete_image_file(img.url)
            self.db.delete(img)
        delete_community_json(p.body_path)

        self.db.query(IdeaComment).filter(IdeaComment.post_id == post_id).delete()
        self.db.query(IdeaLike).filter(IdeaLike.post_id == post_id).delete()
        self.db.query(IdeaCollect).filter(IdeaCollect.post_id == post_id).delete()
        self.db.query(IdeaPostTag).filter(IdeaPostTag.post_id == post_id).delete()
        self.db.delete(p)
        self.db.commit()
        return Result.success("已删除")

    @staticmethod
    def _delete_image_file(url: str | None) -> None:
        """仅清本地上传目录（/api/uploads/idea-images/）的配图文件，外链/异常路径不动"""
        if not url or not url.startswith(IMG_URL_PREFIX):
            return
        name = url[len(IMG_URL_PREFIX):]
        if not name or "/" in name or "\\" in name or ".." in name:
            return
        path = os.path.join(UPLOAD_DIR, "idea-images", name)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            log.warning("删除帖子配图文件失败: %s", path)

    # ---------- 评论 ----------

    def list_comments(self, post_id: int, page: int, page_size: int) -> dict:
        q = self.db.query(IdeaComment).filter(IdeaComment.post_id == post_id)
        total = q.count()
        rows = q.order_by(IdeaComment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        names = self._user_names({c.user_id for c in rows})
        return Result.success("获取成功", {
            "total": total,
            "list": [{
                "id": c.id,
                "postId": c.post_id,
                "authorId": c.user_id,
                "authorName": names.get(c.user_id, f"用户{c.user_id}"),
                "content": c.content,
                "createTime": c.create_time.strftime("%Y-%m-%d %H:%M:%S") if c.create_time else "",
            } for c in rows],
        })

    def delete_comment(self, comment_id: int) -> dict:
        c = self.db.get(IdeaComment, comment_id)
        if c is None:
            return Result.error("评论不存在")
        p = self.db.get(IdeaPost, c.post_id)
        if p:
            p.comment_count = max(0, p.comment_count - 1)
            IdeaService(self.db)._recompute_hot(p)
        self.db.delete(c)
        self.db.commit()
        cache.hot_zincr(c.post_id, -HOT_W["comment"])
        return Result.success("已删除")

    # ---------- 灵感墙便签 ----------

    def list_sticky(self, page: int, page_size: int, keyword: str | None,
                    done: bool | None) -> dict:
        q = self.db.query(StickyNote)
        if keyword:
            like = f"%{keyword.strip()}%"
            q = q.join(AppUser, AppUser.id == StickyNote.user_id).filter(
                or_(AppUser.username.like(like), AppUser.nickname.like(like))
            )
        if done is not None:
            q = q.filter(StickyNote.done == (1 if done else 0))
        total = q.count()
        rows = q.order_by(StickyNote.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        names = self._user_names({r.user_id for r in rows})
        out = []
        for r in rows:
            body = sticky_load_body(r)
            out.append({
                "id": r.id,
                "userId": r.user_id,
                "userName": names.get(r.user_id, f"用户{r.user_id}"),
                "color": r.color,
                "done": bool(r.done),
                "inPool": bool(r.in_pool),
                "content": body["content"],
                "images": body["images"],
                "createTime": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else "",
                "updateTime": r.update_time.strftime("%Y-%m-%d %H:%M:%S") if r.update_time else "",
            })
        return Result.success("获取成功", {"total": total, "list": out})

    def delete_sticky(self, note_id: int) -> dict:
        r = self.db.get(StickyNote, note_id)
        if r is None:
            return Result.error("便签不存在")
        delete_json(sticky_subdir(r.user_id), r.id, r.content_path)  # 项目惯例：先删文件后删行
        self.db.delete(r)
        self.db.commit()
        return Result.success("已删除")
