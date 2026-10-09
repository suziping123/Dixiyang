"""点子库请求模型（snake_case 字段 + camelCase alias，项目惯例）"""
from pydantic import BaseModel, Field


class DraftBase(BaseModel):
    category: str = "idea"
    title: str
    content: str = ""
    tags: list[str] = []
    source_ref: str | None = Field(default=None, alias="sourceRef")

    model_config = {"populate_by_name": True}


class DraftCreate(DraftBase):
    pass


class DraftUpdate(DraftBase):
    pass


class PublishRequest(BaseModel):
    previewed: bool = False


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


class CommentCreate(BaseModel):
    content: str


class ImportRequest(BaseModel):
    novel_id: int = Field(alias="novelId")

    model_config = {"populate_by_name": True}
