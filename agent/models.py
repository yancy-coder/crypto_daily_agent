from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsItem:
    source: str
    title: str
    url: str
    published_at: datetime
    content: str
    language: str = "zh"
    importance: float = 0.0
    fingerprint: str = ""
