from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class AppUser(Base):
    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(100))
    bg_config: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # 单点登录：当前登录会话号（登录时覆盖，旧设备请求即被踢出）
    session_id: Mapped[str | None] = mapped_column(String(64))
    # 登录风控：窗口内成功登录次数 / 窗口起点（UTC）/ 是否强制验证码登录
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    login_window_start: Mapped[datetime | None] = mapped_column(DateTime)
    require_code: Mapped[bool] = mapped_column(Boolean, default=False)
    # 角色：user / admin（管理后台鉴权）
    role: Mapped[str] = mapped_column(String(20), default="user", server_default="user")
