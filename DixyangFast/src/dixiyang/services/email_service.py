import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

logger = logging.getLogger(__name__)


def send_verification_code(to_email: str, code: str) -> bool:
    """同步发送验证码邮件（在 FastAPI 线程池中运行）"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = "【DIXIYANG】邮箱验证码"

        html = f"""
        <div style="max-width:400px;margin:0 auto;padding:20px;font-family:Arial,sans-serif;">
          <h2 style="text-align:center;color:#6366f1;">DIXIYANG ENGINE</h2>
          <p>您好，您的邮箱验证码为：</p>
          <div style="text-align:center;margin:20px 0;">
            <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#333;">{code}</span>
          </div>
          <p style="color:#999;font-size:13px;">验证码 5 分钟内有效，请勿泄露给他人。</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <p style="color:#bbb;font-size:12px;">如非本人操作，请忽略此邮件。</p>
        </div>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

        logger.info("验证码邮件已发送: to=%s", to_email)
        return True
    except Exception as e:
        logger.error("发送验证码邮件失败: to=%s, error=%s", to_email, e)
        return False
