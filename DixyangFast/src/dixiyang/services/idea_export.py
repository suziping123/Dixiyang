"""点子库数据源导出/导入：对话链快照、角色卡导出与一键导入"""
import json
import logging
import os

from sqlalchemy.orm import Session

from ..config import CHAT_STORAGE_PATH
from ..models.character import NovelCharacter
from ..models.novel import Novels
from .chain_file_manager import read_chain
from .storage_service import CHARACTER_DIR, STORAGE_ROOT, load_json, save_json

log = logging.getLogger(__name__)

# 对话快照最大条数（200 轮 = 400 条），超出截断
CHAT_SNAPSHOT_MAX = 400


def _community_dir(user_id: int, post_id: int) -> str:
    return os.path.join(STORAGE_ROOT, "community", str(user_id), str(post_id))


def write_community_json(rel_path: str, data) -> str:
    """写 community 下任意 JSON 文件，返回 __file__ 引用"""
    file_path = os.path.join(STORAGE_ROOT, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return f"__file__:{rel_path}"


def read_community_json(db_value: str | None):
    """按 __file__ 引用读 community JSON"""
    if not db_value or not db_value.startswith("__file__:"):
        return None
    file_path = os.path.join(STORAGE_ROOT, db_value.replace("__file__:", ""))
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log.warning("附件文件不存在: %s", file_path)
        return None


def delete_community_json(db_value: str | None) -> None:
    """按 __file__ 引用删文件（容忍不存在）"""
    if not db_value or not db_value.startswith("__file__:"):
        return
    file_path = os.path.join(STORAGE_ROOT, db_value.replace("__file__:", ""))
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def export_chat_snapshot(user_id: int, session_id: str) -> tuple[dict | None, str | None]:
    """
    导出对话链为只读快照（目录即用户维度，天然归属校验）。
    返回 (snapshot_data, error)。
    """
    # 链目录约定与 chat_history_service._session_dir 一致：storage/chat/{userId}/{sessionId}
    chain_dir = os.path.join(CHAT_STORAGE_PATH, "chat", str(user_id), session_id)
    if not os.path.isdir(chain_dir):
        return None, "会话不存在或已删除"
    messages = read_chain(chain_dir)
    if not messages:
        return None, "会话内容为空"
    truncated = len(messages) > CHAT_SNAPSHOT_MAX
    clipped = [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in messages[:CHAT_SNAPSHOT_MAX]
    ]
    return {
        "sourceSessionId": session_id,
        "messages": clipped,
        "truncated": truncated,
        "totalMessages": len(messages),
    }, None


def export_character_cards(db: Session, user_id: int, character_ids: list[int]) -> tuple[dict | None, str | None]:
    """
    导出角色卡快照（校验角色所属小说归当前用户）。
    返回 ({"characters": [...]}, None) 或 (None, 错误)。
    """
    cards = []
    for cid in character_ids:
        c = db.get(NovelCharacter, cid)
        if c is None:
            return None, f"角色不存在: {cid}"
        novel = db.get(Novels, c.novel_id)
        if novel is None or novel.user_id != user_id:
            return None, "无权限访问该角色"
        cards.append({
            "characterId": c.id,
            "novelId": c.novel_id,
            "name": c.name,
            "gender": c.gender,
            "age": c.age,
            "appearance": c.appearance,
            "background": c.background,
            "personality": c.personality,
            "extra": load_json(CHARACTER_DIR, c.id, c.extra),
        })
    return {"characters": cards}, None


def import_character_cards(db: Session, user_id: int, target_novel_id: int, snapshot: dict) -> list[dict]:
    """
    一键导入：把快照里的角色复制到目标小说（新行 + extra 文件，vector_id 不涉及）。
    返回导入结果 [{characterId, name}]。
    """
    results = []
    for card in (snapshot or {}).get("characters", []):
        name = card.get("name") or "未命名角色"
        # uk_novel_name 唯一键：目标小说已有同名角色时自动加后缀
        if db.query(NovelCharacter).filter(
            NovelCharacter.novel_id == target_novel_id, NovelCharacter.name == name
        ).first():
            i = 2
            while db.query(NovelCharacter).filter(
                NovelCharacter.novel_id == target_novel_id, NovelCharacter.name == f"{name} ({i})"
            ).first():
                i += 1
            name = f"{name} ({i})"
        c = NovelCharacter(
            novel_id=target_novel_id,
            name=name,
            gender=card.get("gender"),
            age=card.get("age"),
            appearance=card.get("appearance"),
            background=card.get("background"),
            personality=card.get("personality"),
            extra=None,
        )
        db.add(c)
        db.flush()
        if card.get("extra") is not None:
            c.extra = save_json(CHARACTER_DIR, c.id, card["extra"])
        db.commit()
        results.append({"characterId": c.id, "name": c.name})
    return results
