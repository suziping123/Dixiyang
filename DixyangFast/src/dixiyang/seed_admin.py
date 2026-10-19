"""创建/提升 Dixiyang 管理员账号（幂等）。

用法：
    python -m dixiyang.seed_admin
    python -m dixiyang.seed_admin --username admin123 --password 123456
    python -m dixiyang.seed_admin --reset-password

默认读取环境变量 ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL。
"""
from __future__ import annotations

import argparse
import os

from sqlalchemy import inspect, text

from .models.user import AppUser
from .services.auth_service import _hash_pw
from .utils.database import Base, SessionLocal, engine


def _ensure_user_columns() -> None:
    """兼容旧库：补 role / admin_session_id 列（create_all 不会给旧表加列）。"""
    Base.metadata.create_all(bind=engine)
    cols = {c["name"] for c in inspect(engine).get_columns("app_user")}
    with engine.begin() as conn:
        if "role" not in cols:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
        if "admin_session_id" not in cols:
            conn.execute(text("ALTER TABLE app_user ADD COLUMN admin_session_id VARCHAR(64)"))


def main() -> int:
    parser = argparse.ArgumentParser(description="创建/提升 Dixiyang 管理员账号")
    parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME", "admin123"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "123456"))
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin123@example.com"))
    parser.add_argument("--nickname", default=os.getenv("ADMIN_NICKNAME", "管理员"))
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="账号已存在时也重置密码，并解除登录风控（require_code/login_count）",
    )
    args = parser.parse_args()

    _ensure_user_columns()

    with SessionLocal() as db:
        user = db.query(AppUser).filter(AppUser.username == args.username).first()
        if user is None:
            user = AppUser(
                username=args.username,
                password=_hash_pw(args.password),
                nickname=args.nickname,
                email=args.email,
                role="admin",
                login_count=0,
                require_code=False,
            )
            db.add(user)
            db.commit()
            print(f"[seed_admin] 已创建管理员：{args.username}（role=admin）")
            return 0

        changed = False
        if getattr(user, "role", "user") != "admin":
            user.role = "admin"
            changed = True
        if args.reset_password:
            user.password = _hash_pw(args.password)
            user.require_code = False
            user.login_count = 0
            changed = True
        if changed:
            db.commit()
            suffix = "，密码已重置" if args.reset_password else ""
            print(f"[seed_admin] 已更新管理员：{args.username}{suffix}")
        else:
            print(f"[seed_admin] 管理员已存在：{args.username}（未改动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
