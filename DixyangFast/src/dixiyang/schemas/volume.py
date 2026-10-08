from datetime import datetime

from pydantic import BaseModel, Field


class VolumeCreate(BaseModel):
    title: str
    sort_order: int | None = None
    description: str | None = None

    class Config:
        populate_by_name = True


class VolumeUpdate(BaseModel):
    title: str | None = None
    sort_order: int | None = None
    description: str | None = None

    class Config:
        populate_by_name = True


class VolumeVO(BaseModel):
    id: int
    novel_id: int
    title: str
    sort_order: int
    description: str | None = None
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True