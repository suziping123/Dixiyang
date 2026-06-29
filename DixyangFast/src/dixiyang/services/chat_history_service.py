import json
import os
import shutil
import uuid
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from ..config import STORAGE_DIR
from ..models.chat_session import ChatSession
from ..utils.database import get_db
from ..utils.response import Result
from .chat_service import load_chain_messages, save_chain_file


class ChatHistoryService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _session_dir(self, user_id: int, session_id: str) -> str:
        return os.path.join(STORAGE_DIR, "chat", str(user_id), session_id)

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
        messages = load_chain_messages(chain_dir)
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
        all_msgs = load_chain_messages(chain_dir)
        if message_index < 0 or message_index >= len(all_msgs):
            return Result.error("消息索引越界")

        original = all_msgs[message_index].get("content", "")
        all_msgs[message_index]["role"] = role
        all_msgs[message_index]["content"] = content

        # 重写所有链文件
        for fname in os.listdir(chain_dir):
            if fname.endswith(".json") and fname != "edits.json":
                os.remove(os.path.join(chain_dir, fname))
        save_chain_file(chain_dir, all_msgs)

        # 记录到 edits.json
        edits_path = os.path.join(chain_dir, "edits.json")
        edits: list = []
        if os.path.isfile(edits_path):
            try:
                with open(edits_path, encoding="utf-8") as f:
                    edits = json.load(f)
            except Exception:
                edits = []
        edits.append({
            "message_index": message_index,
            "original": original,
            "edited": content,
            "timestamp": datetime.now().isoformat(),
            "version": len(edits) + 1,
        })
        with open(edits_path, "w", encoding="utf-8") as f:
            json.dump(edits, f, ensure_ascii=False, indent=2)

        return Result.success("编辑成功")

    def generate_title(self, user_id: int, session_id: str) -> dict:
        from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
        from .chat_service import load_chain_messages

        session = self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            return Result.error("会话不存在")

        chain_dir = self._session_dir(user_id, session_id)
        messages = load_chain_messages(chain_dir)
        if not messages:
            title = f"对话_{session_id[:8]}"
            session.title = title
            self.db.commit()
            return Result.success("标题生成成功", title)

        conv = []
        for msg in messages[:4]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role and content:
                label = "用户" if role == "user" else "AI"
                conv.append(f"{label}：{content[:200]}")

        prompt = (
            "你是一个对话标题生成器。请用3-8个字概括以下对话的主题，"
            "直接返回标题，不要任何解释、标点或引号。\n\n对话：\n"
            + "\n".join(conv)
        )
        try:
            from openai import OpenAI
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=32,
            )
            title = resp.choices[0].message.content.strip() if resp.choices else None
            if not title:
                title = f"对话_{session_id[:8]}"
        except Exception:
            title = f"对话_{session_id[:8]}"

        session.title = title
        self.db.commit()
        return Result.success("标题生成成功", title)

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
