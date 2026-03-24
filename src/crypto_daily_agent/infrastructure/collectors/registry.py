"""采集器注册表."""

import logging
from typing import Type

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.utils.http_client import HttpClient

LOGGER = logging.getLogger(__name__)


class CollectorRegistry:
    """采集器注册表."""
    
    def __init__(self):
        self._collectors: dict[str, Type[SourceCollector]] = {}
    
    def register(self, collector_class: Type[SourceCollector]) -> Type[SourceCollector]:
        if not collector_class.name:
            raise ValueError(f"Collector {collector_class.__name__} must define 'name'")
        self._collectors[collector_class.name] = collector_class
        LOGGER.debug(f"Registered collector: {collector_class.name}")
        return collector_class
    
    def get_available_collectors(self, settings: Settings) -> list[SourceCollector]:
        instances = []
        sorted_collectors = sorted(self._collectors.items(), key=lambda x: x[1].priority)
        for name, cls in sorted_collectors:
            try:
                instance = cls(settings)
                if instance.is_available:
                    instances.append(instance)
            except Exception as exc:
                LOGGER.warning(f"Failed to initialize collector {name}: {exc}")
        return instances
    
    async def collect_all(self, settings: Settings, http_client: HttpClient) -> list[NewsItem]:
        import asyncio
        collectors = self.get_available_collectors(settings)
        all_items = []
        
        async def fetch_with_error_handling(collector: SourceCollector) -> list[NewsItem]:
            try:
                items = await collector.fetch(http_client)
                LOGGER.info(f"collector={collector.name} items={len(items)}")
                return items
            except Exception as exc:
                LOGGER.exception(f"collector_failed={collector.name} error={exc}")
                return []
        
        results = await asyncio.gather(*[fetch_with_error_handling(c) for c in collectors])
        for items in results:
            all_items.extend(items)
        return all_items


registry = CollectorRegistry()
register_collector = registry.register
