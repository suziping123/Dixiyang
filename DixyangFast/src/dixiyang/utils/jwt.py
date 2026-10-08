from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def create_access_token(user_id: int, session_id: str) -> str:
    """签发 JWT；session_id 为单点登录会话号，服务端比对 app_user.session_id 决定是否踢出"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> int | None:
    payload = verify_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    return int(sub) if sub else None
