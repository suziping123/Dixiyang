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
from ..services.knowledge_search_tool import KNOWLEDGE_SEARCH_TOOL, knowledge_search
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
                new_fname = truncate_chain(chain_dir, 6)
                if new_fname:
                    new_hp = f"__file__:chat/{user_id}/{session_id}/{new_fname}"
                    _upsert_session(user_id, session_id, None, new_hp)
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


MAX_TOOL_ROUNDS = 5


async def _stream_llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 8192,
                       tools: list[dict] | None = None):
    """流式调用 LLM，yield (type, delta)。支持工具调用。"""
    from openai import AsyncOpenAI
    from ..config import DEEPSEEK_MODEL
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    kwargs: dict = dict(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=True,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if tools:
        kwargs["tools"] = tools

    stream = await client.chat.completions.create(**kwargs)

    state = "INIT"
    buf = ""
    # 工具调用累积
    tool_calls_map: dict[int, dict] = {}  # index → {id, name, arguments}
    has_tool_calls = False

    async for chunk in stream:
        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            continue

        delta = choice.delta

        # 处理工具调用增量
        if delta.tool_calls:
            has_tool_calls = True
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls_map:
                    tool_calls_map[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                entry = tool_calls_map[idx]
                if tc.id:
                    entry["id"] = tc.id
                if tc.function:
                    if tc.function.name:
                        entry["name"] = tc.function.name
                    if tc.function.arguments:
                        entry["arguments"] += tc.function.arguments

        # 处理文本内容增量
        content = delta.content or ""
        if not content:
            continue
        buf += content

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

    # 输出工具调用结果
    if has_tool_calls and tool_calls_map:
        yield ("tool_calls", tool_calls_map)


async def _stream_with_tool_loop(messages: list[dict], temperature: float, max_tokens: int):
    """Agent 循环：LLM → 工具调用 → 执行工具 → 结果回传 → 再次 LLM → ..."""
    current_messages = list(messages)

    for round_num in range(MAX_TOOL_ROUNDS + 1):
        tool_calls_map = None
        full_content = ""

        async for type_, delta in _stream_llm(current_messages, temperature, max_tokens,
                                               tools=[KNOWLEDGE_SEARCH_TOOL]):
            if type_ == "tool_calls":
                tool_calls_map = delta
            elif type_ in ("content", "thinking"):
                full_content += delta
                yield (type_, delta)

        if tool_calls_map is None:
            return  # 无工具调用，正常结束

        # 有工具调用 → 追加 AI 消息 + 执行工具
        ai_tool_calls = []
        for idx in sorted(tool_calls_map.keys()):
            tc = tool_calls_map[idx]
            ai_tool_calls.append({
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["name"], "arguments": tc["arguments"]},
            })

        ai_msg: dict = {"role": "assistant", "content": full_content or None, "tool_calls": ai_tool_calls}
        current_messages.append(ai_msg)

        # 执行每个工具调用
        for tc in ai_tool_calls:
            func_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                args = {}

            yield ("tool_start", func_name)

            if func_name == "knowledge_search":
                result = knowledge_search(
                    query=args.get("query", ""),
                    top_k=args.get("top_k", 5),
                    doc_type=args.get("doc_type"),
                )
            else:
                result = f"未知工具: {func_name}"

            yield ("tool_result", {"name": func_name, "result": result[:200] + "..." if len(result) > 200 else result})

            current_messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })


def _upsert_session(user_id: int, session_id: str, novel_id: int | None = None, head_path: str | None = None):
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
                head_path=head_path,
                title="新对话",
            )
            db.add(session)
        else:
            session.update_time = datetime.now()
            if head_path:
                session.head_path = head_path
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
        saved = False
        try:
            async for type_, delta in _stream_with_tool_loop(messages, temperature, max_tokens):
                if type_ in ("content", "thinking"):
                    full_content += delta
                if type_ == "tool_start":
                    yield _sse("tool_start", {"tool": delta})
                elif type_ == "tool_result":
                    yield _sse("tool_result", delta)
                elif type_ in ("content", "thinking"):
                    yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                user_msg = {"role": "user", "content": req.message, "createTime": now}
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                fname = save_chain_file(chain_dir, [user_msg, asst_msg])
                hp = f"__file__:chat/{user_id}/{session_id}/{fname}"
                _upsert_session(user_id, session_id, req.novel_id, hp)
                saved = True
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if full_content and not saved:
                try:
                    now = datetime.now().isoformat()
                    user_msg = {"role": "user", "content": req.message, "createTime": now}
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    fname = save_chain_file(chain_dir, [user_msg, asst_msg])
                    hp = f"__file__:chat/{user_id}/{session_id}/{fname}"
                    _upsert_session(user_id, session_id, req.novel_id, hp)
                    saved = True
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
        if saved:
            _maybe_summarize(user_id, session_id)
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

        new_fname = truncate_chain(chain_dir, req.regenerate_index)
        if new_fname:
            new_hp = f"__file__:chat/{user_id}/{req.session_id}/{new_fname}"
            _upsert_session(user_id, req.session_id, req.novel_id, new_hp)

        mode = get_mode(req.conversation_mode)
        messages = _build_stream_messages(req, chain_dir)
        max_tokens = req.max_tokens or MODE_META[mode]["max_tokens"]
        temperature = req.temperature or 0.7

        full_content = ""
        saved = False
        try:
            async for type_, delta in _stream_with_tool_loop(messages, temperature, max_tokens):
                if type_ in ("content", "thinking"):
                    full_content += delta
                if type_ == "tool_start":
                    yield _sse("tool_start", {"tool": delta})
                elif type_ == "tool_result":
                    yield _sse("tool_result", delta)
                elif type_ in ("content", "thinking"):
                    yield _sse(type_, {"delta": delta})
            if full_content:
                now = datetime.now().isoformat()
                asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                fname = save_chain_file(chain_dir, [asst_msg])
                hp = f"__file__:chat/{user_id}/{req.session_id}/{fname}"
                _upsert_session(user_id, req.session_id, req.novel_id, hp)
                saved = True
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if full_content and not saved:
                try:
                    now = datetime.now().isoformat()
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    fname = save_chain_file(chain_dir, [asst_msg])
                    hp = f"__file__:chat/{user_id}/{req.session_id}/{fname}"
                    _upsert_session(user_id, req.session_id, req.novel_id, hp)
                    saved = True
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
        if saved:
            _maybe_summarize(user_id, req.session_id)
        yield _sse_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
