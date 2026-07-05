import json
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..config import CHAT_STORAGE_PATH, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from ..services.conversation_mode import get_mode, MODE_META
from ..schemas.chat import ChatRequest
from ..services.chat_service import (
    build_fixed_context,
    format_history_for_prompt,
    get_chat_model,
    load_chain_messages,
    load_edit_context,
    save_chain_file,
    truncate_chain,
)
from ..services.prompt_templates import build_system_prompt, build_user_prompt
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/chat", tags=["聊天模块"])


def _chain_dir(user_id: int, session_id: str) -> str:
    return os.path.join(CHAT_STORAGE_PATH, "chat", str(user_id), session_id)


def _sse(type_: str, data: dict) -> str:
    payload = {"type": type_, **data}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _sse_done() -> str:
    return _sse("done", {})


def _maybe_summarize(user_id: int, session_id: str):
    """异步检查是否需要历史摘要（fire-and-forget）"""
    import threading

    def _run():
        try:
            from ..services.chain_file_manager import read_chain, read_summary, write_summary, truncate_chain
            from ..services.prompt_templates import build_summarize_prompt
            from ..services.chat_service import call_llm

            chain_dir = _chain_dir(user_id, session_id)
            messages = read_chain(chain_dir)
            if len(messages) < 12:
                return

            summary_data = read_summary(chain_dir)
            last_idx = summary_data.get("lastMessageIndex", 0) if summary_data else 0
            if len(messages) - last_idx < 6:
                return

            to_summarize = messages[:6]
            conv = []
            for m in to_summarize:
                role = m.get("role", "user")
                content = m.get("content", "")
                label = "用户" if role == "user" else "AI"
                conv.append(f"{label}：{content[:300]}")

            prev = summary_data["summary"] if summary_data else ""
            prompt = build_summarize_prompt(prev, "\n".join(conv))
            new_summary = call_llm(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=256,
            ).strip()

            if new_summary:
                write_summary(chain_dir, new_summary, len(messages))
                truncate_chain(chain_dir, 6)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


# ==================== 简单聊天（非流式）====================

@router.get("")
async def chat_get(message: str, use_rag: bool = True,
                   user_id: int = Depends(get_current_user_id)):
    if not DEEPSEEK_API_KEY:
        return Result.error("未配置 DeepSeek API Key")
    system = build_system_prompt(get_mode("WRITE"))
    from langchain_core.messages import SystemMessage, HumanMessage
    llm = get_chat_model()
    resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=message)])
    return Result.success("成功", resp.content)


@router.post("")
async def chat_post(req: ChatRequest,
                    user_id: int = Depends(get_current_user_id)):
    if not DEEPSEEK_API_KEY:
        return Result.error("未配置 DeepSeek API Key")
    mode = get_mode(req.conversation_mode)
    fixed_ctx = build_fixed_context(
        req.character_ids, req.story_node_ids,
        req.include_characters, req.include_story,
    ) if req.use_rag else ""
    system = build_system_prompt(mode, req.custom_system_prompt)
    user_prompt = build_user_prompt(fixed_ctx, "", "", req.message)
    from langchain_core.messages import SystemMessage, HumanMessage
    llm = get_chat_model(
        temperature=req.temperature or 0.7,
        max_tokens=req.max_tokens or MODE_META[mode]["max_tokens"],
    )
    resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_prompt)])
    return Result.success("成功", resp.content)


# ==================== 流式聊天 ====================

def _build_stream_messages(req: ChatRequest, chain_dir: str) -> list[dict]:
    """构建流式聊天的完整消息列表"""
    mode = get_mode(req.conversation_mode)

    # 历史消息
    history_msgs = load_chain_messages(chain_dir)
    history_text = format_history_for_prompt(history_msgs)

    # 编辑修正上下文
    edit_ctx = load_edit_context(chain_dir)

    # 固定设定
    fixed_ctx = ""
    if req.use_rag:
        fixed_ctx = build_fixed_context(
            req.character_ids, req.story_node_ids,
            req.include_characters, req.include_story,
        )

    # System prompt
    system = build_system_prompt(mode, req.custom_system_prompt)

    # User prompt
    user_prompt = build_user_prompt(fixed_ctx, history_text, edit_ctx, req.message or "请继续")

    return [{"role": "system", "content": system}, {"role": "user", "content": user_prompt}]


async def _stream_llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 8192):
    """流式调用 LLM，yield (type, delta)"""
    from openai import AsyncOpenAI
    from ..config import DEEPSEEK_MODEL
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    stream = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=True,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    state = "INIT"
    buf = ""

    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if not delta:
            continue
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


def _upsert_session(user_id: int, session_id: str, novel_id: int | None = None):
    from ..models.chat_session import ChatSession
    from ..utils.database import SessionLocal
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


@router.post("/stream")
async def chat_stream(req: ChatRequest,
                      user_id: int = Depends(get_current_user_id)):
    async def event_generator():
        if not DEEPSEEK_API_KEY:
            yield _sse("error", {"message": "未配置 DeepSeek API Key"})
            yield _sse_done()
            return

        mode = get_mode(req.conversation_mode)
        session_id = req.session_id or uuid.uuid4().hex
        chain_dir = _chain_dir(user_id, session_id)
        os.makedirs(chain_dir, exist_ok=True)

        messages = _build_stream_messages(req, chain_dir)
        max_tokens = req.max_tokens or MODE_META[mode]["max_tokens"]
        temperature = req.temperature or 0.7

        full_content = ""
        try:
            async for type_, delta in _stream_llm(messages, temperature, max_tokens):
                if type_ == "content":
                    full_content += delta
                yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                user_msg = {"role": "user", "content": req.message, "createTime": now}
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                save_chain_file(chain_dir, [user_msg, asst_msg])
                _upsert_session(user_id, session_id, req.novel_id)
                # 异步检查是否需要历史摘要
                _maybe_summarize(user_id, session_id)
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
                    _maybe_summarize(user_id, session_id)
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
            yield _sse_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ==================== 重新生成 ====================

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

        mode = get_mode(req.conversation_mode)
        messages = _build_stream_messages(req, chain_dir)
        max_tokens = req.max_tokens or MODE_META[mode]["max_tokens"]
        temperature = req.temperature or 0.7

        full_content = ""
        try:
            async for type_, delta in _stream_llm(messages, temperature, max_tokens):
                if type_ == "content":
                    full_content += delta
                yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                save_chain_file(chain_dir, [asst_msg])
                _upsert_session(user_id, req.session_id, req.novel_id)
                _maybe_summarize(user_id, req.session_id)
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
