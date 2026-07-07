import json
import logging
import os
import re
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..config import CHAT_STORAGE_PATH, DEEPSEEK_API_KEY
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
from ..services.knowledge_search_tool import knowledge_search, knowledge_search_structured
from ..services.novel_tools import get_all_tools
from ..services.prompt_templates import build_system_prompt, build_user_prompt
from ..utils.auth_deps import get_current_user_id
from ..utils.response import Result

router = APIRouter(prefix="/chat", tags=["聊天模块"])

logger = logging.getLogger(__name__)

_rag_enabled: bool | None = None


def is_rag_enabled() -> bool:
    global _rag_enabled
    if _rag_enabled is not None:
        return _rag_enabled
    try:
        from langchain_chroma import Chroma
        from ..services.embeddings import DixiyangEmbeddings
        Chroma(
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "dixiyang_knowledge"),
            embedding_function=DixiyangEmbeddings(),
            persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./storage/vectordb_4060"),
        )
        _rag_enabled = True
    except Exception as e:
        logger.warning("RAG 不可用（Chroma 连接失败）: %s", e)
        _rag_enabled = False
    return _rag_enabled


def _chain_dir(user_id: int, session_id: str) -> str:
    return os.path.join(CHAT_STORAGE_PATH, "chat", str(user_id), session_id)


def _sse(type_: str, data: dict) -> str:
    payload = {"type": type_, **data}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _sse_done(session_id: str | None = None) -> str:
    payload: dict = {"type": "done"}
    if session_id:
        payload["sessionId"] = session_id
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


_SESSION_ID_RE = re.compile(r"^[a-f0-9\-]{8,64}$")


def _is_valid_session_id(sid: str) -> bool:
    return bool(_SESSION_ID_RE.match(sid))


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
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    llm = get_chat_model()
    chain = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
    ]) | llm | StrOutputParser()
    resp = await chain.ainvoke({"input": message})
    return Result.success("成功", resp)


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
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    llm = get_chat_model(
        temperature=req.temperature or 0.7,
        max_tokens=req.max_tokens or MODE_META[mode]["max_tokens"],
    )
    chain = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
    ]) | llm | StrOutputParser()
    resp = await chain.ainvoke({"input": user_prompt})
    return Result.success("成功", resp)


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
    """流式调用 LLM（LangChain），yield (type, delta)。支持工具调用。"""
    llm = get_chat_model(temperature, max_tokens)
    if tools:
        llm = llm.bind_tools(tools)

    state = "INIT"
    buf = ""
    tool_calls_map: dict[int, dict] = {}
    has_tool_calls = False

    async for chunk in llm.astream(messages):
        raw_calls = chunk.tool_call_chunks or chunk.additional_kwargs.get("tool_calls")
        if raw_calls:
            has_tool_calls = True
            for tc in raw_calls:
                if not isinstance(tc, dict):
                    idx = tc.index or 0
                    tid = tc.id or ""
                    fname = tc.name or ""
                    fargs = tc.args or ""
                elif "function" in tc:
                    idx = tc.get("index", 0) or 0
                    tid = tc.get("id", "")
                    function = tc.get("function", {}) or {}
                    fname = function.get("name", "")
                    fargs = function.get("arguments", "")
                else:
                    idx = tc.get("index", 0) or 0
                    tid = tc.get("id", "")
                    fname = tc.get("name", "")
                    fargs = tc.get("args", "")
                if idx not in tool_calls_map:
                    tool_calls_map[idx] = {"id": tid, "name": fname, "arguments": fargs}
                else:
                    entry = tool_calls_map[idx]
                    if tid:
                        entry["id"] = tid
                    if fname:
                        entry["name"] = fname
                    if fargs:
                        entry["arguments"] += fargs

        content = chunk.content or ""
        if not content:
            continue
        buf += content

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

    if has_tool_calls and tool_calls_map:
        yield ("tool_calls", tool_calls_map)


async def _stream_with_tool_loop(messages: list[dict], temperature: float, max_tokens: int, novel_id: int = 0):
    """Agent 循环：LLM → 工具调用 → LangChain tool.invoke() → 结果回传 → 再次 LLM → ..."""
    current_messages = list(messages)

    tools = get_all_tools(novel_id)
    if is_rag_enabled():
        tools.append(knowledge_search)
    tool_map = {t.name: t for t in tools}

    for round_num in range(MAX_TOOL_ROUNDS + 1):
        tool_calls_map = None
        full_content = ""

        async for type_, delta in _stream_llm(current_messages, temperature, max_tokens, tools=tools):
            if type_ == "tool_calls":
                tool_calls_map = delta
            elif type_ in ("content", "thinking"):
                full_content += delta
                yield (type_, delta)

        if tool_calls_map is None:
            return

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

        for tc in ai_tool_calls:
            func_name = tc["function"]["name"]
            raw = tc["function"]["arguments"] or "{}"
            try:
                args = json.loads(raw)
            except (json.JSONDecodeError, KeyError, TypeError):
                args = {}

            yield ("tool_start", func_name)

            result = ""
            tool_fn = tool_map.get(func_name)
            if tool_fn:
                try:
                    result = tool_fn.invoke(args)
                except Exception as e:
                    result = f"工具执行失败: {type(e).__name__}: {e}"
            else:
                result = f"未知工具: {func_name}"

            yield ("tool_result", {"name": func_name, "result": result[:200] + "..." if len(result) > 200 else result})

            # 如果是 knowledge_search，额外推送结构化引用数据
            if func_name == "knowledge_search":
                try:
                    refs = knowledge_search_structured(
                        query=args.get("query", ""),
                        top_k=args.get("top_k", 5),
                        doc_type=args.get("doc_type"),
                    )
                    if refs:
                        yield ("rag_references", {"name": func_name, "references": refs})
                except Exception as e:
                    logger.warning("knowledge_search_structured 失败: %s", e)

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
        if not _is_valid_session_id(session_id):
            session_id = uuid.uuid4().hex
        chain_dir = _chain_dir(user_id, session_id)
        os.makedirs(chain_dir, exist_ok=True)

        messages = _build_stream_messages(req, chain_dir)
        max_tokens = req.max_tokens or MODE_META[mode]["max_tokens"]
        temperature = req.temperature or 0.7

        full_content = ""
        references: list[dict] = []
        saved = False
        try:
            async for type_, delta in _stream_with_tool_loop(messages, temperature, max_tokens, novel_id=req.novel_id or 0):
                if type_ in ("content", "thinking"):
                    full_content += delta
                if type_ == "tool_start":
                    yield _sse("tool_start", {"tool": delta})
                elif type_ == "tool_result":
                    yield _sse("tool_result", delta)
                elif type_ == "rag_references":
                    refs = delta.get("references", [])
                    references.extend(refs)
                    yield _sse("rag_references", delta)
                elif type_ in ("content", "thinking"):
                    yield _sse(type_, {"delta": delta})
            now = datetime.now().isoformat()
            user_msg = {"role": "user", "content": req.message, "createTime": now}
            asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
            if references:
                asst_msg["references"] = references
            fname = save_chain_file(chain_dir, [user_msg, asst_msg])
            hp = f"__file__:chat/{user_id}/{session_id}/{fname}"
            _upsert_session(user_id, session_id, req.novel_id, hp)
            saved = True
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if not saved:
                try:
                    now = datetime.now().isoformat()
                    user_msg = {"role": "user", "content": req.message, "createTime": now}
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    if references:
                        asst_msg["references"] = references
                    fname = save_chain_file(chain_dir, [user_msg, asst_msg])
                    hp = f"__file__:chat/{user_id}/{session_id}/{fname}"
                    _upsert_session(user_id, session_id, req.novel_id, hp)
                    saved = True
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
        if saved:
            _maybe_summarize(user_id, session_id)
        yield _sse_done(session_id)

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
        references: list[dict] = []
        saved = False
        try:
            async for type_, delta in _stream_with_tool_loop(messages, temperature, max_tokens, novel_id=req.novel_id or 0):
                if type_ in ("content", "thinking"):
                    full_content += delta
                if type_ == "tool_start":
                    yield _sse("tool_start", {"tool": delta})
                elif type_ == "tool_result":
                    yield _sse("tool_result", delta)
                elif type_ == "rag_references":
                    refs = delta.get("references", []) if isinstance(delta, dict) else []
                    references.extend(refs)
                    yield _sse("rag_references", delta)
                elif type_ in ("content", "thinking"):
                    yield _sse(type_, {"delta": delta})
            now = datetime.now().isoformat()
            asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
            if references:
                asst_msg["references"] = references
            fname = save_chain_file(chain_dir, [asst_msg])
            hp = f"__file__:chat/{user_id}/{req.session_id}/{fname}"
            _upsert_session(user_id, req.session_id, req.novel_id, hp)
            saved = True
        except Exception as e:
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})
            if not saved:
                try:
                    now = datetime.now().isoformat()
                    asst_msg = {"role": "assistant", "content": full_content, "createTime": now}
                    if references:
                        asst_msg["references"] = references
                    fname = save_chain_file(chain_dir, [asst_msg])
                    hp = f"__file__:chat/{user_id}/{req.session_id}/{fname}"
                    _upsert_session(user_id, req.session_id, req.novel_id, hp)
                    saved = True
                except Exception as e2:
                    yield _sse("error", {"message": f"save after error failed: {e2}"})
        if saved:
            _maybe_summarize(user_id, req.session_id)
        yield _sse_done(req.session_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
