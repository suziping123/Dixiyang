import json
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, JSON, func, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class NovelCharacter(Base):
    __tablename__ = "novel_character"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    novel_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(10))
    age: Mapped[int | None] = mapped_column(Integer)
    appearance: Mapped[str | None] = mapped_column(Text)
    background: Mapped[str | None] = mapped_column(Text)
    personality: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict | None] = mapped_column(JSON)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
