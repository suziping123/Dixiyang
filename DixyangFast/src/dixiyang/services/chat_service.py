import json
import logging
import os
from datetime import datetime

from langchain_openai import ChatOpenAI

from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from .conversation_mode import ConversationMode, MODE_META, get_mode
from .prompt_templates import (
    build_keypoint_prompt,
    build_system_prompt,
    build_title_prompt,
    build_user_prompt,
)
from .storage_service import load_json, CHARACTER_DIR

log = logging.getLogger(__name__)

# ==================== LangChain ChatModel 单例 ====================

_llm_cache: dict[str, ChatOpenAI] = {}


def get_chat_model(
    temperature: float = 0.7,
    max_tokens: int = 8192,
) -> ChatOpenAI:
    key = f"{temperature}:{max_tokens}"
    if key not in _llm_cache:
        _llm_cache[key] = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return _llm_cache[key]


def call_llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 8192) -> str:
    """同步调用 LLM，返回文本"""
    llm = get_chat_model(temperature, max_tokens)
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    lc_msgs = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            lc_msgs.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_msgs.append(AIMessage(content=content))
        else:
            lc_msgs.append(HumanMessage(content=content))
    resp = llm.invoke(lc_msgs)
    return resp.content


# ==================== 上下文构建 ====================

def build_fixed_context(
    character_ids: list[int] | None,
    story_node_ids: list[int] | None,
    include_characters: bool = True,
    include_story: bool = True,
) -> str:
    """构建固定设定上下文（角色卡 + 故事节点全字段）"""
    from ..utils.database import SessionLocal
    from ..models.character import NovelCharacter
    from ..models.story_node import StoryNode

    parts: list[str] = []

    if include_characters and character_ids:
        with SessionLocal() as db:
            chars = db.query(NovelCharacter).filter(NovelCharacter.id.in_(character_ids)).all()
            for c in chars:
                lines = [f"[角色: {c.name}"]
                if c.gender:
                    lines.append(f"性别: {c.gender}")
                if c.appearance:
                    lines.append(f"外貌: {c.appearance}")
                if c.personality:
                    lines.append(f"性格: {c.personality}")
                if c.background:
                    lines.append(f"背景: {c.background}")
                if c.extra:
                    extra_data = load_json(CHARACTER_DIR, c.id, c.extra)
                    if extra_data:
                        lines.append(f"附加: {json.dumps(extra_data, ensure_ascii=False)}")
                lines.append("]")
                parts.append(", ".join(lines))

    if include_story and story_node_ids:
        with SessionLocal() as db:
            nodes = db.query(StoryNode).filter(StoryNode.id.in_(story_node_ids)).all()
            for n in nodes:
                lines = [f"[故事节点: {n.title or '无标题'}"]
                if n.event_date:
                    lines.append(f"时间: {n.event_date}")
                if n.event_type:
                    lines.append(f"类型: {n.event_type}")
                if n.importance:
                    lines.append(f"重要性: {n.importance}")
                if n.character_names:
                    lines.append(f"涉及角色: {n.character_names}")
                if n.tags:
                    lines.append(f"标签: {n.tags}")
                if n.content:
                    lines.append(f"内容: {n.content[:300]}")
                lines.append("]")
                parts.append(", ".join(lines))

    return "\n".join(parts) if parts else ""


# ==================== 链文件操作（委托给 chain_file_manager）====================

from .chain_file_manager import (
    read_chain as load_chain_messages,
    write_chain_file as _write_chain,
    truncate_chain,
    read_edits,
    read_summary,
    write_summary,
)


def save_chain_file(chain_dir: str, messages: list[dict], title: str = "") -> str:
    """保存消息到新的链文件，返回文件名"""
    return _write_chain(chain_dir, messages, title)


# ==================== 编辑修正 ====================

def load_edit_context(chain_dir: str) -> str:
    """读取 edits.json 构建修正 prompt"""
    from .chain_file_manager import read_edits
    edits = read_edits(chain_dir)
    if not edits:
        return ""
    lines = ["以下是用户对之前回答的修正记录，请学习这些修正，避免再犯同样错误："]
    for e in edits:
        key_point = e.get("keyPoint", "")
        error_type = e.get("errorType", "")
        orig = e.get("originalContent", "")
        edited = e.get("editedContent", "")
        idx = e.get("messageIndex", "?")
        if key_point:
            lines.append(f"- 修正 #{idx} [{error_type}]: {key_point}")
        else:
            lines.append(f"- 修正 #{idx}: 原文「{orig[:80]}」→ 修正版「{edited[:80]}」")
    return "\n".join(lines)


def extract_keypoint_async(original: str, edited: str):
    """异步提取编辑修正要点（fire-and-forget）"""
    import asyncio
    import threading

    def _run():
        try:
            prompt = build_keypoint_prompt(original, edited)
            result = call_llm(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=128,
            )
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            return json.loads(result)
        except Exception as e:
            log.warning("keypoint 提取失败: %s", e)
            return {"keyPoint": "", "errorType": "OTHER"}

    # 在线程池中运行，不阻塞主流程
    import concurrent.futures
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    return pool.submit(_run)


# ==================== 消息历史格式化 ====================

def format_history_for_prompt(messages: list[dict], max_pairs: int = 20) -> str:
    """将消息列表格式化为历史文本"""
    recent = messages[-max_pairs * 2:] if len(messages) > max_pairs * 2 else messages
    lines: list[str] = []
    for m in recent:
        role = m.get("role", "user")
        content = m.get("content", "")
        if not content:
            continue
        label = "用户" if role == "user" else "AI"
        lines.append(f"{label}：{content[:500]}")
    return "\n".join(lines)
