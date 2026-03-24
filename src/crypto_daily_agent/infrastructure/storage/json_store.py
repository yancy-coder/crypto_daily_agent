"""JSON 文件存储实现."""

from __future__ import annotations

import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path

from crypto_daily_agent.infrastructure.storage.base import StateStore


class JsonStateStore(StateStore):
    """JSON 文件实现 - 带自动清理."""
    
    def __init__(self, file_path: Path, cleanup_days: int = 7, auto_cleanup_threshold: int = 1000):
        self.file_path = Path(file_path)
        self.cleanup_days = cleanup_days
        self.auto_cleanup_threshold = auto_cleanup_threshold
        self._cache: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._load()
    
    def _load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache = data.get("entries", {})
            except (json.JSONDecodeError, IOError):
                self._cache = {}
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._cache = {}
    
    async def _save(self) -> None:
        async with self._lock:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"entries": self._cache}, f, ensure_ascii=False, indent=2)
    
    async def is_pushed(self, fingerprint: str) -> bool:
        return fingerprint in self._cache
    
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        for fp in fingerprints:
            self._cache[fp] = now
        await self._save()
        if len(self._cache) > self.auto_cleanup_threshold:
            await self.cleanup_old(self.cleanup_days)
    
    async def cleanup_old(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        old_keys = [k for k, v in self._cache.items() if v < cutoff_str]
        for k in old_keys:
            del self._cache[k]
        if old_keys:
            await self._save()
        return len(old_keys)
    
    async def get_stats(self) -> dict[str, int]:
        return {"total_entries": len(self._cache)}
