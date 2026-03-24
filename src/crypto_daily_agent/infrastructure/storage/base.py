"""存储抽象层."""

from abc import ABC, abstractmethod


class StateStore(ABC):
    """状态存储抽象 - 支持多种后端."""
    
    @abstractmethod
    async def is_pushed(self, fingerprint: str) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def cleanup_old(self, days: int = 7) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def get_stats(self) -> dict[str, int]:
        raise NotImplementedError
