from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class StoryNode(Base):
    __tablename__ = "story_node"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timeline_id: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    vector_id: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[str | None] = mapped_column(String(50))
    event_type: Mapped[str | None] = mapped_column(String(20))
    importance: Mapped[int | None] = mapped_column(Integer)
    character_names: Mapped[str | list | None] = mapped_column(JSON)
    tags: Mapped[str | list | None] = mapped_column(JSON)
