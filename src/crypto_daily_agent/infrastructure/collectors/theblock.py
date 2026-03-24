"""TheBlock RSS 采集器."""

from datetime import datetime, timezone
from typing import ClassVar

import feedparser

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class TheBlockCollector(SourceCollector):
    """TheBlock RSS 采集器."""
    
    name: ClassVar[str] = "theblock"
    priority: ClassVar[int] = 40
    RSS_URL = "https://www.theblock.co/rss.xml"
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        feed = feedparser.parse(self.RSS_URL)
        items = []
        for entry in feed.entries[:20]:
            published = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            items.append(NewsItem(
                source="TheBlock",
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                published_at=published,
                content=entry.get("summary", "")[:500],
                language="en",
            ))
        return items
