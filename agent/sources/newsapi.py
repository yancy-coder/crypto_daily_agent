from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import requests

from agent.config import Settings
from agent.models import NewsItem
from agent.sources.base import SourceCollector


class NewsApiCollector(SourceCollector):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch(self) -> List[NewsItem]:
        if not self.settings.newsapi_key:
            return []
        params = {
            "q": "crypto OR bitcoin OR ethereum",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": self.settings.newsapi_key,
        }
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=self.settings.request_timeout_seconds,
                headers={"User-Agent": "crypto-daily-agent/1.0"},
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            return []

        items: List[NewsItem] = []
        for article in payload.get("articles", []):
            published_str = article.get("publishedAt", "")
            try:
                published = datetime.fromisoformat(
                    published_str.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            except ValueError:
                published = datetime.now(tz=timezone.utc)
            items.append(
                NewsItem(
                    source=(article.get("source") or {}).get("name", "NewsAPI"),
                    title=article.get("title", "").strip(),
                    url=article.get("url", ""),
                    published_at=published,
                    content=article.get("description", "") or article.get("content", ""),
                    language="en",
                )
            )
        return items
