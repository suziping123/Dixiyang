from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class UserConfig(Base):
    __tablename__ = "user_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    preset: Mapped[str | None] = mapped_column(String(50))
    anim_enabled: Mapped[bool | None] = mapped_column(Boolean, default=True)
    intensity: Mapped[int | None] = mapped_column(Integer, default=50)
    color_theme: Mapped[str | None] = mapped_column(String(50))
    custom_image_url: Mapped[str | None] = mapped_column(String(500))
    background_id: Mapped[str | None] = mapped_column(String(100))
    custom_bgs: Mapped[dict | None] = mapped_column(JSON)
    font_colors_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
