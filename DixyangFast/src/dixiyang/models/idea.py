"""点子库与创意社区数据模型（7 张表，create_all 自动建表）"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class IdeaPost(Base):
    """社区帖子"""
    __tablename__ = "idea_post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="idea")  # idea/character/setting/timeline/tech
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(300))
    body_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="published")  # published/removed
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    collect_count: Mapped[int] = mapped_column(Integer, default=0)
    hot_score: Mapped[int] = mapped_column(BigInteger, default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class IdeaDraft(Base):
    """私有点子草稿"""
    __tablename__ = "idea_draft"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="idea")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(300))
    body_path: Mapped[str] = mapped_column(String(500), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(64))  # sessionId / characterId（发布时才复制）
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class IdeaAttachment(Base):
    """帖子结构化只读附件（对话快照/角色卡等）"""
    __tablename__ = "idea_attachment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # chat_snapshot/character_card/setting_bundle/timeline_view
    attach_path: Mapped[str] = mapped_column(String(500), nullable=False)
    attach_meta: Mapped[str | None] = mapped_column(Text)  # JSON 字符串：轮数/角色名等展示元数据
    source_ref: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IdeaPostTag(Base):
    """帖子标签（关联表，一帖多标签）"""
    __tablename__ = "idea_post_tag"
    __table_args__ = (UniqueConstraint("post_id", "tag", name="uq_idea_post_tag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tag: Mapped[str] = mapped_column(String(50), nullable=False, index=True)


class IdeaLike(Base):
    """点赞（UNIQUE 防重复）"""
    __tablename__ = "idea_like"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_idea_like"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IdeaCollect(Base):
    """收藏（灵感夹）"""
    __tablename__ = "idea_collect"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_idea_collect"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IdeaComment(Base):
    """评论（平铺，短文本直接入 DB）"""
    __tablename__ = "idea_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
