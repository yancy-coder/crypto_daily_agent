"""基础设施层."""

from crypto_daily_agent.infrastructure.storage import StateStore, JsonStateStore
from crypto_daily_agent.infrastructure.collectors import (
    SourceCollector,
    CollectorRegistry,
    register_collector,
    registry,
)
from crypto_daily_agent.infrastructure.render import ImageRenderer
from crypto_daily_agent.infrastructure.sender import EmailSender

__all__ = [
    "StateStore",
    "JsonStateStore",
    "SourceCollector",
    "CollectorRegistry",
    "register_collector",
    "registry",
    "ImageRenderer",
    "EmailSender",
]
