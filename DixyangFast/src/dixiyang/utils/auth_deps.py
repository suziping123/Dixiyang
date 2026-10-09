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
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> int:
    """管理后台鉴权：token 合法且 role=admin，否则 403"""
    user = db.get(AppUser, user_id)
    if user is None or getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user_id
