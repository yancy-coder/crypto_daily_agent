"""采集器模块."""

from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import (
    CollectorRegistry,
    register_collector,
    registry,
)

__all__ = ["SourceCollector", "CollectorRegistry", "register_collector", "registry"]
