import random
import string
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends
from sqlalchemy.orm import Session

from ..models.user import AppUser
from ..models.email_verification import EmailVerificationCode
from ..schemas.auth import AuthDTO, RegisterDTO, LoginByCodeDTO, SendCodeDTO
from ..services.email_service import send_verification_code
from ..utils.database import get_db
from ..utils.jwt import create_access_token
from ..utils.response import Result

CODE_EXPIRE_MINUTES = 5
RATE_LIMIT_SECONDS = 60
# 登录风控：窗口内成功登录达 RISK_LOGIN_LIMIT 次后，密码登录必须验证码
RISK_WINDOW_MINUTES = 10
RISK_LOGIN_LIMIT = 3


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_pw(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def _now_utc_naive() -> datetime:
    """UTC 字面值时间（与 Java 端共表可比）"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _new_session_id() -> str:
    return uuid.uuid4().hex


def _record_login(user: AppUser) -> None:
    """记录一次成功登录：窗口内计数，达阈值则置强制验证码标记"""
    now = _now_utc_naive()
    start = user.login_window_start
    if start is None or start <= now - timedelta(minutes=RISK_WINDOW_MINUTES):
        count = 1
    else:
        count = (user.login_count or 0) + 1
    user.login_count = count
    user.login_window_start = now
    if count >= RISK_LOGIN_LIMIT:
        user.require_code = True


class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def login(self, req: AuthDTO) -> dict:
        user = self.db.query(AppUser).filter(AppUser.username == req.username).first()
        if not user:
            return Result.error("用户名不存在")
        if not _verify_pw(req.password, user.password):
            return Result.error("用户名或密码错误")
        # 风控：短时间内频繁顶号登录，强制改用邮箱验证码登录
        if user.require_code:
            return Result.error("登录过于频繁，请使用邮箱验证码登录")
        # 单点登录：生成新会话号覆盖旧值，旧设备下次请求即被踢出
        session_id = _new_session_id()
        user.session_id = session_id
        _record_login(user)
        self.db.commit()
        token = create_access_token(user.id, session_id)
        data = {
            "token": token,
            "user": {
                "userId": user.id,
                "username": user.username,
                "nickname": user.nickname or user.username,
                "email": user.email or "",
                "role": getattr(user, "role", "user"),
            },
        }
        return Result.success("操作成功", data)

    def register(self, req: RegisterDTO) -> dict:
        # 如果带了验证码，走验证码注册逻辑
        if req.code and req.email:
            return self._register_by_code(req)

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

    def _register_by_code(self, req: RegisterDTO) -> dict:
        if not req.email:
            return Result.error("邮箱不能为空")
        if not req.username:
            return Result.error("用户名不能为空")
        if len(req.password) < 6:
            return Result.error("密码长度至少为6位")

        # 校验验证码
        record = (
            self.db.query(EmailVerificationCode)
            .filter(
                EmailVerificationCode.email == req.email,
                EmailVerificationCode.purpose == "REGISTER",
                EmailVerificationCode.used == False,
            )
            .order_by(EmailVerificationCode.created_at.desc())
            .first()
        )
        if not record:
            return Result.error("请先获取验证码")
        if record.expire_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return Result.error("验证码已过期，请重新获取")
        if record.code != req.code:
            return Result.error("验证码错误")

        # 标记已使用
        record.used = True
        self.db.commit()

        # 检查用户名
        exist = self.db.query(AppUser).filter(AppUser.username == req.username).first()
        if exist:
            return Result.error("该用户名已存在")

        # 创建用户
        hashed = _hash_pw(req.password)
        user = AppUser(
            username=req.username,
            password=hashed,
            nickname=req.nickname or req.username,
            email=req.email,
        )
        self.db.add(user)
        self.db.commit()
        return Result.success("注册成功", None)

    def send_code(self, req: SendCodeDTO) -> dict:
        if not req.email:
            return Result.error("邮箱不能为空")
        if req.purpose not in ("LOGIN", "REGISTER", "CHG_EMAIL"):
            return Result.error("用途参数无效")

        now = datetime.now(timezone.utc)

        # 60秒限流
        last_record = (
            self.db.query(EmailVerificationCode)
            .filter(
                EmailVerificationCode.email == req.email,
                EmailVerificationCode.purpose == req.purpose,
            )
            .order_by(EmailVerificationCode.created_at.desc())
            .first()
        )
        if last_record and last_record.created_at:
            created = last_record.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            seconds_since = (now - created).total_seconds()
            if seconds_since < RATE_LIMIT_SECONDS:
                return Result.error(f"请{int(RATE_LIMIT_SECONDS - seconds_since)}秒后重试")

        # 生成验证码
        code = _generate_code()
        expire_time = now + timedelta(minutes=CODE_EXPIRE_MINUTES)

        record = last_record
        if record:
            record.code = code
            record.expire_time = expire_time.replace(tzinfo=None)
            record.used = False
            record.created_at = now.replace(tzinfo=None)
        else:
            record = EmailVerificationCode(
                email=req.email,
                code=code,
                purpose=req.purpose,
                expire_time=expire_time.replace(tzinfo=None),
                used=False,
                created_at=now.replace(tzinfo=None),
            )
            self.db.add(record)
        self.db.commit()

        # 发送邮件：失败时删除记录（否则 60s 限流会把用户锁死）并真实返回错误
        if not send_verification_code(req.email, code):
            self.db.delete(record)
            self.db.commit()
            return Result.error("验证码邮件发送失败，请稍后重试")

        return Result.success("验证码已发送")

    def login_by_code(self, req: LoginByCodeDTO) -> dict:
        if not req.email:
            return Result.error("邮箱不能为空")
        if not req.code:
            return Result.error("验证码不能为空")

        # 查询有效验证码
        record = (
            self.db.query(EmailVerificationCode)
            .filter(
                EmailVerificationCode.email == req.email,
                EmailVerificationCode.purpose == "LOGIN",
                EmailVerificationCode.used == False,
            )
            .order_by(EmailVerificationCode.created_at.desc())
            .first()
        )
        if not record:
            return Result.error("请先获取验证码")
        if record.expire_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return Result.error("验证码已过期，请重新获取")
        if record.code != req.code:
            return Result.error("验证码错误")

        # 标记已使用
        record.used = True
        self.db.commit()

        # 查找用户
        user = self.db.query(AppUser).filter(AppUser.email == req.email).first()
        if not user:
            return Result.error("该邮箱未注册")

        # 验证码登录通过风控 → 顶号 + 解除强制验证码 + 重置窗口
        session_id = _new_session_id()
        user.session_id = session_id
        user.require_code = False
        user.login_count = 0
        user.login_window_start = _now_utc_naive()
        self.db.commit()
        token = create_access_token(user.id, session_id)
        data = {
            "token": token,
            "user": {
                "userId": user.id,
                "username": user.username,
                "nickname": user.nickname or user.username,
                "email": user.email or "",
                "role": getattr(user, "role", "user"),
            },
        }
        return Result.success("操作成功", data)


def verify_change_email_code(db: Session, email: str, code: str | None) -> str | None:
    """校验「更换邮箱」验证码（purpose=CHG_EMAIL）。

    返回 None 表示通过；否则返回用户可读的错误文案。
    复用 send_code 写入的 EmailVerificationCode（60s 限流 / 5 分钟过期 / 一次性）。
    """
    if not code:
        return "更换邮箱需要验证码"

    record = (
        db.query(EmailVerificationCode)
        .filter(
            EmailVerificationCode.email == email,
            EmailVerificationCode.purpose == "CHG_EMAIL",
            EmailVerificationCode.used == False,  # noqa: E712 — SQLAlchemy 列比较
        )
        .order_by(EmailVerificationCode.created_at.desc())
        .first()
    )
    if not record:
        return "请先获取验证码"
    if record.expire_time.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return "验证码已过期，请重新获取"
    if record.code != str(code).strip():
        return "验证码错误"

    # 校验通过：标记一次性使用
    record.used = True
    return None
