import json
import os
import smtplib
from email.mime.text import MIMEText
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class EmailInput(BaseModel):
    args: str = Field(description="JSON字符串，包含to/subject/content字段")


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = "发送邮件工具。输入JSON字符串包含to/subject/content三个字段"
    args_schema: Type[BaseModel] = EmailInput

    def _run(self, args: str) -> str:
        try:
            params = json.loads(args)
        except json.JSONDecodeError:
            return f"错误：参数格式错误，需要JSON格式，收到：{args}"
        to = params.get("to", "").strip()
        subject = params.get("subject", "").strip()
        content = params.get("content", "").strip()
        if not to or not subject or not content:
            return f"错误：缺少必要参数(to/subject/content)，收到：{args}"
        email_from = os.getenv("EMAIL_FROM", "3268845120@qq.com").strip()
        email_host = os.getenv("EMAIL_HOST", "smtp.qq.com").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        if not smtp_password:
            return "错误：未配置SMTP_PASSWORD环境变量，无法发送邮件"
        try:
            msg = MIMEText(content, _charset="utf-8")
            msg["To"] = to
            msg["Subject"] = subject
            msg["From"] = email_from
            smtp = smtplib.SMTP_SSL(email_host, 465)
            smtp.login(email_from, smtp_password)
            smtp.sendmail(email_from, to, msg.as_string())
            smtp.quit()
            return f"邮件已成功发送到 {to}"
        except Exception as e:
            return f"邮件发送失败：{e}"


send_email_tool = SendEmailTool()
