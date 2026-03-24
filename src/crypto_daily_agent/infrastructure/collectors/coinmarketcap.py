"""CoinMarketCap 价格数据采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class CoinMarketCapCollector(SourceCollector):
    """CoinMarketCap 价格数据采集器."""
    
    name: ClassVar[str] = "coinmarketcap"
    priority: ClassVar[int] = 5
    
    def __init__(self, settings: Settings):
        self.api_key = settings.coinmarketcap_api_key
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": self.api_key, "Accept": "application/json"}
        params = {"symbol": "BTC,ETH", "convert": "USD"}
        
        data = await http_client.get(url, headers=headers, params=params)
        
        items = []
        for symbol in ["BTC", "ETH"]:
            crypto_data = data["data"][symbol]
            quote = crypto_data["quote"]["USD"]
            change_24h = quote["percent_change_24h"]
            items.append(NewsItem(
                source="CoinMarketCap",
                title=f"{symbol} 24h: {change_24h:+.2f}%",
                url=f"https://coinmarketcap.com/currencies/{crypto_data['slug']}/",
                published_at=datetime.now(timezone.utc),
                content=f"Price: ${quote['price']:.2f}\n24h Change: {change_24h:.2f}%",
                language="en",
                importance=2.0 if abs(change_24h) > 5 else 1.5,
            ))
        return items
