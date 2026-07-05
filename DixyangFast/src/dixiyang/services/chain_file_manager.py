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
            # next_ref 是相对路径如 "./xxx.json"
            next_name = next_ref.lstrip("./")
            current = os.path.join(chain_dir, next_name)
        else:
            current = None

    # 如果链表遍历结果为空（可能全是旧格式文件），降级为平铺排序
    if not messages and json_files:
        for fname in sorted(json_files, key=lambda f: f.split("_")[0]):
            fpath = os.path.join(chain_dir, fname)
            msgs, _ = _parse_chain_file(fpath)
            messages.extend(msgs)

    return messages


def write_chain_file(chain_dir: str, messages: list[dict], title: str = ""):
    """将消息写入新的链文件（追加到链尾）"""
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
                tail_data["next"] = f"./{fname}"
                with open(tail_path, "w", encoding="utf-8") as f:
                    json.dump(tail_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def truncate_chain(chain_dir: str, keep_count: int):
    """保留链中前 keep_count 条消息，删除后续文件"""
    if not os.path.isdir(chain_dir):
        return

    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]
    all_msgs: list[dict] = []
    for fname in sorted(json_files, key=lambda f: f.split("_")[0]):
        fpath = os.path.join(chain_dir, fname)
        msgs, _ = _parse_chain_file(fpath)
        all_msgs.extend(msgs)
        os.remove(fpath)

    kept = all_msgs[:keep_count]
    if kept:
        fname = _make_filename()
        data = {"title": "", "messages": kept, "next": None}
        with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def replace_message(chain_dir: str, index: int, role: str, content: str) -> tuple[str, str]:
    """
    替换链中指定索引的消息内容。
    返回 (original_content, edited_content)
    """
    messages = read_chain(chain_dir)
    if index < 0 or index >= len(messages):
        raise IndexError(f"消息索引 {index} 越界，共 {len(messages)} 条")

    original = messages[index].get("content", "")
    messages[index]["role"] = role
    messages[index]["content"] = content

    # 清除所有链文件，重写
    json_files = [
        f for f in os.listdir(chain_dir)
        if f.endswith(".json") and f not in ("edits.json", "summary.json")
    ]
    for fname in json_files:
        os.remove(os.path.join(chain_dir, fname))

    write_chain_file(chain_dir, messages)
    return original, content


def read_edits(chain_dir: str) -> list[dict]:
    """读取 edits.json"""
    edits_path = os.path.join(chain_dir, "edits.json")
    if not os.path.isfile(edits_path):
        return []
    try:
        with open(edits_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def write_edit(chain_dir: str, record: dict):
    """追加一条编辑记录到 edits.json"""
    edits = read_edits(chain_dir)
    edits.append(record)
    edits_path = os.path.join(chain_dir, "edits.json")
    with open(edits_path, "w", encoding="utf-8") as f:
        json.dump(edits, f, ensure_ascii=False, indent=2)


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
