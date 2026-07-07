import os
import smtplib
from email.mime.text import MIMEText

from langchain_core.tools import tool

from app.chat.ai.emailSchema import EmailSchema


@tool("send_email", args_schema=EmailSchema)
def send_email_tool(to: str, subject: str, content: str) -> str:
    """
    发送邮件工具。收件人、主题、内容由Agent根据用户意图自动填充。
    """
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
