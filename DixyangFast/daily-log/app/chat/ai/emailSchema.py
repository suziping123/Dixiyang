from pydantic import BaseModel, Field


class EmailSchema(BaseModel):
    to: str = Field(description="收件人邮箱")
    subject: str = Field(description="邮件主题")
    content: str = Field(description="邮件内容")
