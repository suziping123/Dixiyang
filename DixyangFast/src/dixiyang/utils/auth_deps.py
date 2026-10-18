from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..models.user import AppUser
from ..utils.database import get_db
from .jwt import verify_token


async def get_current_user_id(
    authorization: str = Header(...), db: Session = Depends(get_db)
) -> int:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    token = authorization[7:]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    # 后台 token（scope=admin）不得访问用户端接口：两套会话完全隔离
    if payload.get("scope") == "admin":
        raise HTTPException(status_code=403, detail="后台会话不能用于用户端接口")
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="token无效")
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="token无效")
    # 单点登录：token 带会话号(sid)时才比对；旧版 token 无 sid，兼容放行至自然过期
    sid = payload.get("sid")
    if sid:
        user = db.get(AppUser, user_id)
        if user is None or sid != user.session_id:
            raise HTTPException(status_code=401, detail="账号已在其他设备登录")
    return user_id


async def get_optional_user_id(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> int | None:
    """可选鉴权：公开接口用——带合法 token 返回 user_id，否则 None（不抛 401）"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    payload = verify_token(authorization[7:])
    if payload is None:
        return None
    # 后台 token 不属于用户端身份（隔离规则：只认用户端会话）
    if payload.get("scope") == "admin":
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        return None
    sid = payload.get("sid")
    if sid:
        user = db.get(AppUser, user_id)
        if user is None or sid != user.session_id:
            return None
    return user_id


async def require_admin(
    authorization: str = Header(...), db: Session = Depends(get_db)
) -> int:
    """管理后台鉴权（独立会话版）：
    ① 仅接受后台登录端点签发、scope=admin 的 token——用户端 token 一律拒绝（切断"共用"）；
    ② sid 必须匹配 app_user.admin_session_id（后台自己的单点登录，登录后台不顶用户端）；
    ③ role 实时校验（被取消管理员即刻失效）。
    不满足分别返回 401（未登录/会话失效）或 403（权限不足）。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    payload = verify_token(authorization[7:])
    if payload is None:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    if payload.get("scope") != "admin":
        raise HTTPException(status_code=403, detail="请从管理后台入口登录")
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="token无效")
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="token无效")
    user = db.get(AppUser, user_id)
    if user is None or getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    sid = payload.get("sid")
    if not sid or sid != user.admin_session_id:
        raise HTTPException(status_code=401, detail="后台会话已失效，请重新登录")
    return user_id
