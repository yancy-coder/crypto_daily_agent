from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import feedparser
import requests

from agent.config import Settings
from agent.models import NewsItem
from agent.sources.base import SourceCollector


class BinanceAnnouncementCollector(SourceCollector):
    """Uses Binance support API-like endpoint with graceful fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch(self) -> List[NewsItem]:
        url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
        payload = {
            "type": 1,
            "catalogId": "48",
            "pageNo": 1,
            "pageSize": 20,
        }
        try:
            resp = requests.post(
                url,
                json=payload,
                timeout=self.settings.request_timeout_seconds,
                headers={"User-Agent": "crypto-daily-agent/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return self._fallback_rss()

        records = data.get("data", {}).get("articles", [])
        items: List[NewsItem] = []
        for row in records:
            code = row.get("code", "")
            items.append(
                NewsItem(
                    source="Binance",
                    title=row.get("title", "").strip(),
                    url=f"https://www.binance.com/zh-CN/support/announcement/{code}",
                    published_at=datetime.fromtimestamp(
                        int(row.get("releaseDate", 0)) / 1000, tz=timezone.utc
                    ),
                    content=row.get("summary", "") or row.get("body", ""),
                    language="zh",
                )
            )
        return items or self._fallback_rss()

    def _fallback_rss(self) -> List[NewsItem]:
        feed = feedparser.parse("https://www.binance.com/en/support/announcement/rss")
        items: List[NewsItem] = []
        for e in feed.entries[:20]:
            published = datetime.now(tz=timezone.utc)
            if getattr(e, "published_parsed", None):
                published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            items.append(
                NewsItem(
                    source="Binance",
                    title=e.get("title", "").strip(),
                    url=e.get("link", ""),
                    published_at=published,
                    content=e.get("summary", "")[:500],
                    language="en",
                )
            )
        return items
