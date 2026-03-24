"""Tests for models module."""

import pytest
from datetime import datetime, timezone
from crypto_daily_agent.models import NewsItem, MarketData, DigestContext


def test_news_item_creation():
    """测试 NewsItem 创建."""
    item = NewsItem(
        source="Binance",
        title="Bitcoin Update",
        url="https://binance.com/news/1",
        published_at=datetime.now(timezone.utc),
        content="Bitcoin is up today",
        language="en",
    )
    assert item.source == "Binance"
    assert item.importance == 0.0
    assert len(item.fingerprint) == 16  # SHA1 前 16 位


def test_news_item_fingerprint_generation():
    """测试指纹自动生成."""
    item1 = NewsItem(
        source="Test",
        title="Same Title",
        url="https://test.com/1",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    item2 = NewsItem(
        source="Test",
        title="Same Title",
        url="https://test.com/1",
        published_at=datetime.now(timezone.utc),
        content="Different content",
    )
    # 相同 source + title + url = 相同指纹
    assert item1.fingerprint == item2.fingerprint


def test_news_item_different_fingerprints():
    """测试不同新闻有不同指纹."""
    item1 = NewsItem(
        source="Test",
        title="Title A",
        url="https://test.com/1",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    item2 = NewsItem(
        source="Test",
        title="Title B",
        url="https://test.com/2",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    assert item1.fingerprint != item2.fingerprint


def test_news_item_with_defaults():
    """测试 NewsItem 默认值."""
    item = NewsItem(
        source="Test",
        title="Test Title",
        url="https://test.com",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    assert item.language == "zh"
    assert item.importance == 0.0


def test_market_data_creation():
    """测试 MarketData 创建."""
    data = MarketData(
        symbol="BTC",
        price_usd=50000.0,
        change_24h_percent=5.5,
        source="CoinMarketCap",
    )
    assert data.symbol == "BTC"
    assert data.change_24h_percent == 5.5
    assert data.is_significant_change is True


def test_market_data_format_change():
    """测试价格变化格式化."""
    data = MarketData(
        symbol="ETH",
        price_usd=3000.0,
        change_24h_percent=-2.5,
        source="Test",
    )
    assert data.format_change() == "-2.50%"


def test_market_data_not_significant():
    """测试非显著变化."""
    data = MarketData(
        symbol="BTC",
        price_usd=50000.0,
        change_24h_percent=3.0,
        source="Test",
    )
    assert data.is_significant_change is False


def test_digest_context_creation():
    """测试 DigestContext 创建."""
    context = DigestContext(
        date_str="2026-03-24",
        market_temperature="偏热",
        headline="Bitcoin Surges",
        cards=[{"rank": 1, "title": "News 1"}],
    )
    assert context.date_str == "2026-03-24"
    assert len(context.cards) == 1
    assert context.market_data == []
