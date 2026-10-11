"""拟物便利贴灵感墙数据模型（1 张表，create_all 自动建表）

DB 只存元数据；正文/图片列表存文件 storage/sticky/{userId}/{noteId}.json（AGENTS §7）。
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class StickyNote(Base):
    """便利贴灵感（全站悬浮层：钉在某路由只在该路由显示）"""
    __tablename__ = "sticky_note"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="yellow")  # yellow/pink/blue/green/purple
    # 坐标为归一化百分比（0~1，相对视口），窗口缩放不漂移
    x: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    y: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    pinned_route: Mapped[str | None] = mapped_column(String(200))  # 钉住的路由 path；NULL=浮动（全站可见可拖）
    in_pool: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 已投喂 AI 补全素材池 0/1
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 拟物微旋转角（度）
    z_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 层叠顺序（点选置顶）
    done: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 完成态 0/1
    content_path: Mapped[str] = mapped_column(String(500), nullable=False)  # __file__:sticky/{uid}/{nid}.json
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
