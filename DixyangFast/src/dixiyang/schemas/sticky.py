"""便利贴灵感请求模型（camelCase alias，项目惯例）"""
from pydantic import BaseModel, Field

ALLOWED_COLORS = {"yellow", "pink", "blue", "green", "purple"}


class NoteCreate(BaseModel):
    content: str = ""
    color: str = "yellow"
    x: float = Field(default=0.1, ge=0, le=1)
    y: float = Field(default=0.1, ge=0, le=1)
    images: list[str] = []

    model_config = {"populate_by_name": True}


class NoteUpdate(BaseModel):
    """None = 不改；解锁用 pinned=False 单独表达（避免 null 歧义）"""
    content: str | None = None
    color: str | None = None
    x: float | None = Field(default=None, ge=0, le=1)
    y: float | None = Field(default=None, ge=0, le=1)
    images: list[str] | None = None
    pinned: bool | None = None          # True=钉在 routePath；False=解锁（回浮动）
    route_path: str | None = Field(default=None, alias="routePath")
    in_pool: bool | None = Field(default=None, alias="inPool")
    z_index: int | None = Field(default=None, alias="zIndex")
    done: bool | None = None

    model_config = {"populate_by_name": True}
