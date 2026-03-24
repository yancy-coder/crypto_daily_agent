"""NewsAPI 采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class NewsAPICollector(SourceCollector):
    """NewsAPI 采集器."""
    
    name: ClassVar[str] = "newsapi"
    priority: ClassVar[int] = 50
    
    def __init__(self, settings: Settings):
        self.api_key = settings.newsapi_key
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "crypto OR bitcoin OR ethereum",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": self.api_key,
        }
        headers = {"User-Agent": "crypto-daily-agent/2.0"}
        
        try:
            data = await http_client.get(url, params=params, headers=headers)
        except Exception:
            return []
        
        items = []
        for article in data.get("articles", []):
            published_str = article.get("publishedAt", "")
            try:
                published = datetime.fromisoformat(published_str.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                published = datetime.now(timezone.utc)
            items.append(NewsItem(
                source=article.get("source", {}).get("name", "NewsAPI"),
                title=article.get("title", "").strip(),
                url=article.get("url", ""),
                published_at=published,
                content=article.get("description", "") or article.get("content", ""),
                language="en",
            ))
        return items
