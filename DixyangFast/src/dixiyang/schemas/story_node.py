from pydantic import BaseModel, Field


class StoryNodeCreate(BaseModel):
    novel_id: int = Field(alias="novelId")
    timeline_id: int | None = Field(default=None, alias="timelineId")
    title: str
    content: str | None = None
    event_date: str | None = Field(default=None, alias="eventDate")
    event_type: str | None = Field(default=None, alias="eventType")
    importance: int | None = None
    character_names: str | None = Field(default=None, alias="characterNames")
    tags: str | None = None

    model_config = {"populate_by_name": True}


class StoryNodeUpdate(BaseModel):
    timeline_id: int | None = Field(default=None, alias="timelineId")
    title: str | None = None
    content: str | None = None
    event_date: str | None = Field(default=None, alias="eventDate")
    event_type: str | None = Field(default=None, alias="eventType")
    importance: int | None = None
    character_names: str | None = Field(default=None, alias="characterNames")
    tags: str | None = None
