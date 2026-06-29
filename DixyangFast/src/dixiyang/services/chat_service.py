import json
import os
from datetime import datetime

from openai import OpenAI


def _call_deepseek(messages: list[dict], stream: bool = False):
    from dixiyang.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )
    kwargs = dict(
        model="deepseek-chat",
        messages=messages,
        stream=stream,
        max_tokens=8192,
    )
    if stream:
        return client.chat.completions.create(**kwargs)
    return client.chat.completions.create(**kwargs).choices[0].message.content


def build_context_query(character_ids: list[int] | None, story_node_ids: list[int] | None) -> str:
    from dixiyang.utils.database import SessionLocal
    from dixiyang.models.character import NovelCharacter
    from dixiyang.models.story_node import StoryNode

    parts: list[str] = []
    if character_ids:
        with SessionLocal() as session:
            chars = session.query(NovelCharacter).filter(NovelCharacter.id.in_(character_ids)).all()
            for c in chars:
                parts.append(
                    f"[角色: {c.name}, 性别: {c.gender or '无'}, "
                    f"年龄: {c.age or '无'}, 性格: {c.personality or '无'}, "
                    f"外貌: {c.appearance or '无'}, 背景: {c.background or '无'}]"
                )
    if story_node_ids:
        with SessionLocal() as session:
            nodes = session.query(StoryNode).filter(StoryNode.id.in_(story_node_ids)).all()
            for n in nodes:
                parts.append(
                    f"[故事节点: {n.title or '无标题'}, 内容: {n.content or '无'}, "
                    f"时间: {n.event_date or '无'}, 类型: {n.event_type or '无'}]"
                )
    if parts:
        return "参考上下文：\n" + "\n".join(parts)
    return ""


def build_system_prompt(use_rag: bool) -> str:
    if use_rag:
        return (
            "你是一个专业的小说创作助手。你会得到一些参考上下文（角色信息、故事节点等），"
            "请基于这些上下文回答用户的问题，帮助用户进行小说创作。"
            "如果没有提供上下文或上下文不相关，则忽略它。"
        )
    return (
        "你是一个专业的小说创作助手。请帮助用户进行小说创作，"
        "提供创意建议、写作指导和内容优化。"
    )


def build_full_prompt(
    message: str,
    use_rag: bool,
    character_ids: list[int] | None,
    story_node_ids: list[int] | None,
    edit_context: str | None = None,
) -> list[dict]:
    context = build_context_query(character_ids, story_node_ids) if use_rag else ""
    system = build_system_prompt(use_rag)
    if edit_context:
        system += "\n\n" + edit_context
    messages = [{"role": "system", "content": system}]
    if context:
        messages.append({"role": "user", "content": context})
        messages.append({"role": "assistant", "content": "已收到参考上下文，请继续提问。"})
    messages.append({"role": "user", "content": message})
    return messages


def load_chain_messages(chain_dir: str) -> list[dict]:
    """读取链式文件，返回按顺序的消息列表"""
    if not os.path.isdir(chain_dir):
        return []
    chain_files = sorted(
        [f for f in os.listdir(chain_dir) if f.endswith(".json") and f != "edits.json"],
        key=lambda f: f.split("_")[0],
    )
    messages: list[dict] = []
    for fname in chain_files:
        fpath = os.path.join(chain_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            msg = {"role": item.get("role", "user"), "content": item.get("content", "")}
            if item.get("thinking"):
                msg["thinking"] = item["thinking"]
            messages.append(msg)
    return messages


def save_chain_file(chain_dir: str, messages: list[dict]):
    """追加消息到新的链文件"""
    os.makedirs(chain_dir, exist_ok=True)
    ts = int(datetime.now().timestamp() * 1000)
    rand = os.urandom(4).hex()
    fname = f"{ts}_{rand}.json"
    with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def truncate_chain(chain_dir: str, keep_count: int):
    """保留链中前 keep_count 条消息，删除后续文件"""
    if not os.path.isdir(chain_dir):
        return
    chain_files = sorted(
        [f for f in os.listdir(chain_dir) if f.endswith(".json") and f != "edits.json"],
        key=lambda f: f.split("_")[0],
    )
    all_msgs: list[dict] = []
    for fname in chain_files:
        fpath = os.path.join(chain_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        all_msgs.extend(items)
        os.remove(fpath)

    kept = all_msgs[:keep_count]
    if kept:
        ts = int(datetime.now().timestamp() * 1000)
        rand = os.urandom(4).hex()
        fname = f"{ts}_{rand}.json"
        with open(os.path.join(chain_dir, fname), "w", encoding="utf-8") as f:
            json.dump(kept, f, ensure_ascii=False, indent=2)


def load_edit_context(chain_dir: str) -> str:
    """读取 edits.json 构建修正 prompt"""
    edits_path = os.path.join(chain_dir, "edits.json")
    if not os.path.isfile(edits_path):
        return ""
    try:
        with open(edits_path, encoding="utf-8") as f:
            edits = json.load(f)
    except Exception:
        return ""
    if not edits:
        return ""
    lines = ["以下是用户对之前回答的修正记录，请学习这些修正，避免再犯同样错误："]
    for e in edits:
        orig = e.get("original", "")
        edited = e.get("edited", "")
        idx = e.get("message_index", "?")
        lines.append(f"- 修正 #{idx}: 原文「{orig}」→ 修正版「{edited}」")
    return "\n".join(lines)
