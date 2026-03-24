"""配置管理 - Pydantic Settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScoringWeights(BaseModel):
    """新闻评分权重配置."""
    
    binance: float = 1.2
    bitcoin_keyword: float = 0.9
    ethereum_keyword: float = 0.7
    tier1_source: float = 0.5  # Binance, X
    tier2_source: float = 0.3  # CoinDesk, TheBlock


class Settings(BaseSettings):
    """应用配置."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 时区与定时
    tz: str = "Asia/Shanghai"
    daily_push_time: str = "08:00"
    
    # 邮件配置
    smtp_host: str = Field(default="", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=465, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    email_from: str = Field(default="", validation_alias="EMAIL_FROM")
    email_to: str = Field(default="", validation_alias="EMAIL_TO")
    enable_email: bool = Field(default=True, validation_alias="ENABLE_EMAIL")
    
    # API Keys
    newsapi_key: str = ""
    coinmarketcap_api_key: str = ""
    x_bearer_token: str = ""
    
    # 行为配置
    max_news_items: int = Field(default=10, ge=1, le=50)
    request_timeout_seconds: int = Field(default=12, ge=5, le=60)
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    storage_backend: Literal["json", "sqlite"] = "json"
    storage_cleanup_days: int = Field(default=7, ge=1, le=30)
    
    # 路径配置
    output_dir: Path = Path("output")
    state_dir: Path = Path("state")
    
    @field_validator("output_dir", "state_dir", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """确保路径是 Path 对象并创建目录."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path


def load_settings() -> Settings:
    """加载设置（兼容旧接口）."""
    return Settings()
