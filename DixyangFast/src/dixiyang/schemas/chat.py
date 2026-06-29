from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    novel_id: int | None = Field(default=None, alias="novelId")
    character_ids: list[int] | None = Field(default=None, alias="characterIds")
    story_node_ids: list[int] | None = Field(default=None, alias="storyNodeIds")
    include_characters: bool = Field(default=True, alias="includeCharacters")
    include_story: bool = Field(default=True, alias="includeStory")
    session_id: str | None = Field(default=None, alias="sessionId")
    regenerate_index: int = Field(default=-1, alias="regenerateIndex")

    model_config = {"populate_by_name": True}
