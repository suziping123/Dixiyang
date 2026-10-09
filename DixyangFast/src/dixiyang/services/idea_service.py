"""点子库核心业务：草稿/发布/帖子/附件/互动/评论/导入（Demo 版：计数与排序直读 DB，Redis 层预留）"""
import json
import logging
import math
import os
import time
from collections import Counter
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy import and_, exists, func, or_
from sqlalchemy.orm import Session

from ..models.idea import (
    IdeaAttachment, IdeaCollect, IdeaComment, IdeaDraft, IdeaLike, IdeaPost, IdeaPostImage, IdeaPostTag,
)
from ..models.user import AppUser
from ..schemas.idea import CommentCreate, DraftCreate, DraftUpdate, ImportRequest, PostUpdate, PublishRequest
from ..utils.database import get_db
from ..utils.response import Result
from .idea_export import (
    delete_community_json, export_character_cards, export_chat_snapshot,
    import_character_cards, read_community_json, write_community_json,
)
from .idea_cache import cache
from .storage_service import STORAGE_ROOT

log = logging.getLogger(__name__)

CATEGORIES = {"idea", "character", "setting", "timeline", "tech"}
# 分区 → 允许的附件类型（None = 纯文字）
CATEGORY_ATTACH = {
    "idea": "chat_snapshot",
    "character": "character_card",
    "setting": "setting_bundle",
    "timeline": "timeline_view",
    "tech": None,
}
PAGE_SIZE = 10
TAG_MAX, TAG_LEN_MAX = 5, 50
IMG_MAX = 9
IMG_URL_PREFIX = "/api/uploads/idea-images/"
COMMENT_LEN_MAX = 1000

# 热度事件权重（与 hot_score 公式一致：3赞+2藏+2评+1浏览）
HOT_W = {"like": 3.0, "collect": 2.0, "comment": 2.0, "view": 1.0}
HOT_TOP_MAX = 200  # sort=hot 时从 ZSET 预取的深水区上限

# 内存频控（Redis 降级兜底；正常态走 idea:rl:* TTL）
_rate: dict[str, float] = {}


def _limit_check(scope: str, uid: int, seconds: float) -> float:
    """只读频控检查：0 = 放行；>0 = 剩余秒（Redis 优先，降级内存 dict）"""
    remain = cache.rate_check(scope, uid, seconds)
    if cache.healthy():
        return remain
    now = time.monotonic()
    last = _rate.get(f"{scope}:{uid}")
    if last is not None and now - last < seconds:
        return seconds - (now - last)
    return 0.0


def _limit_mark(scope: str, uid: int, seconds: float) -> None:
    """操作成功后打点；业务失败不消耗额度"""
    if cache.rate_mark(scope, uid, seconds):
        _rate.pop(f"{scope}:{uid}", None)
        return
    _rate[f"{scope}:{uid}"] = time.monotonic()


class IdeaService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ---------- 内部工具 ----------

    @staticmethod
    def _dt(val):
        return val.isoformat() if val else None

    @staticmethod
    def _summary(content: str) -> str:
        return content.replace("\n", " ").strip()[:300]

    @staticmethod
    def _norm_tags(tags: list[str] | None) -> list[str]:
        out = []
        for t in tags or []:
            t = t.strip()[:TAG_LEN_MAX]
            if t and t not in out:
                out.append(t)
        return out[:TAG_MAX]

    @staticmethod
    def _clean_images(images: list[str] | None) -> list[str]:
        """仅保留本服务 idea-images 目录下的 URL，最多 IMG_MAX 张（防伪造外链）"""
        out = []
        for u in images or []:
            u = (u or "").strip()[:500]
            if u.startswith(IMG_URL_PREFIX) and u not in out:
                out.append(u)
        return out[:IMG_MAX]

    @staticmethod
    def _write_body(rel_path: str, data: dict) -> str:
        return write_community_json(rel_path, data)

    @staticmethod
    def _read_body(db_value: str | None) -> dict:
        data = read_community_json(db_value)
        return data if isinstance(data, dict) else {}

    def _recompute_hot(self, p: IdeaPost):
        """hot = 3赞+2收藏+2评论+1浏览（Demo 直算；正式版走 Redis ZSET）"""
        p.hot_score = 3 * p.like_count + 2 * p.collect_count + 2 * p.comment_count + p.view_count

    def _user_name(self, uid: int) -> tuple[str, str | None]:
        u = self.db.get(AppUser, uid)
        if u is None:
            return "未知用户", None
        return (u.nickname or u.username), u.email  # Demo：avatar 待 app_user 扩展，前端首字母占位

    def _tags_of(self, post_ids: list[int]) -> dict[int, list[str]]:
        if not post_ids:
            return {}
        rows = self.db.query(IdeaPostTag.post_id, IdeaPostTag.tag).filter(
            IdeaPostTag.post_id.in_(post_ids)
        ).all()
        m: dict[int, list[str]] = {pid: [] for pid in post_ids}
        for pid, tag in rows:
            m.setdefault(pid, []).append(tag)
        return m

    def _attachments_of(self, post_ids: list[int]) -> dict[int, dict]:
        if not post_ids:
            return {}
        rows = self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id.in_(post_ids)).all()
        out = {}
        for a in rows:
            try:
                meta = json.loads(a.attach_meta) if a.attach_meta else {}
            except json.JSONDecodeError:
                meta = {}
            out[a.post_id] = {"type": a.type, "sourceRef": a.source_ref, **meta}
        return out

    def _liked_set(self, user_id: int | None, post_ids: list[int]) -> set[int]:
        if not user_id or not post_ids:
            return set()
        rows = self.db.query(IdeaLike.post_id).filter(
            IdeaLike.user_id == user_id, IdeaLike.post_id.in_(post_ids)
        ).all()
        return {r[0] for r in rows}

    def _collected_set(self, user_id: int | None, post_ids: list[int]) -> set[int]:
        if not user_id or not post_ids:
            return set()
        rows = self.db.query(IdeaCollect.post_id).filter(
            IdeaCollect.user_id == user_id, IdeaCollect.post_id.in_(post_ids)
        ).all()
        return {r[0] for r in rows}

    def _images_of(self, post_ids: list[int]) -> dict[int, list[str]]:
        if not post_ids:
            return {}
        rows = self.db.query(IdeaPostImage).filter(
            IdeaPostImage.post_id.in_(post_ids)
        ).order_by(IdeaPostImage.sort.asc(), IdeaPostImage.id.asc()).all()
        m: dict[int, list[str]] = {pid: [] for pid in post_ids}
        for r in rows:
            m.setdefault(r.post_id, []).append(r.url)
        return m

    def _post_item(self, p: IdeaPost, tag_map: dict, att_map: dict, liked: set,
                    with_content: bool = False, img_map: dict | None = None,
                    collected: set | None = None) -> dict:
        name, _ = self._user_name(p.user_id)
        imgs = (img_map or {}).get(p.id) or []
        item = {
            "id": p.id,
            "category": p.category,
            "title": p.title,
            "summary": p.summary,
            "authorId": p.user_id,
            "authorName": name,
            "tags": tag_map.get(p.id, []),
            "attach": att_map.get(p.id),
            "images": imgs,
            "coverUrl": imgs[0] if imgs else None,
            "status": p.status,
            "viewCount": p.view_count,
            "likeCount": p.like_count,
            "commentCount": p.comment_count,
            "collectCount": p.collect_count,
            "likedByMe": p.id in liked,
            "collectedByMe": p.id in (collected or set()),
            "createTime": self._dt(p.create_time),
        }
        if with_content:
            item["content"] = self._read_body(p.body_path).get("content", "")
        return item

    # ---------- 草稿 ----------

    def create_draft(self, user_id: int, req: DraftCreate) -> dict:
        if req.category not in CATEGORIES:
            return Result.error("无效分区")
        if not req.title.strip():
            return Result.error("标题不能为空")
        d = IdeaDraft(
            user_id=user_id, category=req.category, title=req.title.strip()[:200],
            summary=self._summary(req.content), body_path="", source_ref=req.source_ref,
        )
        self.db.add(d)
        self.db.flush()
        d.body_path = self._write_body(
            f"community/{user_id}/draft_{d.id}.json",
            {
                "title": req.title, "content": req.content,
                "tags": self._norm_tags(req.tags), "images": self._clean_images(req.images),
            },
        )
        self.db.commit()
        return Result.success("创建成功", {"id": d.id})

    def update_draft(self, user_id: int, draft_id: int, req: DraftUpdate) -> dict:
        d = self._own_draft(user_id, draft_id)
        if d is None:
            return Result.error("草稿不存在")
        if req.category not in CATEGORIES:
            return Result.error("无效分区")
        body = {
            "title": req.title, "content": req.content,
            "tags": self._norm_tags(req.tags), "images": self._clean_images(req.images),
        }
        delete_community_json(d.body_path)
        d.category = req.category
        d.title = req.title.strip()[:200]
        d.summary = self._summary(req.content)
        d.source_ref = req.source_ref
        d.body_path = self._write_body(f"community/{user_id}/draft_{d.id}.json", body)
        self.db.commit()
        return Result.success("保存成功")

    def delete_draft(self, user_id: int, draft_id: int) -> dict:
        d = self._own_draft(user_id, draft_id)
        if d is None:
            return Result.error("草稿不存在")
        delete_community_json(d.body_path)
        self.db.delete(d)
        self.db.commit()
        return Result.success("删除成功")

    def get_draft(self, user_id: int, draft_id: int) -> dict:
        d = self._own_draft(user_id, draft_id)
        if d is None:
            return Result.error("草稿不存在")
        body = self._read_body(d.body_path)
        return Result.success("获取成功", {
            "id": d.id, "category": d.category, "title": d.title,
            "content": body.get("content", ""), "tags": body.get("tags", []),
            "images": body.get("images", []),
            "sourceRef": d.source_ref, "updateTime": self._dt(d.update_time),
        })

    def list_drafts(self, user_id: int, category: str | None, q: str | None, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaDraft).filter(IdeaDraft.user_id == user_id)
        if category in CATEGORIES:
            query = query.filter(IdeaDraft.category == category)
        if q:
            query = query.filter(IdeaDraft.title.like(f"%{q}%"))
        total = query.count()
        rows = query.order_by(IdeaDraft.update_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return Result.success("获取成功", {
            "total": total,
            "list": [{
                "id": d.id, "category": d.category, "title": d.title, "summary": d.summary,
                "sourceRef": d.source_ref, "updateTime": self._dt(d.update_time),
            } for d in rows],
        })

    def _own_draft(self, user_id: int, draft_id: int) -> IdeaDraft | None:
        return self.db.query(IdeaDraft).filter(
            IdeaDraft.id == draft_id, IdeaDraft.user_id == user_id
        ).first()

    # ---------- 发布 ----------

    def publish(self, user_id: int, draft_id: int, req: PublishRequest) -> dict:
        if not req.previewed:
            return Result.error("请先预览附件")
        remain = _limit_check("pub", user_id, 10)
        if remain:
            return Result.error(f"发布太频繁了，请 {int(remain) + 1} 秒后再试")
        d = self._own_draft(user_id, draft_id)
        if d is None:
            return Result.error("草稿不存在")
        body = self._read_body(d.body_path)
        content = body.get("content", "")
        tags = self._norm_tags(body.get("tags"))

        p = IdeaPost(
            user_id=user_id, category=d.category, title=d.title,
            summary=self._summary(content), body_path="",
        )
        self.db.add(p)
        self.db.flush()
        p.body_path = self._write_body(
            f"community/{user_id}/{p.id}.json",
            {"title": body.get("title", d.title), "content": content, "tags": tags},
        )

        # 结构化附件（按分区 + 数据源引用）
        attach, err = self._build_attachment(user_id, p.id, d.category, d.source_ref)
        if err:
            delete_community_json(p.body_path)
            self.db.delete(p)
            self.db.commit()
            return Result.error(err)

        for t in tags:
            self.db.add(IdeaPostTag(post_id=p.id, tag=t))

        for i, u in enumerate(self._clean_images(body.get("images"))):
            self.db.add(IdeaPostImage(post_id=p.id, url=u, sort=i))

        delete_community_json(d.body_path)
        self.db.delete(d)
        self.db.commit()
        _limit_mark("pub", user_id, 10)
        return Result.success("发布成功", {"postId": p.id, "attach": attach})

    def _build_attachment(self, user_id: int, post_id: int, category: str,
                          source_ref: str | None) -> tuple[dict | None, str | None]:
        need_type = CATEGORY_ATTACH.get(category)
        if need_type is None:
            return None, None  # tech 区纯文字
        if not source_ref:
            return None, None  # 数据源可选，不选则纯文字帖
        if need_type == "chat_snapshot":
            data, err = export_chat_snapshot(user_id, source_ref)
        elif need_type == "character_card":
            try:
                ids = [int(x) for x in source_ref.split(",") if x.strip()]
            except ValueError:
                return None, "角色数据源无效"
            if not ids:
                return None, "角色数据源无效"
            data, err = export_character_cards(self.db, user_id, ids)
        else:
            return None, None  # setting/timeline 附件导出为后续迭代，暂按纯文字
        if err or not data:
            return None, err or "附件导出失败"
        attach_path = self._write_body(f"community/{user_id}/{post_id}/attach_{need_type}.json", data)
        if need_type == "chat_snapshot":
            meta = {"rounds": (data.get("totalMessages", 0) + 1) // 2, "truncated": data.get("truncated", False)}
        else:
            meta = {"characterNames": [c.get("name") for c in data.get("characters", [])]}
        a = IdeaAttachment(
            post_id=post_id, type=need_type, attach_path=attach_path,
            attach_meta=json.dumps(meta, ensure_ascii=False), source_ref=source_ref,
        )
        self.db.add(a)
        self.db.flush()
        return {"id": a.id, "type": a.type, **meta}, None

    # ---------- 帖子列表/详情 ----------

    def _user_taste_tags(self, user_id: int) -> Counter:
        """轻量 Item-CF 近似：取用户赞/藏过的帖的标签作为兴趣画像（权重 藏>赞）"""
        pairs = (
            self.db.query(IdeaPostTag.post_id, IdeaPostTag.tag, IdeaLike.post_id.label("lk"))
            .join(IdeaLike, IdeaLike.post_id == IdeaPostTag.post_id)
            .filter(IdeaLike.user_id == user_id).all()
        )
        c: Counter = Counter()
        for row in pairs:
            c[row.tag] += 2  # 点赞
        pairs2 = (
            self.db.query(IdeaPostTag.post_id, IdeaPostTag.tag, IdeaCollect.post_id.label("cc"))
            .join(IdeaCollect, IdeaCollect.post_id == IdeaPostTag.post_id)
            .filter(IdeaCollect.user_id == user_id).all()
        )
        for row in pairs2:
            c[row.tag] += 3  # 收藏权重更高
        return c

    def _recommend_rows(self, query, user_id: int | None, page: int, page_size: int) -> list:
        """综合推荐 = Redis 热度(与热门同源) × 时间衰减 + 兴趣标签加成（与 最新/热门 拉开区分度）"""
        since = datetime.now() - timedelta(days=14)
        cand = query.order_by(IdeaPost.id.desc()).limit(HOT_TOP_MAX).all()
        seen = {p.id for p in cand}
        fresh = (
            query.filter(IdeaPost.create_time >= since)
            .order_by(IdeaPost.create_time.desc()).limit(200).all()
        )
        cand.extend(p for p in fresh if p.id not in seen)
        hot_map = {pid: s for pid, s in (cache.hot_top_scores(HOT_TOP_MAX) or [])}  # ZSET 分数（回写滞后时仍有效）
        taste = self._user_taste_tags(user_id) if user_id else Counter()
        tag_map = self._tags_of([p.id for p in cand]) if taste else {}
        now = datetime.now()

        def score(p: IdeaPost) -> float:
            hours = max(0.0, (now - (p.create_time or now)).total_seconds() / 3600.0)
            decay = 1.0 / (1.0 + hours / 48.0) ** 1.0  # 48h 衰减，比热门更"保鲜"
            hot = float(hot_map.get(p.id, p.hot_score or 0)) + 3.0  # +3 平滑零互动新帖
            aff = sum(min(taste.get(t, 0), 6) for t in tag_map.get(p.id, [])) * 1.5
            return hot * decay + aff

        cand.sort(key=score, reverse=True)
        return cand[(page - 1) * page_size: page * page_size]

    def list_posts(self, user_id: int | None, category: str | None, sort: str,
                   q: str | None, tags: list[str] | None, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaPost).filter(IdeaPost.status == "published")
        if category in CATEGORIES:
            query = query.filter(IdeaPost.category == category)
        if q:
            like = f"%{q}%"
            query = query.filter(or_(IdeaPost.title.like(like), IdeaPost.summary.like(like)))
        for t in self._norm_tags(tags):
            query = query.filter(exists().where(
                and_(IdeaPostTag.post_id == IdeaPost.id, IdeaPostTag.tag == t)
            ))
        total = query.count()
        if sort == "recommend":
            rows = self._recommend_rows(query, user_id, page, page_size)
        elif sort == "hot":
            # Redis 热门榜优先（ZSET O(logN+M)）；无数据/降级回源 hot_score 全表排序
            ranked = cache.hot_top((page - 1) * page_size + page_size)
            if ranked:
                pos = {pid: i for i, pid in enumerate(ranked)}
                rows = [r for r in query.filter(IdeaPost.id.in_(pos)).all()]
                rows.sort(key=lambda r: pos.get(r.id, HOT_TOP_MAX))
                rows = rows[(page - 1) * page_size: page * page_size]
            else:
                rows = query.order_by(IdeaPost.hot_score.desc(), IdeaPost.id.desc()).offset(
                    (page - 1) * page_size
                ).limit(page_size).all()
        else:
            order = {
                "like": IdeaPost.like_count.desc(),
                "new": IdeaPost.create_time.desc(),
            }.get(sort, IdeaPost.create_time.desc())
            rows = query.order_by(order, IdeaPost.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
        ids = [p.id for p in rows]
        tag_map, att_map = self._tags_of(ids), self._attachments_of(ids)
        liked = self._liked_set(user_id, ids)
        collected = self._collected_set(user_id, ids)
        img_map = self._images_of(ids)
        return Result.success("获取成功", {
            "total": total,
            "list": [self._post_item(p, tag_map, att_map, liked, img_map=img_map, collected=collected) for p in rows],
        })

    def get_post(self, post_id: int, user_id: int | None) -> dict:
        p = self.db.get(IdeaPost, post_id)
        if p is None or (p.status != "published" and p.user_id != user_id):
            return Result.error("帖子不存在或已下架")
        if user_id is not None and cache.view_seen(p.id, user_id):
            pass  # 600s 内重复浏览：跳过计数（去重）
        elif cache.healthy():
            cache.view_incr(p.id)  # 增量暂存，60s 后台回写 DB
            cache.hot_zincr(p.id, HOT_W["view"])
        else:
            p.view_count += 1  # 降级：原行为，每次详情直写
            self._recompute_hot(p)
            self.db.commit()
        item = self._post_item(
            p, self._tags_of([p.id]), self._attachments_of([p.id]),
            self._liked_set(user_id, [p.id]), with_content=True,
            img_map=self._images_of([p.id]),
            collected=self._collected_set(user_id, [p.id]),
        )
        pending = cache.view_pending(p.id)
        if pending:  # 叠加未回写增量，详情页计数实时可见
            item["viewCount"] = (item.get("viewCount") or 0) + pending
        return Result.success("获取成功", item)

    def get_attachment(self, post_id: int, user_id: int | None) -> dict:
        p = self.db.get(IdeaPost, post_id)
        if p is None or (p.status != "published" and p.user_id != user_id):
            return Result.error("帖子不存在或已下架")
        a = self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id == post_id).first()
        if a is None:
            return Result.error("该帖子没有附件")
        data = read_community_json(a.attach_path)
        if data is None:
            return Result.error("附件文件缺失")
        return Result.success("获取成功", {"type": a.type, "data": data})

    def update_post(self, user_id: int, post_id: int, req: PostUpdate) -> dict:
        p = self._own_post(user_id, post_id)
        if p is None:
            return Result.error("帖子不存在")
        body = self._read_body(p.body_path)
        if req.title is not None:
            p.title = req.title.strip()[:200] or p.title
        if req.content is not None:
            body["content"] = req.content
            p.summary = self._summary(req.content)
        if req.tags is not None:
            body["tags"] = self._norm_tags(req.tags)
            self.db.query(IdeaPostTag).filter(IdeaPostTag.post_id == p.id).delete()
            for t in body["tags"]:
                self.db.add(IdeaPostTag(post_id=p.id, tag=t))
        if req.images is not None:
            body["images"] = self._clean_images(req.images)
            self.db.query(IdeaPostImage).filter(IdeaPostImage.post_id == p.id).delete()
            for i, u in enumerate(body["images"]):
                self.db.add(IdeaPostImage(post_id=p.id, url=u, sort=i))
        if req.source_ref is not None and CATEGORY_ATTACH.get(p.category):
            # 来源变更 → 重建附件快照（先建新、失败整体回滚保旧；成功再删旧行）
            new_ref = req.source_ref.strip()
            old = self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id == p.id).first()
            old_ref = (old.source_ref if old else "") or ""
            if new_ref != old_ref:
                attach, err = self._build_attachment(user_id, p.id, p.category, new_ref or None)
                if err:
                    self.db.rollback()
                    return Result.error(err)
                rows = self.db.query(IdeaAttachment).filter(
                    IdeaAttachment.post_id == p.id
                ).order_by(IdeaAttachment.id).all()
                if attach:
                    newest = rows[-1]
                    for r in rows[:-1]:  # 新行已 flush；删旧（同路径覆盖写时不删文件）
                        if r.attach_path != newest.attach_path:
                            delete_community_json(r.attach_path)
                        self.db.delete(r)
                elif rows:  # 新来源为空 → 仅移除附件
                    delete_community_json(rows[0].attach_path)
                    self.db.delete(rows[0])
        body["title"] = p.title
        delete_community_json(p.body_path)
        p.body_path = self._write_body(f"community/{user_id}/{p.id}.json", body)
        self.db.commit()
        return Result.success("保存成功")

    def remove_post(self, user_id: int, post_id: int) -> dict:
        """下架（软删，附件/评论保留，作者可见可再上架）"""
        p = self._own_post(user_id, post_id)
        if p is None:
            return Result.error("帖子不存在")
        p.status = "removed"
        self.db.commit()
        return Result.success("已下架")

    def restore_post(self, user_id: int, post_id: int) -> dict:
        p = self._own_post(user_id, post_id)
        if p is None:
            return Result.error("帖子不存在")
        p.status = "published"
        self.db.commit()
        return Result.success("已重新上架")

    def list_mine_posts(self, user_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaPost).filter(IdeaPost.user_id == user_id)
        total = query.count()
        rows = query.order_by(IdeaPost.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        ids = [p.id for p in rows]
        return Result.success("获取成功", {
            "total": total,
            "list": [self._post_item(p, self._tags_of(ids), self._attachments_of(ids), self._liked_set(user_id, ids), img_map=self._images_of(ids), collected=self._collected_set(user_id, ids)) for p in rows],
        })

    def _own_post(self, user_id: int, post_id: int) -> IdeaPost | None:
        return self.db.query(IdeaPost).filter(
            IdeaPost.id == post_id, IdeaPost.user_id == user_id
        ).first()

    # ---------- 附件导入 ----------

    def import_attachment(self, user_id: int, post_id: int, req: ImportRequest) -> dict:
        remain = _limit_check("imp", user_id, 10)
        if remain:
            return Result.error(f"导入太频繁了，请 {int(remain) + 1} 秒后再试")
        p = self.db.get(IdeaPost, post_id)
        if p is None or p.status != "published":
            return Result.error("帖子不存在或已下架")
        from ..models.novel import Novels
        novel = self.db.get(Novels, req.novel_id)
        if novel is None or novel.user_id != user_id:
            return Result.error("无权限导入到该小说")
        a = self.db.query(IdeaAttachment).filter(IdeaAttachment.post_id == post_id).first()
        if a is None or a.type != "character_card":
            return Result.error("仅角色卡附件支持导入")
        snapshot = read_community_json(a.attach_path)
        if not snapshot or not snapshot.get("characters"):
            return Result.error("附件内容缺失")
        results = import_character_cards(self.db, user_id, req.novel_id, snapshot)
        _limit_mark("imp", user_id, 10)
        return Result.success("导入成功", {"characters": results})

    # ---------- 互动 ----------

    def toggle_like(self, user_id: int, post_id: int) -> dict:
        p = self.db.get(IdeaPost, post_id)
        if p is None:
            return Result.error("帖子不存在或已下架")
        row = self.db.query(IdeaLike).filter(
            IdeaLike.user_id == user_id, IdeaLike.post_id == post_id
        ).first()
        if row:
            # 取消点赞：已下架帖也允许，避免悬空点赞无法移除
            self.db.delete(row)
            p.like_count = max(0, p.like_count - 1)
            liked, delta = False, -1
        elif p.status == "published":
            self.db.add(IdeaLike(user_id=user_id, post_id=post_id))
            p.like_count += 1
            liked, delta = True, 1
        else:
            return Result.error("帖子不存在或已下架")
        self._recompute_hot(p)
        self.db.commit()
        cache.hot_zincr(post_id, HOT_W["like"] * delta)
        return Result.success("操作成功", {"liked": liked, "likeCount": p.like_count})

    def toggle_collect(self, user_id: int, post_id: int) -> dict:
        p = self.db.get(IdeaPost, post_id)
        if p is None:
            return Result.error("帖子不存在或已下架")
        row = self.db.query(IdeaCollect).filter(
            IdeaCollect.user_id == user_id, IdeaCollect.post_id == post_id
        ).first()
        if row:
            # 取消收藏：已下架帖也允许，避免悬空收藏无法移除
            self.db.delete(row)
            p.collect_count = max(0, p.collect_count - 1)
            collected, delta = False, -1
        elif p.status == "published":
            self.db.add(IdeaCollect(user_id=user_id, post_id=post_id))
            p.collect_count += 1
            collected, delta = True, 1
        else:
            return Result.error("帖子不存在或已下架")
        self._recompute_hot(p)
        self.db.commit()
        cache.hot_zincr(post_id, HOT_W["collect"] * delta)
        return Result.success("操作成功", {"collected": collected, "collectCount": p.collect_count})

    def list_mine_collects(self, user_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaPost).join(
            IdeaCollect, IdeaCollect.post_id == IdeaPost.id
        ).filter(IdeaCollect.user_id == user_id, IdeaPost.status == "published")
        total = query.count()
        rows = query.order_by(IdeaCollect.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        ids = [p.id for p in rows]
        return Result.success("获取成功", {
            "total": total,
            "list": [self._post_item(p, self._tags_of(ids), self._attachments_of(ids), {p.id} | self._liked_set(user_id, ids), img_map=self._images_of(ids), collected={p.id}) for p in rows],
        })

    def list_mine_likes(self, user_id: int, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaPost).join(
            IdeaLike, IdeaLike.post_id == IdeaPost.id
        ).filter(IdeaLike.user_id == user_id, IdeaPost.status == "published")
        total = query.count()
        rows = query.order_by(IdeaLike.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        ids = [p.id for p in rows]
        return Result.success("获取成功", {
            "total": total,
            "list": [self._post_item(p, self._tags_of(ids), self._attachments_of(ids), {p.id} | self._liked_set(user_id, ids), img_map=self._images_of(ids), collected=self._collected_set(user_id, ids)) for p in rows],
        })

    # ---------- 评论 ----------

    def add_comment(self, user_id: int, post_id: int, req: CommentCreate) -> dict:
        content = req.content.strip()
        if not content:
            return Result.error("评论不能为空")
        if len(content) > COMMENT_LEN_MAX:
            return Result.error(f"评论不能超过{COMMENT_LEN_MAX}字")
        remain = _limit_check("cmt", user_id, 15)
        if remain:
            return Result.error(f"评论太频繁了，请 {int(remain) + 1} 秒后再试")
        p = self.db.get(IdeaPost, post_id)
        if p is None or p.status != "published":
            return Result.error("帖子不存在或已下架")
        c = IdeaComment(post_id=post_id, user_id=user_id, content=content)
        self.db.add(c)
        p.comment_count += 1
        self._recompute_hot(p)
        self.db.commit()
        cache.hot_zincr(post_id, HOT_W["comment"])
        _limit_mark("cmt", user_id, 15)
        name, _ = self._user_name(user_id)
        return Result.success("评论成功", {
            "id": c.id, "authorName": name, "content": c.content,
            "createTime": self._dt(c.create_time), "mine": True,
        })

    def delete_comment(self, user_id: int, comment_id: int) -> dict:
        c = self.db.get(IdeaComment, comment_id)
        if c is None:
            return Result.error("评论不存在")
        if c.user_id != user_id:
            return Result.error("无权限删除该评论")
        p = self.db.get(IdeaPost, c.post_id)
        if p:
            p.comment_count = max(0, p.comment_count - 1)
            self._recompute_hot(p)
        self.db.delete(c)
        self.db.commit()
        cache.hot_zincr(c.post_id, -HOT_W["comment"])
        return Result.success("删除成功")

    def list_comments(self, post_id: int, user_id: int | None, page: int, page_size: int) -> dict:
        query = self.db.query(IdeaComment).filter(IdeaComment.post_id == post_id)
        total = query.count()
        rows = query.order_by(IdeaComment.create_time.asc()).offset((page - 1) * page_size).limit(page_size).all()
        out = []
        for c in rows:
            name, _ = self._user_name(c.user_id)
            out.append({
                "id": c.id, "authorName": name, "content": c.content,
                "createTime": self._dt(c.create_time), "mine": c.user_id == user_id,
            })
        return Result.success("获取成功", {"total": total, "list": out})

    # ---------- 标签聚合 ----------

    def list_tags(self, top: int) -> dict:
        rows = self.db.query(IdeaPostTag.tag, func.count(func.distinct(IdeaPostTag.post_id)).label("n")).join(
            IdeaPost, IdeaPost.id == IdeaPostTag.post_id
        ).filter(IdeaPost.status == "published").group_by(IdeaPostTag.tag).order_by(
            func.count(func.distinct(IdeaPostTag.post_id)).desc()
        ).limit(top).all()
        return Result.success("获取成功", [{"tag": r[0], "count": r[1]} for r in rows])
