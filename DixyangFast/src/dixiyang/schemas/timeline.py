from pydantic import BaseModel, Field


class TimelineCreate(BaseModel):
    novel_id: int = Field(alias="novelId")
    name: str
    description: str | None = None

    model_config = {"populate_by_name": True}


class TimelineUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
