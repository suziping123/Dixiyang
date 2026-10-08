"""
章节正文存储服务
正文以 JSON 文件存文件系统，MySQL 只存路径/hash/version 元数据
路径约定: books/{bookId}/chapters/{chapterId}/content.json
"""
import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timezone

from ..config import CHAT_STORAGE_PATH

log = logging.getLogger(__name__)

BOOKS_DIR = "books"


def _books_root() -> str:
    return os.path.join(CHAT_STORAGE_PATH, BOOKS_DIR)


def _chapter_dir(book_id: int, chapter_id: int) -> str:
    return os.path.join(_books_root(), str(book_id), "chapters", str(chapter_id))


def content_rel_path(book_id: int, chapter_id: int) -> str:
    """DB 中存的相对路径引用（__file__ 协议）"""
    return f"__file__:{BOOKS_DIR}/{book_id}/chapters/{chapter_id}/content.json"


def resolve_path(content_path: str) -> str:
    """把 DB 中的 __file__: 引缀转为绝对路径"""
    rel = content_path.replace("__file__:", "", 1)
    return os.path.join(CHAT_STORAGE_PATH, rel)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ChapterContentService:
    """正文文件读写 + 版本管理 + 冲突检测"""

    @staticmethod
    def read_content(content_path: str) -> dict | None:
        """读取正文文件，返回 {version, chapterId, title, content, updatedAt, wordCount}"""
        if not content_path:
            return None
        path = resolve_path(content_path)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.warning("正文文件读取失败: %s, %s", path, e)
            return None

    @staticmethod
    def write_content(
        book_id: int,
        chapter_id: int,
        title: str,
        content: str,
        version: int,
    ) -> dict:
        """
        写正文文件（含历史版本归档）。
        返回 {contentPath, contentHash, contentSize, version, wordCount}
        """
        chapter_dir = _chapter_dir(book_id, chapter_id)
        os.makedirs(chapter_dir, exist_ok=True)

        # 归档当前版本到 versions/
        current_file = os.path.join(chapter_dir, "content.json")
        if os.path.isfile(current_file) and version > 1:
            versions_dir = os.path.join(chapter_dir, "versions")
            os.makedirs(versions_dir, exist_ok=True)
            archive = os.path.join(versions_dir, f"{version - 1}.json")
            try:
                shutil.copy2(current_file, archive)
            except OSError as e:
                log.warning("版本归档失败: %s", e)

        payload = {
            "version": version,
            "chapterId": chapter_id,
            "title": title,
            "content": content,
            "updatedAt": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "wordCount": len(content),
        }
        # 原子写入：先写 tmp 再 rename
        tmp = current_file + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, current_file)

        return {
            "contentPath": content_rel_path(book_id, chapter_id),
            "contentHash": _sha256(content),
            "contentSize": len(content.encode("utf-8")),
            "version": version,
            "wordCount": len(content),
        }

    @staticmethod
    def list_versions(book_id: int, chapter_id: int) -> list[int]:
        """列出历史版本号（不含当前版本）"""
        versions_dir = os.path.join(_chapter_dir(book_id, chapter_id), "versions")
        if not os.path.isdir(versions_dir):
            return []
        out = []
        for f in os.listdir(versions_dir):
            if f.endswith(".json"):
                try:
                    out.append(int(f[:-5]))
                except ValueError:
                    pass
        return sorted(out, reverse=True)

    @staticmethod
    def read_version(book_id: int, chapter_id: int, version: int) -> dict | None:
        """读取指定历史版本"""
        path = os.path.join(_chapter_dir(book_id, chapter_id), "versions", f"{version}.json")
        if not os.path.isfile(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def delete_content(content_path: str):
        """删除正文文件及其版本目录"""
        if not content_path:
            return
        path = resolve_path(content_path)
        chapter_dir = os.path.dirname(path)
        try:
            shutil.rmtree(chapter_dir, ignore_errors=True)
        except OSError as e:
            log.warning("正文目录删除失败: %s, %s", chapter_dir, e)

    @staticmethod
    def check_conflict(
        chapter_id: int,
        client_version: int,
        client_hash: str,
    ) -> dict:
        """
        冲突检测：客户端带上次同步的 version + hash。
        返回 {hasConflict, serverVersion, serverHash}
        """
        from ..utils.database import SessionLocal
        from ..models.chapter import Chapter

        with SessionLocal() as db:
            c = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not c:
                return {"hasConflict": True, "serverVersion": 0, "serverHash": ""}
            server_version = c.version or 1
            server_hash = c.content_hash or ""
            has_conflict = (
                client_version != server_version
                and (client_hash != server_hash)
            )
            return {
                "hasConflict": has_conflict,
                "serverVersion": server_version,
                "serverHash": server_hash,
            }
