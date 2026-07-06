from pydantic import BaseModel, Field, field_validator


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

    @field_validator("age", mode="before")
    @classmethod
    def cast_age(cls, v):
        if v is None:
            return None
        return int(v)


class CharacterUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    appearance: str | None = None
    background: str | None = None
    personality: str | None = None
    extra: dict | str | None = None

    @field_validator("age", mode="before")
    @classmethod
    def cast_age(cls, v):
        if v is None:
            return None
        return int(v)
