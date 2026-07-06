from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    novel_id: int | None = Field(default=None, alias="novelId")
    title: str = "新对话"


class BatchSaveRequest(BaseModel):
    session_id: str = Field(alias="sessionId")
    novel_id: int | None = Field(default=None, alias="novelId")
    messages: list


class EditMessageRequest(BaseModel):
    message_index: int = Field(alias="messageIndex", default=-1)
    role: str = "user"
    content: str = ""
