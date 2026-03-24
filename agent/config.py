from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    tz: str
    daily_push_time: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_from: str
    email_to: str
    newsapi_key: str
    coinmarketcap_api_key: str
    x_bearer_token: str
    max_news_items: int
    request_timeout_seconds: int
    enable_email: bool
    state_file: Path
    output_dir: Path


def load_settings() -> Settings:
    load_dotenv()
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        tz=os.getenv("TZ", "Asia/Shanghai"),
        daily_push_time=os.getenv("DAILY_PUSH_TIME", "08:00"),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "465")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        email_from=os.getenv("EMAIL_FROM", ""),
        email_to=os.getenv("EMAIL_TO", ""),
        newsapi_key=os.getenv("NEWSAPI_KEY", ""),
        coinmarketcap_api_key=os.getenv("COINMARKETCAP_API_KEY", ""),
        x_bearer_token=os.getenv("X_BEARER_TOKEN", ""),
        max_news_items=int(os.getenv("MAX_NEWS_ITEMS", "10")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "12")),
        enable_email=os.getenv("ENABLE_EMAIL", "true").lower() == "true",
        state_file=base_dir / "state" / "cache.json",
        output_dir=output_dir,
    )
