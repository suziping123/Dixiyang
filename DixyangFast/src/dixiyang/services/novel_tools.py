import json
import logging
import os
from typing import Annotated

from langchain_core.tools import tool, InjectedToolArg

from ..models.character import NovelCharacter
from ..models.timeline import Timeline
from ..models.story_node import StoryNode
from ..utils.database import SessionLocal

log = logging.getLogger(__name__)


def get_all_tools(novel_id: int) -> list:
    """创建绑定到具体小说的工具列表"""

    @tool
    def get_novel_characters() -> str:
        """获取当前小说的所有角色列表及属性（姓名/性别/年龄/外貌/性格/背景）"""
        with SessionLocal() as db:
            chars = db.query(NovelCharacter).filter(NovelCharacter.novel_id == novel_id).all()
            if not chars:
                return "当前小说暂无角色"
            rows = []
            for c in chars:
                attrs = {"name": c.name}
                if c.gender:
                    attrs["gender"] = c.gender
                if c.age is not None:
                    attrs["age"] = c.age
                if c.appearance:
                    attrs["appearance"] = c.appearance
                if c.personality:
                    attrs["personality"] = c.personality
                if c.background:
                    attrs["background"] = c.background
                rows.append(attrs)
            return json.dumps(rows, ensure_ascii=False, indent=2)

    @tool
    def get_timeline() -> str:
        """获取当前小说的故事时间线。返回各时间段的名称和描述。"""
        with SessionLocal() as db:
            entries = db.query(Timeline).filter(Timeline.novel_id == novel_id).order_by(Timeline.id).all()
            if not entries:
                return "当前小说暂无时间线"
            rows = []
            for t in entries:
                row = {"id": t.id, "name": t.name, "parent_id": t.parent_id}
                if t.description:
                    row["description"] = t.description[:200]
                rows.append(row)
            return json.dumps(rows, ensure_ascii=False, indent=2)

    @tool
    def get_story_nodes() -> str:
        """获取当前小说的所有故事节点（章节/场景）列表。返回标题、内容摘要、事件信息。"""
        with SessionLocal() as db:
            nodes = db.query(StoryNode).filter(StoryNode.novel_id == novel_id).order_by(StoryNode.id).all()
            if not nodes:
                return "当前小说暂无故事节点"
            rows = []
            for n in nodes:
                row = {"id": n.id, "title": n.title or ""}
                if n.event_date:
                    row["event_date"] = n.event_date
                if n.event_type:
                    row["event_type"] = n.event_type
                if n.importance:
                    row["importance"] = n.importance
                if n.character_names:
                    row["character_names"] = n.character_names
                if n.content:
                    row["content"] = n.content[:500]
                rows.append(row)
            return json.dumps(rows, ensure_ascii=False, indent=2)

    @tool
    def get_novel_setting(query: str) -> str:
        """搜索小说的世界观设定资料（地理/魔法/历史/文化等）。当你需要查阅世界观背景设定时调用。"""
        from .knowledge_search_tool import knowledge_search
        return knowledge_search.invoke({"query": query, "top_k": 5, "doc_type": "worldbuilding"})

    @tool
    def save_to_knowledge(text: str, source: str = "AI笔记") -> str:
        """将创作笔记、灵感、设定说明等信息保存到知识库，供后续检索。"""
        from .embeddings import DixiyangEmbeddings
        from langchain_chroma import Chroma
        try:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
            collection_name = os.getenv("CHROMA_COLLECTION_NAME", "dixiyang_knowledge")
            vs = Chroma(
                collection_name=collection_name,
                embedding_function=DixiyangEmbeddings(),
                persist_directory=persist_dir,
            )
            vs.add_texts(
                texts=[text],
                metadatas=[{"source": source, "novel_id": str(novel_id), "type": "note"}],
            )
            return f"已保存到知识库（来源: {source}）"
        except Exception as e:
            log.warning("save_to_knowledge 失败: %s", e)
            return f"保存失败: {e}"

    return [get_novel_characters, get_timeline, get_story_nodes, get_novel_setting, save_to_knowledge]
