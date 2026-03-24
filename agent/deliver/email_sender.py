from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from agent.config import Settings


def send_digest_email(settings: Settings, image_path: Path, subject: str, body: str) -> None:
    if not all(
        [
            settings.smtp_host,
            settings.smtp_user,
            settings.smtp_password,
            settings.email_from,
            settings.email_to,
        ]
    ):
        raise ValueError("SMTP or email settings are incomplete")

    msg = MIMEMultipart()
    msg["From"] = settings.email_from
    msg["To"] = settings.email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    attachment = MIMEApplication(image_path.read_bytes(), _subtype="png")
    attachment.add_header("Content-Disposition", "attachment", filename=image_path.name)
    msg.attach(attachment)

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.email_from, [settings.email_to], msg.as_string())
