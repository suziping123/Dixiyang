import hashlib
import json
import os
import uuid

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..config import UPLOAD_DIR
from ..models.novel import Novels
from ..models.user_config import UserConfig
from ..utils.auth_deps import get_current_user_id
from ..utils.database import get_db
from ..utils.response import Result

router = APIRouter(prefix="/upload", tags=["文件上传模块"])

COVERS_DIR = os.path.join(UPLOAD_DIR, "covers")
BACKGROUNDS_DIR = os.path.join(UPLOAD_DIR, "backgrounds")
COVER_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
BG_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 10 * 1024 * 1024


def _type_to_ext(content_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }.get(content_type, ".bin")


def _do_upload(file: UploadFile, save_dir: str, url_prefix: str, allowed_types: set) -> JSONResponse:
    if not file.content_type or file.content_type not in allowed_types:
        return Result.error("不支持的文件格式")
    content = file.file.read()
    if len(content) > MAX_SIZE:
        return Result.error("文件大小不能超过10MB")

    os.makedirs(save_dir, exist_ok=True)
    md5_hash = hashlib.md5(content).hexdigest()
    md5_path = os.path.join(save_dir, md5_hash + ".md5")
    if os.path.exists(md5_path):
        with open(md5_path) as f:
            existing_url = f.read().strip()
        return Result.success("文件已存在，已复用", existing_url)

    ext = _type_to_ext(file.content_type)
    filename = uuid.uuid4().hex + ext
    with open(os.path.join(save_dir, filename), "wb") as f:
        f.write(content)
    url = f"/api/uploads/{url_prefix}/{filename}"
    with open(md5_path, "w") as f:
        f.write(url)
    return Result.success("上传成功", url)


def _do_delete_file(url: str, save_dir: str) -> JSONResponse:
    if not url or not url.startswith("/api/uploads/"):
        return Result.error("无法删除非本系统文件")
    filename = url.rsplit("/", 1)[-1]
    filepath = os.path.join(save_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    for fname in os.listdir(save_dir):
        if fname.endswith(".md5"):
            with open(os.path.join(save_dir, fname)) as f:
                if f.read().strip() == url:
                    os.remove(os.path.join(save_dir, fname))
                    break
    return Result.success("删除成功")


@router.post("/novel-cover")
async def upload_cover(file: UploadFile):
    return _do_upload(file, COVERS_DIR, "covers", COVER_TYPES)


def delete_file_by_url(url: str):
    if not url or not url.startswith("/api/uploads/"):
        return
    relative = url[len("/api/uploads/"):]
    save_dir = os.path.join(UPLOAD_DIR, "covers") if relative.startswith("covers/") else os.path.join(UPLOAD_DIR, "backgrounds")
    filename = relative.split("/", 1)[-1] if "/" in relative else relative
    filepath = os.path.join(save_dir, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


@router.delete("/novel-cover")
async def delete_cover(url: str = Query(...), novelId: int = Query(..., alias="novelId"), db: Session = Depends(get_db)):
    r = _do_delete_file(url, COVERS_DIR)
    if isinstance(r, dict) and r.get("code") != 200:
        return r
    novel = db.query(Novels).filter(Novels.id == novelId).first()
    if novel and url == novel.cover_url:
        novel.cover_url = None
        db.commit()
    return Result.success("删除成功")


@router.post("/background")
async def upload_background(file: UploadFile):
    return _do_upload(file, BACKGROUNDS_DIR, "backgrounds", BG_TYPES)


@router.delete("/background")
async def delete_background(url: str = Query(...), userId: int = Query(..., alias="userId"), db: Session = Depends(get_db)):
    r = _do_delete_file(url, BACKGROUNDS_DIR)
    if isinstance(r, dict) and r.get("code") != 200:
        return r
    config = db.query(UserConfig).filter(UserConfig.user_id == userId).first()
    if config and config.custom_bgs:
        arr = config.custom_bgs if isinstance(config.custom_bgs, list) else []
        arr = [item for item in arr if item.get("url") != url]
        config.custom_bgs = arr if arr else None
        db.commit()
    return Result.success("删除成功")
