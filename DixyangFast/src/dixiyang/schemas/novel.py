from datetime import datetime

from pydantic import BaseModel, Field


class NovelCreate(BaseModel):
    title: str
    pen_name: str | None = Field(default=None, alias="penName")
    description: str | None = None
    cover_url: str | None = Field(default=None, alias="coverUrl")

    class Config:
        populate_by_name = True


class NovelUpdate(BaseModel):
    title: str | None = None
    pen_name: str | None = Field(default=None, alias="penName")
    description: str | None = None
    cover_url: str | None = Field(default=None, alias="coverUrl")

    class Config:
        populate_by_name = True


class NovelVO(BaseModel):
    id: int
    title: str
    pen_name: str | None = None
    description: str | None = None
    cover_url: str | None = None
    user_id: int
    char_count: int = 0
    node_count: int = 0
    relation_count: int = 0
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True
