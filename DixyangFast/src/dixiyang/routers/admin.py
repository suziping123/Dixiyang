"""管理后台 API：仪表盘统计 / 用户管理（M1）。全部走 require_admin 鉴权"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.chat_session import ChatSession
from ..models.novel import Novels
from ..models.user import AppUser
from ..utils.auth_deps import require_admin
from ..utils.database import get_db
from ..utils.response import Result
from ..models import idea as idea_model

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """仪表盘：用户/小说/帖子/会话总数 + 帖子分区分布 + 近7天发帖趋势"""
    total_users = db.query(func.count(AppUser.id)).scalar() or 0
    total_novels = db.query(func.count(Novels.id)).scalar() or 0
    total_posts = db.query(func.count(idea_model.IdeaPost.id)).filter(
        idea_model.IdeaPost.status == "published"
    ).scalar() or 0
    total_sessions = db.query(func.count(ChatSession.id)).scalar() or 0
    cat_rows = (
        db.query(idea_model.IdeaPost.category, func.count(idea_model.IdeaPost.id))
        .filter(idea_model.IdeaPost.status == "published")
        .group_by(idea_model.IdeaPost.category).all()
    )
    # 近7天发帖趋势（按天）
    from datetime import datetime, timedelta
    since = datetime.now() - timedelta(days=6)
    day_rows = (
        db.query(func.date(idea_model.IdeaPost.create_time), func.count(idea_model.IdeaPost.id))
        .filter(idea_model.IdeaPost.create_time >= since)
        .group_by(func.date(idea_model.IdeaPost.create_time)).all()
    )
    return Result.success("获取成功", {
        "totals": {"users": total_users, "novels": total_novels, "posts": total_posts, "sessions": total_sessions},
        "postCategories": [{"category": c, "count": n} for c, n in cat_rows],
        "postTrend": [{"date": str(d), "count": n} for d, n in day_rows],
    })


@router.get("/users")
def list_users(page: int = 1, pageSize: int = 20, keyword: str | None = None,
               db: Session = Depends(get_db)):
    """用户列表（分页 + 用户名/昵称搜索）"""
    q = db.query(AppUser)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((AppUser.username.like(like)) | (AppUser.nickname.like(like)))
    total = q.count()
    rows = q.order_by(AppUser.id.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    return Result.success("获取成功", {
        "total": total,
        "list": [{
            "id": u.id, "username": u.username, "nickname": u.nickname or "",
            "email": u.email or "", "role": getattr(u, "role", "user"),
            "createTime": str(u.create_time) if u.create_time else "",
        } for u in rows],
    })


@router.put("/users/{user_id}/role")
def update_role(user_id: int, payload: dict, db: Session = Depends(get_db)):
    """改角色：body {"role": "user"|"admin"}"""
    role = payload.get("role")
    if role not in ("user", "admin"):
        return Result.error("role 只能是 user 或 admin")
    u = db.get(AppUser, user_id)
    if u is None:
        return Result.error("用户不存在")
    u.role = role
    db.commit()
    return Result.success("操作成功", {"id": u.id, "role": u.role})
