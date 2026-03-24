"""共享异步 HTTP 客户端."""

import aiohttp
from typing import Any


class HttpClient:
    """异步 HTTP 客户端封装."""
    
    def __init__(self, timeout: int = 12):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get(self, url: str, **kwargs) -> dict[str, Any]:
        if not self._session:
            raise RuntimeError("Client not initialized")
        async with self._session.get(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, url: str, **kwargs) -> dict[str, Any]:
        if not self._session:
            raise RuntimeError("Client not initialized")
        async with self._session.post(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
