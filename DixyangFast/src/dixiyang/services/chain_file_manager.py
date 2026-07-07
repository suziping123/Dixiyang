"""
链文件管理器 — 负责链文件的底层读写操作
支持链表结构（title + messages + next）和平铺旧格式自动兼容
"""

import json
import logging
import os
from datetime import datetime

log = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _make_filename() -> str:
    ts = int(datetime.now().timestamp() * 1000)
    rand = os.urandom(4).hex()
    return f"{ts}_{rand}.json"


def _parse_chain_file(fpath: str) -> tuple[list[dict], str | None]:
    """解析单个链文件，返回 (messages, next_path)"""
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return [], None

    # 链表结构：{title, messages, next}
    if isinstance(data, dict) and "messages" in data:
        return data["messages"], data.get("next")

    # 旧平铺结构：直接是 list 或单个 dict
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        return [data], None
    return [], None


def read_chain(chain_dir: str) -> list[dict]:
    """
    读取整个链文件，返回按顺序的消息列表。
    支持 next 指针链表和旧平铺格式。
    """
    if not os.path.isdir(chain_dir):
        return []

    # 找 head 文件（最小时间戳的 .json）
    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]
    if not json_files:
        return []

    # 优先按 next 指针遍历
    head_file = min(json_files, key=lambda f: f.split("_")[0])
    head_path = os.path.join(chain_dir, head_file)

    messages: list[dict] = []
    visited: set[str] = set()
    current = head_path

    while current and current not in visited:
        visited.add(current)
        msgs, next_ref = _parse_chain_file(current)
        messages.extend(msgs)
        if next_ref:
            # next_ref 是纯文件名
            current = os.path.join(chain_dir, next_ref)
        else:
            current = None

    # 如果链表遍历结果为空（可能全是旧格式文件），降级为平铺排序
    if not messages and json_files:
        for fname in sorted(json_files, key=lambda f: f.split("_")[0]):
            fpath = os.path.join(chain_dir, fname)
            msgs, _ = _parse_chain_file(fpath)
            messages.extend(msgs)

    return messages


def write_chain_file(chain_dir: str, messages: list[dict], title: str = "") -> str:
    """
    将消息写入新的链文件（追加到链尾）。
    返回新建文件的文件名。
    """
    os.makedirs(chain_dir, exist_ok=True)
    fname = _make_filename()
    data = {"title": title, "messages": messages, "next": None}

    # 找到当前链尾，设置 next 指针
    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]
    if json_files:
        tail_file = max(json_files, key=lambda f: f.split("_")[0])
        tail_path = os.path.join(chain_dir, tail_file)
        # 读取链尾文件，设置其 next 指向新文件
        try:
            with open(tail_path, encoding="utf-8") as f:
                tail_data = json.load(f)
            if isinstance(tail_data, dict):
                tail_data["next"] = fname
                with open(tail_path, "w", encoding="utf-8") as f:
                    json.dump(tail_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return fname


def truncate_chain(chain_dir: str, keep_count: int) -> str | None:
    """保留链中前 keep_count 条消息，删除后续文件。返回新文件名（如有）"""
    if not os.path.isdir(chain_dir):
        return None

    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]
    all_msgs: list[dict] = []
    for fname in sorted(json_files, key=lambda f: f.split("_")[0]):
        fpath = os.path.join(chain_dir, fname)
        msgs, _ = _parse_chain_file(fpath)
        all_msgs.extend(msgs)

    kept = all_msgs[:keep_count]
    if not kept:
        return None

    # 原子写入：先写 tmp 文件，确保成功后删除旧文件再 rename
    fname = _make_filename()
    tmp_name = fname + ".tmp"
    tmp_path = os.path.join(chain_dir, tmp_name)
    data = {"title": "", "messages": kept, "next": None}
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 删除旧文件
    for fn in json_files:
        try:
            os.remove(os.path.join(chain_dir, fn))
        except Exception:
            pass

    os.rename(tmp_path, os.path.join(chain_dir, fname))
    return fname


def replace_message(chain_dir: str, index: int, role: str, content: str) -> tuple[str, str]:
    """
    替换链中指定索引的消息内容。
    返回 (original_content, edited_content)
    Spring 兼容：替换前将原内容存入消息的 originalContent 字段
    """
    messages = read_chain(chain_dir)
    if index < 0 or index >= len(messages):
        raise IndexError(f"消息索引 {index} 越界，共 {len(messages)} 条")

    original = messages[index].get("content", "")
    # Spring 兼容：保留原始内容到 originalContent 字段
    messages[index]["originalContent"] = original
    messages[index]["role"] = role
    messages[index]["content"] = content

    # 清除所有链文件，重写
    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]

    fname = _make_filename()
    tmp_name = fname + ".tmp"
    tmp_path = os.path.join(chain_dir, tmp_name)
    data = {"title": "", "messages": messages, "next": None}
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for fn in json_files:
        try:
            os.remove(os.path.join(chain_dir, fn))
        except Exception:
            pass

    final_path = os.path.join(chain_dir, fname)
    os.rename(tmp_path, final_path)
    return original, content


def read_edits(chain_dir: str) -> list[dict]:
    """
    读取 edits.json
    兼容两种格式：
    - Spring: {"edits": [...]}
    - 旧版: [...]
    """
    edits_path = os.path.join(chain_dir, "edits.json")
    if not os.path.isfile(edits_path):
        return []
    try:
        with open(edits_path, encoding="utf-8") as f:
            data = json.load(f)
        # Spring 格式：{"edits": [...]}
        if isinstance(data, dict) and "edits" in data:
            return data["edits"]
        # 旧格式：直接是数组
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def write_edit(chain_dir: str, record: dict):
    """
    追加一条编辑记录到 edits.json
    Spring 兼容格式：{"edits": [...]}
    """
    edits = read_edits(chain_dir)
    edits.append(record)
    edits_path = os.path.join(chain_dir, "edits.json")
    with open(edits_path, "w", encoding="utf-8") as f:
        json.dump({"edits": edits}, f, ensure_ascii=False, indent=2)


def read_summary(chain_dir: str) -> dict | None:
    """读取 summary.json"""
    path = os.path.join(chain_dir, "summary.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_summary(chain_dir: str, summary: str, last_message_index: int):
    """保存历史摘要"""
    data = {
        "summary": summary,
        "lastMessageIndex": last_message_index,
        "updatedAt": _now_iso(),
    }
    path = os.path.join(chain_dir, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
