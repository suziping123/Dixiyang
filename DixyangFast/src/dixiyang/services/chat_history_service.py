import json
import logging
import os
import shutil
import uuid
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from ..config import CHAT_STORAGE_PATH, CHAT_MAX_FILE_SIZE
from ..models.chat_session import ChatSession
from ..utils.database import get_db
from ..utils.response import Result
from .chain_file_manager import (
    read_chain,
    replace_message,
    read_edits,
    write_edit,
    read_summary,
    write_summary,
    truncate_chain,
)
from .chat_service import save_chain_file

log = logging.getLogger(__name__)


class ChatHistoryService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _session_dir(self, user_id: int, session_id: str) -> str:
        return os.path.join(CHAT_STORAGE_PATH, "chat", str(user_id), session_id)

    def _ensure_dir(self, user_id: int, session_id: str):
        d = self._session_dir(user_id, session_id)
        os.makedirs(d, exist_ok=True)
        return d

    def _upsert_session(self, user_id: int, session_id: str, novel_id: int | None = None):
        session = self.db.query(ChatSession).filter(
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
            self.db.add(session)
        else:
            session.update_time = datetime.now()
        self.db.commit()
        return session

    def create_session(self, user_id: int, novel_id: int | None, title: str) -> dict:
        session_id = uuid.uuid4().hex
        session = ChatSession(
            user_id=user_id,
            novel_id=novel_id,
            session_id=session_id,
            title=title,
        )
        self.db.add(session)
        self.db.commit()
        self._ensure_dir(user_id, session_id)
        return Result.success("创建成功", session_id)

    def get_sessions(self, user_id: int, novel_id: int | None) -> dict:
        q = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)
        if novel_id:
            q = q.filter(ChatSession.novel_id == novel_id)
        sessions = q.order_by(ChatSession.update_time.desc()).all()
        return Result.success("获取成功", [
            {
                "sessionId": s.session_id,
                "novelId": s.novel_id,
                "title": s.title or "新对话",
                "createTime": s.create_time.isoformat() if s.create_time else None,
                "updateTime": s.update_time.isoformat() if s.update_time else None,
            }
            for s in sessions
        ])

    def get_session_messages(self, user_id: int, session_id: str) -> dict:
        chain_dir = self._session_dir(user_id, session_id)
        messages = read_chain(chain_dir)
        now = datetime.now().isoformat()
        for m in messages:
            m.setdefault("createTime", now)
        return Result.success("获取成功", messages)

    def batch_save(self, user_id: int, session_id: str, novel_id: int | None, messages: list) -> dict:
        chain_dir = self._ensure_dir(user_id, session_id)
        save_chain_file(chain_dir, messages)
        self._upsert_session(user_id, session_id, novel_id)
        return Result.success("保存成功")

    def edit_message(self, user_id: int, session_id: str, message_index: int, role: str, content: str) -> dict:
        chain_dir = self._session_dir(user_id, session_id)
        if not os.path.isdir(chain_dir):
            return Result.error("会话目录不存在")

        try:
            original, edited = replace_message(chain_dir, message_index, role, content)
        except IndexError:
            return Result.error("消息索引越界")
        except Exception as e:
            return Result.error(f"编辑失败: {e}")

        # 记录到 edits.json（结构化：含 keyPoint 和 errorType）
        edits = read_edits(chain_dir)
        record = {
            "message_index": message_index,
            "original": original,
            "edited": edited,
            "timestamp": datetime.now().isoformat(),
            "version": len(edits) + 1,
            "keyPoint": "",
            "errorType": "OTHER",
        }

        # 异步提取修正要点（fire-and-forget）
        try:
            from .chat_service import extract_keypoint_async
            future = extract_keypoint_async(original, edited)
            # 不阻塞，后台线程会更新
            import concurrent.futures
            def _update_keypoint(f):
                try:
                    result = f.result(timeout=30)
                    record["keyPoint"] = result.get("keyPoint", "")
                    record["errorType"] = result.get("errorType", "OTHER")
                    # 重新写入（覆盖刚才的空值）
                    all_edits = read_edits(chain_dir)
                    if all_edits and all_edits[-1].get("version") == record["version"]:
                        all_edits[-1]["keyPoint"] = record["keyPoint"]
                        all_edits[-1]["errorType"] = record["errorType"]
                        edits_path = os.path.join(chain_dir, "edits.json")
                        with open(edits_path, "w", encoding="utf-8") as f:
                            json.dump(all_edits, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    log.warning("keypoint 更新失败: %s", e)
            future.add_done_callback(_update_keypoint)
        except Exception as e:
            log.warning("keypoint 提取启动失败: %s", e)

        write_edit(chain_dir, record)
        return Result.success("编辑成功")

    def generate_title(self, user_id: int, session_id: str) -> dict:
        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            return Result.error("会话不存在")

        chain_dir = self._session_dir(user_id, session_id)
        messages = read_chain(chain_dir)
        if not messages:
            title = f"对话_{session_id[:8]}"
            session.title = title
            self.db.commit()
            return Result.success("标题生成成功", title)

        from .prompt_templates import build_title_prompt
        conv = []
        for msg in messages[:4]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role and content:
                label = "用户" if role == "user" else "AI"
                conv.append(f"{label}：{content[:200]}")

        prompt = build_title_prompt("\n".join(conv))
        try:
            from .chat_service import call_llm
            title = call_llm(
                [{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=32,
            ).strip()
            if not title:
                title = f"对话_{session_id[:8]}"
        except Exception:
            title = f"对话_{session_id[:8]}"

        session.title = title
        self.db.commit()
        return Result.success("标题生成成功", title)

    def maybe_summarize(self, user_id: int, session_id: str):
        """
        自动历史摘要：消息超过 12 条时，异步取前 6 条生成摘要并截断。
        """
        import threading

        def _run():
            try:
                chain_dir = self._session_dir(user_id, session_id)
                messages = read_chain(chain_dir)
                if len(messages) < 12:
                    return

                summary_data = read_summary(chain_dir)
                last_idx = summary_data.get("lastMessageIndex", 0) if summary_data else 0

                # 距上次摘要不足 6 条则跳过
                if len(messages) - last_idx < 6:
                    return

                # 取前 6 条生成摘要
                to_summarize = messages[:6]
                conv = []
                for m in to_summarize:
                    role = m.get("role", "user")
                    content = m.get("content", "")
                    label = "用户" if role == "user" else "AI"
                    conv.append(f"{label}：{content[:300]}")

                prev_summary = summary_data["summary"] if summary_data else ""
                from .prompt_templates import build_summarize_prompt
                prompt = build_summarize_prompt(prev_summary, "\n".join(conv))

                from .chat_service import call_llm
                new_summary = call_llm(
                    [{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=256,
                ).strip()

                if new_summary:
                    write_summary(chain_dir, new_summary, len(messages))
                    # 截断链：保留前 6 条（摘要覆盖了它们的内容）
                    truncate_chain(chain_dir, 6)
                    log.info("历史摘要完成: session=%s, summary=%s", session_id, new_summary[:50])
            except Exception as e:
                log.warning("历史摘要失败: session=%s, %s", session_id, e)

        threading.Thread(target=_run, daemon=True).start()

    def get_summary(self, user_id: int, session_id: str) -> dict | None:
        chain_dir = self._session_dir(user_id, session_id)
        return read_summary(chain_dir)

    def delete_session(self, user_id: int, session_id: str) -> dict:
        self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        ).delete()
        self.db.commit()
        d = self._session_dir(user_id, session_id)
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
        return Result.success("删除成功")
