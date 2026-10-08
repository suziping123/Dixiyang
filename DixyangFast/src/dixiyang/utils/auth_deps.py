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
