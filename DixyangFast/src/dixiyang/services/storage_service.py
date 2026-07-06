"""
统一存储服务
负责 JSON 数据的文件存储，DB 只存路径引用
"""
import json
import os
import logging
from ..config import CHAT_STORAGE_PATH

log = logging.getLogger(__name__)

# 文件存储根目录（与 chat/ 同级）
STORAGE_ROOT = CHAT_STORAGE_PATH

# 存储阈值：超过此大小存文件，否则存 DB（单位：字节）
FILE_THRESHOLD = 1024

# 目录常量（相对于 STORAGE_ROOT）
CHARACTER_DIR = "character"
NOVEL_DIR = "novel"
USER_DIR = "user"


def _ensure_dir(subdir: str):
    """确保子目录存在"""
    path = os.path.join(STORAGE_ROOT, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def _get_file_path(subdir: str, record_id: int) -> str:
    """获取文件完整路径"""
    return os.path.join(STORAGE_ROOT, subdir, f"{record_id}.json")


def save_json(subdir: str, record_id: int, data: dict | list | None) -> str | None:
    """
    保存 JSON 数据到文件系统（全部存文件）
    返回：DB 中应存储的值（文件路径引用或 None）
    """
    if data is None:
        return None

    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    # 存文件
    file_path = _get_file_path(subdir, record_id)
    _ensure_dir(subdir)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    log.info("JSON 存入文件: %s", file_path)
    return f"__file__:{subdir}/{record_id}.json"


def load_json(subdir: str, record_id: int, db_value) -> dict | list | None:
    """
    加载 JSON 数据
    自动判断 db_value 是文件路径还是 JSON 字符串
    返回：解析后的 dict/list 或 None
    """
    if db_value is None:
        return None

    if isinstance(db_value, dict):
        return db_value

    if isinstance(db_value, str):
        # 检查是否为文件路径引用
        if db_value.startswith("__file__:"):
            rel_path = db_value.replace("__file__:", "")
            file_path = os.path.join(STORAGE_ROOT, rel_path)
            try:
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                log.warning("文件不存在: %s", file_path)
                return None
            except json.JSONDecodeError:
                log.warning("JSON 解析失败: %s", file_path)
                return None

        # 尝试作为 JSON 字符串解析
        try:
            return json.loads(db_value)
        except (json.JSONDecodeError, TypeError):
            # 解析失败，包装为 content 字段
            return {"content": db_value} if db_value else None

    return None


def delete_json(subdir: str, record_id: int, db_value) -> None:
    """
    删除 JSON 数据（如果存在文件则删除文件）
    """
    if isinstance(db_value, str) and db_value.startswith("__file__:"):
        rel_path = db_value.replace("__file__:", "")
        file_path = os.path.join(STORAGE_ROOT, rel_path)
        try:
            os.remove(file_path)
            log.info("已删除文件: %s", file_path)
        except FileNotFoundError:
            pass


def list_files(subdir: str) -> list[int]:
    """列出某子目录下所有记录 ID"""
    dir_path = os.path.join(STORAGE_ROOT, subdir)
    if not os.path.isdir(dir_path):
        return []
    return [
        int(f.replace(".json", ""))
        for f in os.listdir(dir_path)
        if f.endswith(".json")
    ]


def migrate_db_value_to_file(subdir: str, record_id: int, db_value) -> str | None:
    """
    迁移：将 DB 中的 JSON 值迁移到文件系统
    用于一次性迁移旧数据
    """
    if db_value is None:
        return None

    # 如果已经是路径引用，跳过
    if isinstance(db_value, str) and db_value.startswith("__file__:"):
        return db_value

    # 解析现有数据
    data = load_json(subdir, record_id, db_value)
    if data is None:
        return None

    # 保存到文件
    return save_json(subdir, record_id, data)
