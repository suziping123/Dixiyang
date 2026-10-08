from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..models.chapter import Chapter
from ..schemas.chapter import ChapterCreate, ChapterUpdate
from ..services.chapter_service import ChapterService
from ..services.chapter_content_service import ChapterContentService
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/chapters", tags=["章节管理"])


class ContentSaveReq(BaseModel):
    """保存正文请求（本地优先：仅用户显式上传时调用）"""
    title: str = ""
    content: str = ""
    clientVersion: int = 1
    clientHash: str = ""
    force: bool = Field(default=False, description="强制覆盖（用户确认冲突后）")

    class Config:
        populate_by_name = True


class ConflictCheckReq(BaseModel):
    clientVersion: int
    clientHash: str = ""


class ChapterCreateReq(BaseModel):
    """创建章节请求（novel_id 从路径取，不出现在 body）"""
    title: str
    volume_id: int | None = None
    sort_order: int | None = None

    class Config:
        populate_by_name = True


@router.get("/novel/{novel_id}")
async def list_chapters(
    novel_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    return svc.list_chapters(novel_id, user_id)


@router.get("/{chapter_id}")
async def get_chapter(
    chapter_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    return svc.get_chapter(chapter_id, user_id)


@router.post("/novel/{novel_id}")
async def create_chapter(
    novel_id: int,
    req: ChapterCreateReq,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    create_req = ChapterCreate(
        novel_id=novel_id,
        volume_id=req.volume_id,
        title=req.title,
        sort_order=req.sort_order,
    )
    return svc.create_chapter(user_id, create_req)


@router.post("/{chapter_id}")
async def update_chapter(
    chapter_id: int,
    req: ChapterUpdate,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    return svc.update_chapter(user_id, chapter_id, req)


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    return svc.delete_chapter(user_id, chapter_id)


@router.post("/novel/{novel_id}/reorder")
async def reorder_chapters(
    novel_id: int,
    chapter_ids: list[int],
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    return svc.reorder_chapters(novel_id, chapter_ids, user_id)


# ==================== 正文（文件存储）====================


@router.get("/{chapter_id}/content")
async def get_content(
    chapter_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    """读取云端正文，正文不在 MySQL 中"""
    meta = svc.get_chapter(chapter_id, user_id)
    if meta.get("code") != 200:
        return meta
    data = meta["data"]
    content = ChapterContentService.read_content(data.get("content_path"))
    return Result.success("获取成功", {
        "chapterId": data["id"],
        "title": data["title"],
        "version": data["version"],
        "contentHash": data.get("content_hash"),
        "content": content.get("content", "") if content else "",
        "wordCount": data.get("word_count", 0),
        "updatedAt": content.get("updatedAt") if content else None,
    })


@router.post("/{chapter_id}/content/conflict-check")
async def conflict_check(
    chapter_id: int,
    req: ConflictCheckReq,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    """保存前冲突检测：本地版本 ≠ 云端版本时不允许静默覆盖"""
    meta = svc.get_chapter(chapter_id, user_id)
    if meta.get("code") != 200:
        return meta
    result = ChapterContentService.check_conflict(chapter_id, req.clientVersion, req.clientHash)
    return Result.success("检测完成", result)


@router.post("/{chapter_id}/content")
async def save_content(
    chapter_id: int,
    req: ContentSaveReq,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    """
    保存正文到云端（仅用户显式触发）。
    MySQL 只更新 content_path/hash/version/size 元数据，正文写 JSON 文件。
    """
    meta = svc.get_chapter(chapter_id, user_id)
    if meta.get("code") != 200:
        return meta
    data = meta["data"]

    ch = svc.db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not ch:
        return Result.error("章节不存在")

    # 冲突检测：版本变化且 hash 不同 → 拒绝（除非 force）
    conflict = ChapterContentService.check_conflict(
        chapter_id, req.clientVersion, req.clientHash
    )
    if conflict["hasConflict"] and not req.force:
        return Result.success("存在冲突", {
            "hasConflict": True,
            "serverVersion": conflict["serverVersion"],
            "serverHash": conflict["serverHash"],
        })

    new_version = (ch.version or 1) + 1
    result = ChapterContentService.write_content(
        book_id=ch.novel_id,
        chapter_id=ch.id,
        title=req.title or ch.title,
        content=req.content,
        version=new_version,
    )

    ch.content_path = result["contentPath"]
    ch.content_hash = result["contentHash"]
    ch.content_size = result["contentSize"]
    ch.version = new_version
    ch.local_version = new_version
    ch.word_count = result["wordCount"]
    svc.db.commit()

    return Result.success("保存成功", {
        "chapterId": chapter_id,
        "version": new_version,
        "contentHash": result["contentHash"],
        "contentPath": result["contentPath"],
        "wordCount": result["wordCount"],
        "hasConflict": False,
    })


@router.get("/{chapter_id}/versions")
async def list_versions(
    chapter_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    meta = svc.get_chapter(chapter_id, user_id)
    if meta.get("code") != 200:
        return meta
    data = meta["data"]
    return Result.success("获取成功", {
        "current": data["version"],
        "history": ChapterContentService.list_versions(data["novel_id"], chapter_id),
    })


@router.get("/{chapter_id}/versions/{version}")
async def read_version(
    chapter_id: int,
    version: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChapterService = Depends(),
):
    meta = svc.get_chapter(chapter_id, user_id)
    if meta.get("code") != 200:
        return meta
    data = meta["data"]
    if version == data["version"]:
        content = ChapterContentService.read_content(data.get("content_path"))
    else:
        content = ChapterContentService.read_version(data["novel_id"], chapter_id, version)
    if not content:
        return Result.not_found("版本不存在")
    return Result.success("获取成功", content)
