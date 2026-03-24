"""X (Twitter) 列表采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class XListCollector(SourceCollector):
    """X (Twitter) 账号列表采集器."""
    
    name: ClassVar[str] = "x_list"
    priority: ClassVar[int] = 20
    ACCOUNT_IDS = ["44196397", "783214"]
    
    def __init__(self, settings: Settings):
        self.bearer_token = settings.x_bearer_token
    
    @property
    def is_available(self) -> bool:
        return bool(self.bearer_token)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        items = []
        for user_id in self.ACCOUNT_IDS:
            try:
                url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {"max_results": 5, "tweet.fields": "created_at"}
                data = await http_client.get(url, params=params, headers=headers)
                for tweet in data.get("data", []):
                    created = tweet.get("created_at", "")
                    try:
                        published = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    except ValueError:
                        published = datetime.now(timezone.utc)
                    items.append(NewsItem(
                        source="X",
                        title=tweet.get("text", "").split("\n")[0][:120],
                        url=f"https://x.com/i/web/status/{tweet.get('id', '')}",
                        published_at=published,
                        content=tweet.get("text", ""),
                        language="en",
                    ))
            except Exception:
                continue
        return items
