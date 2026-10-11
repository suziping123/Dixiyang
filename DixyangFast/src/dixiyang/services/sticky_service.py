"""便利贴灵感服务：CRUD + 正文文件存储（AGENTS §7，DB 只存路径引用）"""
import logging
import random

from ..schemas.sticky import ALLOWED_COLORS, NoteCreate, NoteUpdate
from ..utils.response import Result
from .storage_service import delete_json, load_json, save_json

log = logging.getLogger(__name__)

SUBDIR_TMPL = "sticky/{user_id}"  # 文件: storage/sticky/{userId}/{noteId}.json
MAX_CONTENT = 5000  # 正文上限（便签是短灵感，不是长文）


def _subdir(user_id: int) -> str:
    return SUBDIR_TMPL.format(user_id=user_id)


def _load_body(row) -> dict:
    data = load_json(_subdir(row.user_id), row.id, row.content_path)
    if not isinstance(data, dict):
        return {"content": "", "images": []}
    return {"content": data.get("content", ""), "images": data.get("images", []) or []}


def _serialize(row) -> dict:
    body = _load_body(row)
    return {
        "id": row.id,
        "color": row.color,
        "x": row.x,
        "y": row.y,
        "pinnedRoute": row.pinned_route,
        "inPool": bool(row.in_pool),
        "rotation": row.rotation,
        "zIndex": row.z_index,
        "done": bool(row.done),
        "content": body["content"],
        "images": body["images"],
        "createTime": row.create_time.strftime("%Y-%m-%d %H:%M:%S") if row.create_time else None,
        "updateTime": row.update_time.strftime("%Y-%m-%d %H:%M:%S") if row.update_time else None,
    }


def _get_owned(db, user_id: int, note_id: int):
    from ..models.sticky import StickyNote
    return db.query(StickyNote).filter(StickyNote.id == note_id, StickyNote.user_id == user_id).first()


def list_notes(db, user_id: int, in_pool: bool | None = None) -> dict:
    from ..models.sticky import StickyNote
    q = db.query(StickyNote).filter(StickyNote.user_id == user_id)
    if in_pool is True:
        q = q.filter(StickyNote.in_pool == 1)
    elif in_pool is False:
        q = q.filter(StickyNote.in_pool == 0)
    rows = q.order_by(StickyNote.id.desc()).all()
    return Result.success("获取成功", [_serialize(r) for r in rows])


def create_note(db, user_id: int, req: NoteCreate) -> dict:
    from ..models.sticky import StickyNote
    content = (req.content or "")[:MAX_CONTENT]
    color = req.color if req.color in ALLOWED_COLORS else "yellow"
    row = StickyNote(
        user_id=user_id,
        color=color,
        x=req.x,
        y=req.y,
        rotation=round(random.uniform(-3, 3), 1),  # 拟物：新便签随机微旋转
        z_index=0,
        content_path="",  # 占位，save_json 后回填
    )
    db.add(row)
    db.commit()
    row.content_path = save_json(_subdir(user_id), row.id, {"content": content, "images": req.images}) or ""
    db.commit()
    return Result.success("创建成功", _serialize(row))


def update_note(db, user_id: int, note_id: int, req: NoteUpdate) -> dict:
    row = _get_owned(db, user_id, note_id)
    if row is None:
        return Result.not_found("便签不存在")

    # 元数据字段
    if req.color is not None and req.color in ALLOWED_COLORS:
        row.color = req.color
    if req.x is not None:
        row.x = req.x
    if req.y is not None:
        row.y = req.y
    if req.z_index is not None:
        row.z_index = req.z_index
    if req.in_pool is not None:
        row.in_pool = 1 if req.in_pool else 0
    # 钉住/解锁：pinned=True 需带 routePath；pinned=False 解锁回浮动
    if req.pinned is True:
        if not req.route_path:
            return Result.bad_request("钉住需指定当前路由")
        row.pinned_route = req.route_path[:200]
    elif req.pinned is False:
        row.pinned_route = None

    # 完成态
    if req.done is not None:
        row.done = 1 if req.done else 0

    # 正文/图片（有提供才重写文件）
    if req.content is not None or req.images is not None:
        body = _load_body(row)
        content = (req.content if req.content is not None else body["content"])[:MAX_CONTENT]
        images = req.images if req.images is not None else body["images"]
        row.content_path = save_json(_subdir(user_id), row.id, {"content": content, "images": images}) or row.content_path

    db.commit()
    return Result.success("保存成功", _serialize(row))


def delete_note(db, user_id: int, note_id: int) -> dict:
    row = _get_owned(db, user_id, note_id)
    if row is None:
        return Result.not_found("便签不存在")
    delete_json(_subdir(user_id), row.id, row.content_path)  # 先删文件后删行（项目惯例）
    db.delete(row)
    db.commit()
    return Result.success("删除成功")
