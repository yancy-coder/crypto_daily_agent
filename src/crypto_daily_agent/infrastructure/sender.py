"""邮件发送器."""

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import DigestContext

LOGGER = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send_digest(self, image_path: Path, context: DigestContext) -> None:
        if not self._is_configured():
            raise ValueError("SMTP settings are incomplete")
        
        subject = f"[Crypto Daily] {context.date_str} 市场资讯"
        body = f"今日为你筛选 {len(context.cards)} 条加密资讯。\n市场温度：{context.market_temperature}\n详见附件图片。"
        
        try:
            await self._send_email(subject, body, image_path)
            LOGGER.info(f"email_sent file={image_path}")
        except Exception as exc:
            LOGGER.exception(f"email_send_failed error={exc}")
            await self._send_alert(f"推送失败: {exc}")
            raise
    
    def _is_configured(self) -> bool:
        return all([self.settings.smtp_host, self.settings.smtp_user, 
                   self.settings.smtp_password, self.settings.email_from, self.settings.email_to])
    
    async def _send_email(self, subject: str, body: str, attachment: Path) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.settings.email_from
        msg["To"] = self.settings.email_to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        with open(attachment, "rb") as f:
            attachment_data = MIMEApplication(f.read(), _subtype="png")
        attachment_data.add_header("Content-Disposition", "attachment", filename=attachment.name)
        msg.attach(attachment_data)
        
        with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.sendmail(self.settings.email_from, [self.settings.email_to], msg.as_string())
    
    async def _send_alert(self, message: str) -> None:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.settings.email_from
            msg["To"] = self.settings.email_to
            msg["Subject"] = "[Crypto Daily][ALERT] 推送失败"
            msg.attach(MIMEText(f"{message}\n请检查日志与配置。", "plain", "utf-8"))
            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.sendmail(self.settings.email_from, [self.settings.email_to], msg.as_string())
        except Exception as exc:
            LOGGER.error(f"alert_email_failed error={exc}")
