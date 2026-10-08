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
    # 用户提问编辑：置 true 时后端同步截断其后的问答
    truncate_after: bool = Field(alias="truncateAfter", default=False)


class VersionRefRequest(BaseModel):
    """版本恢复/删除请求。field: versions=独立编辑历史 / paired=与提问版本成对的回答存档"""
    message_index: int = Field(alias="messageIndex", default=-1)
    version_index: int = Field(alias="versionIndex", default=-1)
    field: str = "versions"


class DeleteCurrentRequest(BaseModel):
    """删除"当前版本"（最新格）并回退上一版。target: pair=提问成对回退 / self=本消息回退"""
    message_index: int = Field(alias="messageIndex", default=-1)
    target: str = "pair"
