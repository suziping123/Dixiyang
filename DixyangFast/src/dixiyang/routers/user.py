import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..models.user import AppUser
from ..services.auth_service import _hash_pw, _verify_pw, verify_change_email_code
from ..utils.auth_deps import get_current_user_id
from ..utils.database import get_db
from ..utils.response import Result

router = APIRouter(prefix="/user", tags=["用户管理模块"])


@router.get("/info")
async def get_user_info(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return Result.error("用户不存在")
    return Result.success("获取成功", {
        "userId": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
    })


@router.post("/update")
async def update_user(body: dict, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """更新昵称/邮箱。

    邮箱**发生变化**时必须携带 `code`（purpose=CHG_EMAIL 的邮箱验证码，由
    POST /auth/send-code 发放），并做唯一性校验；未变化则不要求验证码。
    全部校验通过才落库（要么全改、要么全不改）。
    """
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return Result.error("用户不存在")

    # ---- 1. 昵称校验 ----
    new_nickname = body.get("nickname")
    if new_nickname is not None:
        new_nickname = str(new_nickname).strip()
        if not new_nickname or len(new_nickname) > 20:
            return Result.error("昵称需为 1-20 个字符")

    # ---- 2. 邮箱校验（变了才要求验证码）----
    new_email = body.get("email")
    if new_email is not None:
        new_email = str(new_email).strip()
        if not new_email:
            return Result.error("邮箱不能为空")
        if new_email != (user.email or ""):
            err = verify_change_email_code(db, new_email, body.get("code"))
            if err:
                return Result.error(err)
            taken = (
                db.query(AppUser)
                .filter(AppUser.email == new_email, AppUser.id != user_id)
                .first()
            )
            if taken:
                return Result.error("该邮箱已被其他账号使用")

    # ---- 3. 校验全部通过，统一落库 ----
    if new_nickname is not None:
        user.nickname = new_nickname
    if new_email is not None:
        user.email = new_email
    db.commit()
    return Result.success("更新成功")


@router.post("/password")
async def change_password(body: dict, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """修改密码：校验旧密码后写入新密码（对齐前端 AccountSection POST /user/password）"""
    old_password = body.get("oldPassword")
    new_password = body.get("newPassword")
    if not old_password or not new_password:
        return Result.error("参数不完整")
    if len(new_password) < 6:
        return Result.error("新密码至少 6 位")
    if old_password == new_password:
        return Result.error("新密码不能与当前密码相同")

    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return Result.error("用户不存在")
    if not _verify_pw(old_password, user.password):
        return Result.error("当前密码不正确")

    user.password = _hash_pw(new_password)
    db.commit()
    return Result.success("密码已修改")


@router.get("/bg-config")
async def get_bg_config(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return Result.error("用户不存在")
    data = json.loads(user.bg_config) if user.bg_config else {}
    return Result.success("获取成功", data)


@router.post("/bg-config")
async def update_bg_config(body: dict, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(AppUser).filter(AppUser.id == user_id).first()
    if not user:
        return Result.error("用户不存在")
    user.bg_config = json.dumps(body, ensure_ascii=False)
    db.commit()
    return Result.success("更新成功")
