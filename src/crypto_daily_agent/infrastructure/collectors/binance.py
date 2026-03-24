"""Binance 公告采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class BinanceCollector(SourceCollector):
    """Binance 公告采集器."""
    
    name: ClassVar[str] = "binance"
    priority: ClassVar[int] = 10
    
    def __init__(self, settings: Settings):
        self.timeout = settings.request_timeout_seconds
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
        payload = {"type": 1, "catalogId": "48", "pageNo": 1, "pageSize": 20}
        headers = {"User-Agent": "crypto-daily-agent/2.0"}
        
        try:
            data = await http_client.post(url, json=payload, headers=headers)
        except Exception:
            return await self._fetch_rss(http_client)
        
        records = data.get("data", {}).get("articles", [])
        items = []
        for row in records:
            code = row.get("code", "")
            items.append(NewsItem(
                source="Binance",
                title=row.get("title", "").strip(),
                url=f"https://www.binance.com/zh-CN/support/announcement/{code}",
                published_at=datetime.fromtimestamp(
                    int(row.get("releaseDate", 0)) / 1000, tz=timezone.utc
                ),
                content=row.get("summary", "") or row.get("body", ""),
                language="zh",
            ))
        return items or await self._fetch_rss(http_client)
    
    async def _fetch_rss(self, http_client: HttpClient) -> list[NewsItem]:
        import feedparser
        feed = feedparser.parse("https://www.binance.com/en/support/announcement/rss")
        items = []
        for entry in feed.entries[:20]:
            published = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            items.append(NewsItem(
                source="Binance",
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                published_at=published,
                content=entry.get("summary", "")[:500],
                language="en",
            ))
        return items
