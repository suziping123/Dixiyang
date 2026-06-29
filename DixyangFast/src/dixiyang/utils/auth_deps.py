from fastapi import Header, HTTPException

from .jwt import verify_token


async def get_current_user_id(authorization: str = Header(...)) -> int:
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
        return int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="token无效")
