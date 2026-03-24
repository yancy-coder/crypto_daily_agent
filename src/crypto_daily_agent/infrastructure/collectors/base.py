"""采集器抽象基类."""

from abc import ABC, abstractmethod
from typing import ClassVar

from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.utils.http_client import HttpClient


class SourceCollector(ABC):
    """数据源采集器抽象基类."""
    
    name: ClassVar[str] = ""
    priority: ClassVar[int] = 100
    
    @abstractmethod
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        raise NotImplementedError
    
    @property
    def is_available(self) -> bool:
        return True
