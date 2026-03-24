"""数据模型定义."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class NewsItem:
    """新闻条目模型."""
    
    source: str
    title: str
    url: str
    published_at: datetime
    content: str
    language: str = "zh"
    importance: float = 0.0
    fingerprint: str = ""
    
    def __post_init__(self):
        """生成指纹（如果未提供）."""
        if not self.fingerprint:
            self.fingerprint = self._generate_fingerprint()
    
    def _generate_fingerprint(self) -> str:
        """基于 source + title + url 生成唯一指纹."""
        base = f"{self.source}|{self.title}|{self.url}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


@dataclass
class MarketData:
    """市场数据模型（价格信息）."""
    
    symbol: str
    price_usd: float
    change_24h_percent: float
    source: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def is_significant_change(self) -> bool:
        """是否有显著价格变化（>5%）."""
        return abs(self.change_24h_percent) > 5.0
    
    def format_change(self) -> str:
        """格式化价格变化显示."""
        return f"{self.change_24h_percent:+.2f}%"


@dataclass
class DigestContext:
    """每日资讯汇总上下文（用于渲染）."""
    
    date_str: str
    market_temperature: str
    headline: str
    cards: list[dict]
    market_data: list[MarketData] = field(default_factory=list)
