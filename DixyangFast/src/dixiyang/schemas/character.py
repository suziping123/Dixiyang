from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    novel_id: int = Field(alias="novelId")
    name: str
    gender: str | None = None
    age: int | None = None
    appearance: str | None = None
    background: str | None = None
    personality: str | None = None
    extra: dict | str | None = None

    model_config = {"populate_by_name": True}


class CharacterUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    appearance: str | None = None
    background: str | None = None
    personality: str | None = None
    extra: dict | str | None = None
