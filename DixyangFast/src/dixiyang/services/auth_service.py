import bcrypt
from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.user import AppUser
from ..schemas.auth import AuthDTO, RegisterDTO
from ..utils.database import get_db
from ..utils.jwt import create_access_token
from ..utils.response import Result


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def login(self, req: AuthDTO) -> dict:
        user = self.db.query(AppUser).filter(AppUser.username == req.username).first()
        if not user:
            return Result.error("用户名不存在")
        if not _verify_pw(req.password, user.password):
            return Result.error("用户名或密码错误")
        token = create_access_token(user.id)
        data = {
            "token": token,
            "user": {
                "userId": user.id,
                "username": user.username,
                "nickname": user.nickname or user.username,
                "email": user.email or "",
            },
        }
        return Result.success("操作成功", data)

    def register(self, req: RegisterDTO) -> dict:
        exist = self.db.query(AppUser).filter(AppUser.username == req.username).first()
        if exist:
            return Result.error("用户名已存在")
        hashed = _hash_pw(req.password)
        user = AppUser(
            username=req.username,
            password=hashed,
            nickname=req.nickname or req.username,
            email=req.email,
        )
        self.db.add(user)
        self.db.commit()
        return Result.success("注册成功！！！", None)
