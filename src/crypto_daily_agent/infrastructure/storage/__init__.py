"""存储模块."""

from crypto_daily_agent.infrastructure.storage.base import StateStore
from crypto_daily_agent.infrastructure.storage.json_store import JsonStateStore

__all__ = ["StateStore", "JsonStateStore"]
