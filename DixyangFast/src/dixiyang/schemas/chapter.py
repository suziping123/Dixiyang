from datetime import datetime

from pydantic import BaseModel, Field


class ChapterCreate(BaseModel):
    novel_id: int
    volume_id: int | None = None
    title: str
    sort_order: int | None = None

    class Config:
        populate_by_name = True


class ChapterUpdate(BaseModel):
    title: str | None = None
    sort_order: int | None = None
    volume_id: int | None = None

    class Config:
        populate_by_name = True


class ChapterVO(BaseModel):
    id: int
    novel_id: int
    volume_id: int | None = None
    title: str
    sort_order: int
    content_path: str | None = None
    content_hash: str | None = None
    content_size: int = 0
    version: int = 1
    local_version: int = 1
    word_count: int = 0
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True