import json
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, STORAGE_DIR
from ..schemas.chat import ChatRequest
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result
from ..services.chat_service import (
    _call_deepseek,
    build_full_prompt,
    load_chain_messages,
    load_edit_context,
    save_chain_file,
    truncate_chain,
)

router = APIRouter(prefix="/chat", tags=["聊天模块"])


def _chain_dir(user_id: int, session_id: str) -> str:
    return os.path.join(STORAGE_DIR, "chat", str(user_id), session_id)


@router.get("")
async def chat_get(message: str, use_rag: bool = True,
                   user_id: int = Depends(get_current_user_id)):
    if not DEEPSEEK_API_KEY:
        return Result.error("未配置 DeepSeek API Key")
    prompt = build_full_prompt(message, use_rag, None, None)
    try:
        reply = _call_deepseek(prompt, stream=False)
        return Result.success("成功", reply)
    except Exception as e:
        return Result.error(str(e))


@router.post("")
async def chat_post(req: ChatRequest,
                    user_id: int = Depends(get_current_user_id)):
    if not DEEPSEEK_API_KEY:
        return Result.error("未配置 DeepSeek API Key")
    prompt = build_full_prompt(
        message=req.message,
        use_rag=req.use_rag,
        character_ids=req.character_ids,
        story_node_ids=req.story_node_ids,
    )
    try:
        reply = _call_deepseek(prompt, stream=False)
        return Result.success("成功", reply)
    except Exception as e:
        return Result.error(str(e))


def _build_messages(req: ChatRequest, chain_dir: str) -> list[dict]:
    history = load_chain_messages(chain_dir)
    edit_ctx = load_edit_context(chain_dir)

    system_prompt = _build_system_prompt(req.use_rag, edit_ctx)
    msgs = [{"role": "system", "content": system_prompt}]

    if req.use_rag:
        context_str = _build_context_str(req.character_ids, req.story_node_ids)
        if context_str:
            msgs.append({"role": "user", "content": context_str})
            msgs.append({"role": "assistant", "content": "已收到参考上下文，请继续提问。"})

    msgs.extend(history)
    msgs.append({"role": "user", "content": req.message or "请继续"})
    return msgs


async def _stream_llm(messages: list[dict]):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    stream = await client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
        max_tokens=8192,
    )

    state = "INIT"
    buf = ""
    full_content = ""

    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if not delta:
            continue
        full_content += delta
        buf += delta

        # <thinking> 标签检测拆分
        if state == "INIT":
            idx = buf.find("<thinking>")
            if idx >= 0:
                before = buf[:idx]
                if before:
                    yield ("content", before)
                buf = buf[idx + len("<thinking>"):]
                state = "THINKING"
            elif len(buf) > 64:
                yield ("content", buf)
                buf = ""
                state = "CONTENT"

        if state == "THINKING":
            idx = buf.find("</thinking>")
            if idx >= 0:
                think = buf[:idx]
                if think:
                    yield ("thinking", think)
                buf = buf[idx + len("</thinking>"):]
                state = "CONTENT"
            elif len(buf) > len("</thinking>"):
                safe = buf[:-len("</thinking>")]
                if safe:
                    yield ("thinking", safe)
                buf = buf[-len("</thinking>"):]

        if state == "CONTENT" and buf:
            yield ("content", buf)
            buf = ""

    if buf:
        yield ("content" if state != "THINKING" else "thinking", buf)


@router.post("/stream")
async def chat_stream(req: ChatRequest,
                      user_id: int = Depends(get_current_user_id)):
    async def event_generator():
        if not DEEPSEEK_API_KEY:
            yield _sse("error", {"message": "未配置 DeepSeek API Key"})
            yield _sse_done()
            return

        session_id = req.session_id or uuid.uuid4().hex
        chain_dir = _chain_dir(user_id, session_id)
        os.makedirs(chain_dir, exist_ok=True)

        messages = _build_messages(req, chain_dir)

        full_content = ""
        try:
            async for type_, delta in _stream_llm(messages):
                if type_ == "content":
                    full_content += delta
                yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                user_msg = {"role": "user", "content": req.message, "createTime": now}
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                save_chain_file(chain_dir, [user_msg, asst_msg])
                _upsert_session(user_id, session_id, req.novel_id)
            yield _sse_done()
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if full_content:
                try:
                    now = datetime.now().isoformat()
                    user_msg = {"role": "user", "content": req.message, "createTime": now}
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    save_chain_file(chain_dir, [user_msg, asst_msg])
                    _upsert_session(user_id, session_id, req.novel_id)
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
            yield _sse_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/regenerate")
async def chat_regenerate(req: ChatRequest,
                          user_id: int = Depends(get_current_user_id)):
    async def event_generator():
        if not req.session_id or req.regenerate_index < 0:
            yield _sse("error", {"message": "参数不完整"})
            yield _sse_done()
            return
        if not DEEPSEEK_API_KEY:
            yield _sse("error", {"message": "未配置 DeepSeek API Key"})
            yield _sse_done()
            return

        chain_dir = _chain_dir(user_id, req.session_id)
        os.makedirs(chain_dir, exist_ok=True)

        truncate_chain(chain_dir, req.regenerate_index)

        messages = _build_messages(req, chain_dir)

        full_content = ""
        try:
            async for type_, delta in _stream_llm(messages):
                if type_ == "content":
                    full_content += delta
                yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                save_chain_file(chain_dir, [asst_msg])
                _upsert_session(user_id, req.session_id, req.novel_id)
            yield _sse_done()
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if full_content:
                try:
                    now = datetime.now().isoformat()
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    save_chain_file(chain_dir, [asst_msg])
                    _upsert_session(user_id, req.session_id, req.novel_id)
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
            yield _sse_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _sse(type_: str, data: dict) -> str:
    payload = {"type": type_, **data}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _sse_done() -> str:
    return _sse("done", {})


def _build_system_prompt(use_rag: bool, edit_context: str = "") -> str:
    if use_rag:
        prompt = (
            "你是一个专业的小说创作助手。你会得到一些参考上下文（角色信息、故事节点等），"
            "请基于这些上下文回答用户的问题，帮助用户进行小说创作。"
            "如果没有提供上下文或上下文不相关，则忽略它。"
        )
    else:
        prompt = (
            "你是一个专业的小说创作助手。请帮助用户进行小说创作，"
            "提供创意建议、写作指导和内容优化。"
        )
    if edit_context:
        prompt += "\n\n" + edit_context
    return prompt


def _build_context_str(character_ids: list[int] | None,
                       story_node_ids: list[int] | None) -> str:
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


def _upsert_session(user_id: int, session_id: str, novel_id: int | None = None):
    from dixiyang.models.chat_session import ChatSession
    from dixiyang.utils.database import SessionLocal
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            session = ChatSession(
                user_id=user_id,
                novel_id=novel_id,
                session_id=session_id,
                title="新对话",
            )
            db.add(session)
        else:
            session.update_time = datetime.now()
        db.commit()
    finally:
        db.close()
