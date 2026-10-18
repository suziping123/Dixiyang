"""管理后台 API：登录（独立会话）/ 仪表盘统计 / 用户管理 / 内容管理（广场·灵感墙）。管理端点全部走 require_admin 鉴权"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.chat_session import ChatSession
from ..models.novel import Novels
from ..models.user import AppUser
from ..schemas.auth import AuthDTO
from ..services.admin_content_service import AdminContentService
from ..services.auth_service import AuthService
from ..utils.auth_deps import require_admin
from ..utils.database import get_db
from ..utils.response import Result
from ..models import idea as idea_model

# 后台登录端点：不能带 require_admin（否则死锁），单独挂载 → POST /api/admin/auth/login
auth_router = APIRouter(prefix="/admin/auth", tags=["admin"])

# 管理端点：全部走 require_admin——仅后台会话 token 可过，用户端 token 一律拒绝
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@auth_router.post("/login")
async def admin_login(req: AuthDTO, svc: AuthService = Depends()):
    """管理后台登录：仅 role=admin 放行；独立会话号，不影响用户端登录态"""
    return svc.admin_login(req)


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


# ---------- 内容管理：广场帖子 ----------

class PostStatusPayload(BaseModel):
    status: str  # published | removed


@router.get("/posts")
async def list_posts(page: int = 1, pageSize: int = 20, status: str | None = None,
                     category: str | None = None, keyword: str | None = None,
                     svc: AdminContentService = Depends()):
    """帖子列表（全状态；支持 状态/分区/关键词 筛选）"""
    return svc.list_posts(page, pageSize, status, category, keyword)


@router.get("/posts/{post_id}")
async def get_post(post_id: int, svc: AdminContentService = Depends()):
    """帖子详情（含正文/配图/标签/附件元信息）"""
    return svc.get_post(post_id)


@router.put("/posts/{post_id}/status")
async def set_post_status(post_id: int, payload: PostStatusPayload,
                          svc: AdminContentService = Depends()):
    """平台下架/恢复：下架置 admin_removed=1（作者不可自行恢复），恢复清 0"""
    return svc.set_post_status(post_id, payload.status)


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, svc: AdminContentService = Depends()):
    """硬删除：级联清理评论/点赞/收藏/标签行 + 正文/附件/配图文件"""
    return svc.delete_post(post_id)


@router.get("/posts/{post_id}/comments")
async def list_post_comments(post_id: int, page: int = 1, pageSize: int = 20,
                             svc: AdminContentService = Depends()):
    return svc.list_comments(post_id, page, pageSize)


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, svc: AdminContentService = Depends()):
    """删除违规评论（回写帖子评论计数与热度）"""
    return svc.delete_comment(comment_id)


# ---------- 内容管理：灵感墙便签 ----------

@router.get("/sticky")
async def list_sticky(page: int = 1, pageSize: int = 20, keyword: str | None = None,
                      done: bool | None = None, svc: AdminContentService = Depends()):
    """便签列表（keyword 匹配用户名/昵称；done 过滤完成态）"""
    return svc.list_sticky(page, pageSize, keyword, done)


@router.delete("/sticky/{note_id}")
async def delete_sticky(note_id: int, svc: AdminContentService = Depends()):
    """删除便签（连带正文文件清理）"""
    return svc.delete_sticky(note_id)
