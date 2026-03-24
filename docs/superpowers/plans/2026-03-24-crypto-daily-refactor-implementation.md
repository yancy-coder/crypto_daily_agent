# Crypto Daily Agent 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 crypto_daily_agent 重构为现代化、可测试、可扩展的每日加密资讯推送系统

**Architecture:** 分层架构（Application → Pipeline → Infrastructure），插件化采集器，依赖注入，Pydantic 配置验证

**Tech Stack:** Python 3.11+, Pydantic Settings, pytest, pytest-asyncio, aiosqlite

**Design Spec:** `docs/superpowers/specs/2026-03-24-crypto-daily-refactor-design.md`

---

## Phase 1: 基础设施搭建 (Foundation)

### Task 1: 创建新目录结构

**Files:**
- Create: `pyproject.toml`
- Create: `pytest.ini`
- Create: `src/crypto_daily_agent/__init__.py`
- Create: `src/crypto_daily_agent/__main__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Context:** 将项目迁移到标准 Python 包结构 (PEP 420)

- [ ] **Step 1: 创建 pyproject.toml**

Create: `pyproject.toml`

```toml
[project]
name = "crypto_daily_agent"
version = "2.0.0"
description = "每日加密资讯图片推送 Agent"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.32.0",
    "feedparser>=6.0.11",
    "beautifulsoup4>=4.12.3",
    "jinja2>=3.1.4",
    "playwright>=1.53.0",
    "python-dotenv>=1.1.0",
    "apscheduler>=3.10.4",
    "Pillow>=11.2.1",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "aiosqlite>=0.20.0",
    "aiohttp>=3.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "aioresponses>=0.7.0",
    "ruff>=0.3.0",
    "pyright>=1.1.350",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "N", "D", "UP", "B", "C4", "SIM"]

[tool.pyright]
pythonVersion = "3.11"
strict = ["src"]
```

- [ ] **Step 2: 创建 pytest.ini**

Create: `pytest.ini`

```ini
[pytest]
testpaths = tests
asyncio_mode = auto
pythonpath = src
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

- [ ] **Step 3: 创建 src 目录结构**

```bash
mkdir -p src/crypto_daily_agent/{application,pipeline,infrastructure/{collectors,storage},utils}
mkdir -p tests/{unit,integration,fixtures}
```

Create: `src/crypto_daily_agent/__init__.py`

```python
"""Crypto Daily Agent - 每日加密资讯推送系统."""

__version__ = "2.0.0"
```

Create: `src/crypto_daily_agent/__main__.py`

```python
"""CLI 入口点."""

from crypto_daily_agent.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 创建测试基础**

Create: `tests/conftest.py`

```python
"""Pytest fixtures."""

import pytest
from pathlib import Path
from crypto_daily_agent.config import Settings, ScoringWeights


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """测试配置 - 禁用邮件，使用临时目录."""
    return Settings(
        tz="Asia/Shanghai",
        daily_push_time="08:00",
        smtp_host="",
        smtp_port=465,
        smtp_user="",
        smtp_password="",
        email_from="",
        email_to="",
        enable_email=False,
        newsapi_key="",
        coinmarketcap_api_key="",
        x_bearer_token="",
        max_news_items=5,
        request_timeout_seconds=10,
        scoring_weights=ScoringWeights(),
        storage_backend="json",
        storage_cleanup_days=7,
        output_dir=tmp_path / "output",
        state_dir=tmp_path / "state",
    )


@pytest.fixture
def sample_news_item():
    """示例新闻数据."""
    from crypto_daily_agent.models import NewsItem
    from datetime import datetime, timezone
    
    return NewsItem(
        source="TestSource",
        title="Bitcoin Reaches New Heights",
        url="https://example.com/news/1",
        published_at=datetime.now(timezone.utc),
        content="Bitcoin price has increased significantly...",
        language="en",
    )
```

- [ ] **Step 5: 提交**

```bash
git add pyproject.toml pytest.ini src/ tests/
git commit -m "chore: Setup project structure with pyproject.toml and pytest"
```

---

### Task 2: 创建数据模型

**Files:**
- Create: `src/crypto_daily_agent/models.py`
- Create: `tests/unit/test_models.py`

**Context:** 定义完整的数据模型，包括 NewsItem 和新增的价格数据模型

- [ ] **Step 1: 编写模型测试**

Create: `tests/unit/test_models.py`

```python
"""Tests for models module."""

import pytest
from datetime import datetime, timezone
from crypto_daily_agent.models import NewsItem, MarketData


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
    assert item.fingerprint == ""


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
```

Run: `pytest tests/unit/test_models.py -v`
Expected: FAIL (models not yet created)

- [ ] **Step 2: 实现数据模型**

Create: `src/crypto_daily_agent/models.py`

```python
"""数据模型定义."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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
        import hashlib
        base = f"{self.source}|{self.title}|{self.url}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


@dataclass
class MarketData:
    """市场数据模型（价格信息）."""
    
    symbol: str
    price_usd: float
    change_24h_percent: float
    source: str
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    
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
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/unit/test_models.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add src/crypto_daily_agent/models.py tests/unit/test_models.py
git commit -m "feat: Add data models with fingerprint generation"
```

---

### Task 3: 实现 Pydantic 配置系统

**Files:**
- Create: `src/crypto_daily_agent/config.py`
- Create: `tests/unit/test_config.py`

**Context:** 替换原有的 dataclass 配置，使用 Pydantic Settings 实现类型安全和验证

- [ ] **Step 1: 编写配置测试**

Create: `tests/unit/test_config.py`

```python
"""Tests for config module."""

import pytest
from pathlib import Path
from pydantic import ValidationError
from crypto_daily_agent.config import Settings, ScoringWeights


def test_scoring_weights_defaults():
    """测试评分权重默认值."""
    weights = ScoringWeights()
    assert weights.binance == 1.2
    assert weights.bitcoin_keyword == 0.9


def test_settings_defaults(tmp_path: Path):
    """测试设置默认值."""
    settings = Settings(
        _env_file=None,  # 禁用 .env 加载
        output_dir=tmp_path / "output",
        state_dir=tmp_path / "state",
    )
    assert settings.tz == "Asia/Shanghai"
    assert settings.max_news_items == 10
    assert settings.storage_backend == "json"


def test_settings_validation():
    """测试配置验证."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            max_news_items=100,  # 超出范围
        )
    assert "max_news_items" in str(exc_info.value)


def test_settings_path_resolution(tmp_path: Path):
    """测试路径解析."""
    settings = Settings(
        _env_file=None,
        output_dir=tmp_path / "out",
        state_dir=tmp_path / "state",
    )
    assert settings.output_dir == tmp_path / "out"
    assert settings.state_dir == tmp_path / "state"
```

Run: `pytest tests/unit/test_config.py -v`
Expected: FAIL (config module not yet created)

- [ ] **Step 2: 实现配置系统**

Create: `src/crypto_daily_agent/config.py`

```python
"""配置管理 - Pydantic Settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScoringWeights(BaseModel):
    """新闻评分权重配置."""
    
    binance: float = 1.2
    bitcoin_keyword: float = 0.9
    ethereum_keyword: float = 0.7
    tier1_source: float = 0.5  # Binance, X
    tier2_source: float = 0.3  # CoinDesk, TheBlock


class Settings(BaseSettings):
    """应用配置."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 时区与定时
    tz: str = "Asia/Shanghai"
    daily_push_time: str = "08:00"
    
    # 邮件配置
    smtp_host: str = Field(default="", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=465, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    email_from: str = Field(default="", validation_alias="EMAIL_FROM")
    email_to: str = Field(default="", validation_alias="EMAIL_TO")
    enable_email: bool = Field(default=True, validation_alias="ENABLE_EMAIL")
    
    # API Keys
    newsapi_key: str = ""
    coinmarketcap_api_key: str = ""
    x_bearer_token: str = ""
    
    # 行为配置
    max_news_items: int = Field(default=10, ge=1, le=50)
    request_timeout_seconds: int = Field(default=12, ge=5, le=60)
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    storage_backend: Literal["json", "sqlite"] = "json"
    storage_cleanup_days: int = Field(default=7, ge=1, le=30)
    
    # 路径配置
    output_dir: Path = Path("output")
    state_dir: Path = Path("state")
    
    @field_validator("output_dir", "state_dir", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """确保路径是 Path 对象并创建目录."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/unit/test_config.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add src/crypto_daily_agent/config.py tests/unit/test_config.py
git commit -m "feat: Add Pydantic Settings with validation"
```

---

## Phase 2: 存储层实现 (Storage)

### Task 4: 实现存储抽象层

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/storage/base.py`
- Create: `src/crypto_daily_agent/infrastructure/storage/json_store.py`
- Create: `src/crypto_daily_agent/infrastructure/storage/__init__.py`
- Create: `tests/unit/test_storage.py`

**Context:** 解决状态文件无限增长问题，支持自动清理

- [ ] **Step 1: 编写存储测试**

Create: `tests/unit/test_storage.py`

```python
"""Tests for storage backends."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from crypto_daily_agent.infrastructure.storage.json_store import JsonStateStore


@pytest.fixture
def temp_json_store(tmp_path: Path):
    """临时 JSON 存储."""
    return JsonStateStore(tmp_path / "test_state.json", cleanup_days=7)


@pytest.mark.asyncio
async def test_is_pushed_new_item(temp_json_store: JsonStateStore):
    """测试新条目未被推送."""
    result = await temp_json_store.is_pushed("fp123")
    assert result is False


@pytest.mark.asyncio
async def test_mark_and_check_pushed(temp_json_store: JsonStateStore):
    """测试标记为已推送."""
    await temp_json_store.mark_pushed(["fp123", "fp456"])
    
    assert await temp_json_store.is_pushed("fp123") is True
    assert await temp_json_store.is_pushed("fp456") is True
    assert await temp_json_store.is_pushed("fp789") is False


@pytest.mark.asyncio
async def test_cleanup_old_entries(temp_json_store: JsonStateStore):
    """测试清理旧条目."""
    # 添加旧条目
    old_time = datetime.now(timezone.utc) - timedelta(days=10)
    temp_json_store._cache["old_fp"] = old_time
    
    # 添加新条目
    await temp_json_store.mark_pushed(["new_fp"])
    
    # 清理 7 天前的条目
    cleaned = await temp_json_store.cleanup_old(7)
    assert cleaned == 1
    assert await temp_json_store.is_pushed("old_fp") is False
    assert await temp_json_store.is_pushed("new_fp") is True


@pytest.mark.asyncio
async def test_get_stats(temp_json_store: JsonStateStore):
    """测试存储统计."""
    await temp_json_store.mark_pushed(["fp1", "fp2", "fp3"])
    stats = await temp_json_store.get_stats()
    assert stats["total_entries"] == 3
```

Run: `pytest tests/unit/test_storage.py -v`
Expected: FAIL (storage not yet created)

- [ ] **Step 2: 实现存储抽象**

Create: `src/crypto_daily_agent/infrastructure/storage/base.py`

```python
"""存储抽象层."""

from abc import ABC, abstractmethod


class StateStore(ABC):
    """状态存储抽象 - 支持多种后端."""
    
    @abstractmethod
    async def is_pushed(self, fingerprint: str) -> bool:
        """检查是否已推送."""
        raise NotImplementedError
    
    @abstractmethod
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        """标记为已推送."""
        raise NotImplementedError
    
    @abstractmethod
    async def cleanup_old(self, days: int = 7) -> int:
        """清理 N 天前的旧记录，返回清理数量."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_stats(self) -> dict[str, int]:
        """获取存储统计."""
        raise NotImplementedError
```

Create: `src/crypto_daily_agent/infrastructure/storage/json_store.py`

```python
"""JSON 文件存储实现."""

from __future__ import annotations

import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from crypto_daily_agent.infrastructure.storage.base import StateStore


class JsonStateStore(StateStore):
    """JSON 文件实现 - 带自动清理."""
    
    def __init__(self, file_path: Path, cleanup_days: int = 7, auto_cleanup_threshold: int = 1000):
        self.file_path = Path(file_path)
        self.cleanup_days = cleanup_days
        self.auto_cleanup_threshold = auto_cleanup_threshold
        self._cache: dict[str, str] = {}  # fingerprint -> isoformat timestamp
        self._lock = asyncio.Lock()
        self._load()
    
    def _load(self) -> None:
        """从文件加载状态."""
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
        """保存状态到文件."""
        async with self._lock:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"entries": self._cache}, f, ensure_ascii=False, indent=2)
    
    async def is_pushed(self, fingerprint: str) -> bool:
        """检查是否已推送."""
        return fingerprint in self._cache
    
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        """标记为已推送."""
        now = datetime.now(timezone.utc).isoformat()
        for fp in fingerprints:
            self._cache[fp] = now
        await self._save()
        
        # 自动触发清理（如果记录数超过阈值）
        if len(self._cache) > self.auto_cleanup_threshold:
            await self.cleanup_old(self.cleanup_days)
    
    async def cleanup_old(self, days: int) -> int:
        """清理 N 天前的旧记录."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        old_keys = [
            k for k, v in self._cache.items() 
            if v < cutoff_str
        ]
        
        for k in old_keys:
            del self._cache[k]
        
        if old_keys:
            await self._save()
        
        return len(old_keys)
    
    async def get_stats(self) -> dict[str, int]:
        """获取存储统计."""
        return {"total_entries": len(self._cache)}
```

Create: `src/crypto_daily_agent/infrastructure/storage/__init__.py`

```python
"""存储模块."""

from crypto_daily_agent.infrastructure.storage.base import StateStore
from crypto_daily_agent.infrastructure.storage.json_store import JsonStateStore

__all__ = ["StateStore", "JsonStateStore"]
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/unit/test_storage.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/storage/ tests/unit/test_storage.py
git commit -m "feat: Add state storage abstraction with JSON backend and auto-cleanup"
```

---

## Phase 3: Pipeline 层实现

### Task 5: 实现可配置评分系统

**Files:**
- Create: `src/crypto_daily_agent/pipeline/scorer.py`
- Create: `tests/unit/test_scorer.py`

**Context:** 替换硬编码评分逻辑，支持配置化权重

- [ ] **Step 1: 编写评分测试**

Create: `tests/unit/test_scorer.py`

```python
"""Tests for news scorer."""

import pytest
from datetime import datetime, timezone
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.config import ScoringWeights
from crypto_daily_agent.pipeline.scorer import NewsScorer


def test_scorer_binance_keyword():
    """测试 Binance 关键词加权."""
    scorer = NewsScorer(ScoringWeights(binance=1.5))
    item = NewsItem(
        source="Test",
        title="Binance Announces New Feature",
        url="https://test.com",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    score = scorer.score(item)
    assert score == 1.0 + 1.5  # base + binance weight


def test_scorer_bitcoin_keyword():
    """测试 Bitcoin 关键词加权."""
    scorer = NewsScorer(ScoringWeights(bitcoin_keyword=0.9))
    item = NewsItem(
        source="Test",
        title="Bitcoin Price Surges",
        url="https://test.com",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    score = scorer.score(item)
    assert score == 1.0 + 0.9


def test_scorer_source_weight():
    """测试来源加权."""
    scorer = NewsScorer(ScoringWeights(tier1_source=0.5))
    item = NewsItem(
        source="Binance",
        title="Regular Update",
        url="https://test.com",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    score = scorer.score(item)
    assert score == 1.0 + 0.5


def test_scorer_combined_weights():
    """测试多重权重组合."""
    scorer = NewsScorer(ScoringWeights(
        binance=1.2,
        bitcoin_keyword=0.9,
        tier1_source=0.5,
    ))
    item = NewsItem(
        source="Binance",
        title="Binance Lists New Bitcoin Trading Pair",
        url="https://test.com",
        published_at=datetime.now(timezone.utc),
        content="Content",
    )
    score = scorer.score(item)
    assert score == 1.0 + 1.2 + 0.9 + 0.5
```

Run: `pytest tests/unit/test_scorer.py -v`
Expected: FAIL (scorer not yet created)

- [ ] **Step 2: 实现评分系统**

Create: `src/crypto_daily_agent/pipeline/scorer.py`

```python
"""可配置的新闻重要性评分器."""

from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.config import ScoringWeights


class NewsScorer:
    """新闻重要性评分器."""
    
    def __init__(self, weights: ScoringWeights | None = None):
        self.weights = weights or ScoringWeights()
        self._keywords = self._build_keywords()
        self._source_weights = self._build_source_weights()
    
    def _build_keywords(self) -> dict[str, float]:
        """构建关键词权重映射."""
        return {
            "binance": self.weights.binance,
            "币安": self.weights.binance,
            "bitcoin": self.weights.bitcoin_keyword,
            "btc": self.weights.bitcoin_keyword,
            "ethereum": self.weights.ethereum_keyword,
            "eth": self.weights.ethereum_keyword,
        }
    
    def _build_source_weights(self) -> dict[str, float]:
        """构建来源权重映射."""
        return {
            "Binance": self.weights.tier1_source,
            "X": self.weights.tier1_source,
            "CoinDesk": self.weights.tier2_source,
            "TheBlock": self.weights.tier2_source,
        }
    
    def score(self, item: NewsItem) -> float:
        """计算新闻重要性得分."""
        score = 1.0  # 基础分
        title_lower = item.title.lower()
        
        # 关键词加权
        for keyword, weight in self._keywords.items():
            if keyword in title_lower:
                score += weight
        
        # 来源加权
        score += self._source_weights.get(item.source, 0.0)
        
        # 存储得分
        item.importance = round(score, 2)
        return item.importance
    
    def score_batch(self, items: list[NewsItem]) -> list[NewsItem]:
        """批量评分并排序."""
        for item in items:
            self.score(item)
        return sorted(items, key=lambda x: (x.importance, x.published_at), reverse=True)
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/unit/test_scorer.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add src/crypto_daily_agent/pipeline/scorer.py tests/unit/test_scorer.py
git commit -m "feat: Add configurable news scoring system"
```

---

## Phase 4: 采集器实现 (Collectors)

### Task 6: 实现插件化采集器基类和注册表

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/collectors/base.py`
- Create: `src/crypto_daily_agent/infrastructure/collectors/registry.py`
- Create: `src/crypto_daily_agent/infrastructure/collectors/__init__.py`
- Create: `src/crypto_daily_agent/utils/http_client.py`

**Context:** 建立插件化架构，支持自动发现和注册采集器

- [ ] **Step 1: 创建 HTTP 客户端工具**

Create: `src/crypto_daily_agent/utils/http_client.py`

```python
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
        """执行 GET 请求."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async with context.")
        
        async with self._session.get(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, url: str, **kwargs) -> dict[str, Any]:
        """执行 POST 请求."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async with context.")
        
        async with self._session.post(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
```

- [ ] **Step 2: 实现采集器基类**

Create: `src/crypto_daily_agent/infrastructure/collectors/base.py`

```python
"""采集器抽象基类."""

from abc import ABC, abstractmethod
from typing import ClassVar

from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.utils.http_client import HttpClient


class SourceCollector(ABC):
    """数据源采集器抽象基类."""
    
    name: ClassVar[str] = ""
    priority: ClassVar[int] = 100  # 优先级，越小越优先
    
    @abstractmethod
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取新闻条目."""
        raise NotImplementedError
    
    @property
    def is_available(self) -> bool:
        """检查采集器是否可用（配置是否完整）."""
        return True
```

- [ ] **Step 3: 实现注册表**

Create: `src/crypto_daily_agent/infrastructure/collectors/registry.py`

```python
"""采集器注册表 - 自动发现和管理采集器."""

import logging
from typing import Type

from crypto_daily_agent.config import Settings
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.utils.http_client import HttpClient

LOGGER = logging.getLogger(__name__)


class CollectorRegistry:
    """采集器注册表."""
    
    def __init__(self):
        self._collectors: dict[str, Type[SourceCollector]] = {}
    
    def register(self, collector_class: Type[SourceCollector]) -> Type[SourceCollector]:
        """装饰器：注册采集器."""
        if not collector_class.name:
            raise ValueError(f"Collector {collector_class.__name__} must define 'name'")
        
        self._collectors[collector_class.name] = collector_class
        LOGGER.debug(f"Registered collector: {collector_class.name}")
        return collector_class
    
    def get_available_collectors(self, settings: Settings) -> list[SourceCollector]:
        """获取所有可用的采集器实例（按优先级排序）."""
        instances = []
        
        sorted_collectors = sorted(
            self._collectors.items(),
            key=lambda x: x[1].priority
        )
        
        for name, cls in sorted_collectors:
            try:
                instance = cls(settings)
                if instance.is_available:
                    instances.append(instance)
                    LOGGER.debug(f"Collector available: {name}")
                else:
                    LOGGER.debug(f"Collector unavailable: {name}")
            except Exception as exc:
                LOGGER.warning(f"Failed to initialize collector {name}: {exc}")
        
        return instances
    
    async def collect_all(
        self, 
        settings: Settings, 
        http_client: HttpClient
    ) -> list[NewsItem]:
        """并行采集所有可用来源."""
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
        
        # 并行执行所有采集器
        results = await asyncio.gather(*[
            fetch_with_error_handling(c) for c in collectors
        ])
        
        for items in results:
            all_items.extend(items)
        
        return all_items


# 全局注册表实例
registry = CollectorRegistry()
register_collector = registry.register
```

Create: `src/crypto_daily_agent/infrastructure/collectors/__init__.py`

```python
"""采集器模块."""

from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import (
    CollectorRegistry,
    register_collector,
    registry,
)

__all__ = [
    "SourceCollector",
    "CollectorRegistry",
    "register_collector",
    "registry",
]
```

- [ ] **Step 4: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/collectors/ src/crypto_daily_agent/utils/http_client.py
git commit -m "feat: Add plugin-based collector architecture with registry"
```

---

### Task 7: 实现 Binance 采集器

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/collectors/binance.py`
- Create: `tests/unit/collectors/test_binance.py`

**Context:** 重构原有的 Binance 采集器，使用新的异步架构

- [ ] **Step 1: 编写测试**

Create: `tests/unit/collectors/test_binance.py`

```python
"""Tests for Binance collector."""

import pytest
from datetime import datetime, timezone
from crypto_daily_agent.config import Settings
from crypto_daily_agent.infrastructure.collectors.binance import BinanceCollector


def test_binance_collector_availability():
    """测试 Binance 采集器始终可用."""
    settings = Settings(_env_file=None)
    collector = BinanceCollector(settings)
    assert collector.is_available is True
    assert collector.name == "binance"
    assert collector.priority == 10


@pytest.mark.asyncio
async def test_binance_fetch_mocked(aioresponse, test_settings):
    """测试 Binance 采集（模拟响应）."""
    from crypto_daily_agent.utils.http_client import HttpClient
    
    collector = BinanceCollector(test_settings)
    
    # 模拟 API 响应
    mock_data = {
        "data": {
            "articles": [
                {
                    "code": "test-123",
                    "title": "Binance Test Article",
                    "releaseDate": 1700000000000,
                    "summary": "Test summary",
                }
            ]
        }
    }
    aioresponse.post(
        "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
        payload=mock_data,
    )
    
    async with HttpClient() as client:
        items = await collector.fetch(client)
    
    assert len(items) == 1
    assert items[0].source == "Binance"
    assert items[0].title == "Binance Test Article"
```

- [ ] **Step 2: 实现 Binance 采集器**

Create: `src/crypto_daily_agent/infrastructure/collectors/binance.py`

```python
"""Binance 公告采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class BinanceCollector(SourceCollector):
    """Binance 公告采集器."""
    
    name: ClassVar[str] = "binance"
    priority: ClassVar[int] = 10
    
    def __init__(self, settings: Settings):
        self.timeout = settings.request_timeout_seconds
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 Binance 公告."""
        url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
        payload = {
            "type": 1,
            "catalogId": "48",
            "pageNo": 1,
            "pageSize": 20,
        }
        headers = {"User-Agent": "crypto-daily-agent/2.0"}
        
        try:
            data = await http_client.post(url, json=payload, headers=headers)
        except Exception:
            # Fallback to RSS on API failure
            return await self._fetch_rss(http_client)
        
        records = data.get("data", {}).get("articles", [])
        items = []
        
        for row in records:
            code = row.get("code", "")
            items.append(NewsItem(
                source="Binance",
                title=row.get("title", "").strip(),
                url=f"https://www.binance.com/zh-CN/support/announcement/{code}",
                published_at=datetime.fromtimestamp(
                    int(row.get("releaseDate", 0)) / 1000, 
                    tz=timezone.utc
                ),
                content=row.get("summary", "") or row.get("body", ""),
                language="zh",
            ))
        
        return items or await self._fetch_rss(http_client)
    
    async def _fetch_rss(self, http_client: HttpClient) -> list[NewsItem]:
        """RSS 备用方案."""
        import feedparser
        
        feed = feedparser.parse("https://www.binance.com/en/support/announcement/rss")
        items = []
        
        for entry in feed.entries[:20]:
            published = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            items.append(NewsItem(
                source="Binance",
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                published_at=published,
                content=entry.get("summary", "")[:500],
                language="en",
            ))
        
        return items
```

- [ ] **Step 3: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/collectors/binance.py tests/unit/collectors/test_binance.py
git commit -m "feat: Add Binance collector with RSS fallback"
```

---

### Task 8: 实现 CoinMarketCap 采集器（新增功能）

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/collectors/coinmarketcap.py`

**Context:** 新增价格数据采集功能

- [ ] **Step 1: 实现 CMC 采集器**

Create: `src/crypto_daily_agent/infrastructure/collectors/coinmarketcap.py`

```python
"""CoinMarketCap 价格数据采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem, MarketData
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class CoinMarketCapCollector(SourceCollector):
    """
    CoinMarketCap 价格数据采集器.
    提供 BTC/ETH 24h 价格变化作为市场温度参考.
    """
    
    name: ClassVar[str] = "coinmarketcap"
    priority: ClassVar[int] = 5  # 最高优先级
    
    def __init__(self, settings: Settings):
        self.api_key = settings.coinmarketcap_api_key
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        """需要 API key 才可用."""
        return bool(self.api_key)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 BTC/ETH 价格数据."""
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }
        params = {"symbol": "BTC,ETH", "convert": "USD"}
        
        data = await http_client.get(url, headers=headers, params=params)
        
        items = []
        for symbol in ["BTC", "ETH"]:
            crypto_data = data["data"][symbol]
            quote = crypto_data["quote"]["USD"]
            change_24h = quote["percent_change_24h"]
            
            # 创建为 NewsItem（用于渲染）
            items.append(NewsItem(
                source="CoinMarketCap",
                title=f"{symbol} 24h: {change_24h:+.2f}%",
                url=f"https://coinmarketcap.com/currencies/{crypto_data['slug']}/",
                published_at=datetime.now(timezone.utc),
                content=(
                    f"Price: ${quote['price']:.2f}\n"
                    f"24h Change: {change_24h:.2f}%\n"
                    f"Market Cap: ${quote['market_cap']:,.0f}"
                ),
                language="en",
                importance=2.0 if abs(change_24h) > 5 else 1.5,
            ))
        
        return items
    
    async def fetch_market_data(self, http_client: HttpClient) -> list[MarketData]:
        """获取原始市场数据（用于市场温度计算）."""
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }
        params = {"symbol": "BTC,ETH", "convert": "USD"}
        
        data = await http_client.get(url, headers=headers, params=params)
        
        market_data = []
        for symbol in ["BTC", "ETH"]:
            crypto_data = data["data"][symbol]
            quote = crypto_data["quote"]["USD"]
            
            market_data.append(MarketData(
                symbol=symbol,
                price_usd=quote["price"],
                change_24h_percent=quote["percent_change_24h"],
                source="CoinMarketCap",
            ))
        
        return market_data
```

- [ ] **Step 2: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/collectors/coinmarketcap.py
git commit -m "feat: Add CoinMarketCap price data collector"
```

---

## Phase 5: 应用服务层

### Task 9: 实现主服务 (DigestService)

**Files:**
- Create: `src/crypto_daily_agent/application/digest_service.py`
- Create: `src/crypto_daily_agent/application/__init__.py`

**Context:** 整合所有组件，实现核心业务逻辑

- [ ] **Step 1: 实现主服务**

Create: `src/crypto_daily_agent/application/digest_service.py`

```python
"""主服务 - 每日资讯汇总."""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import DigestContext, NewsItem
from crypto_daily_agent.infrastructure.collectors.registry import registry
from crypto_daily_agent.infrastructure.storage.base import StateStore
from crypto_daily_agent.infrastructure.storage.json_store import JsonStateStore
from crypto_daily_agent.pipeline.scorer import NewsScorer
from crypto_daily_agent.utils.http_client import HttpClient

LOGGER = logging.getLogger(__name__)


class DigestService:
    """每日资讯汇总服务."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.scorer = NewsScorer(settings.scoring_weights)
        self.store = self._create_store()
    
    def _create_store(self) -> StateStore:
        """创建存储实例."""
        if self.settings.storage_backend == "json":
            return JsonStateStore(
                self.settings.state_dir / "cache.json",
                cleanup_days=self.settings.storage_cleanup_days,
            )
        else:
            # SQLite 实现（后续添加）
            raise NotImplementedError("SQLite backend not yet implemented")
    
    async def run(self) -> DigestContext:
        """执行一次资讯汇总."""
        LOGGER.info("digest_run_started")
        
        # 1. 采集数据
        async with HttpClient(self.settings.request_timeout_seconds) as http_client:
            all_items = await registry.collect_all(self.settings, http_client)
        
        LOGGER.info(f"collected_total={len(all_items)}")
        
        # 2. 过滤和去重
        recent_items = self._filter_recent(all_items)
        unique_items = await self._deduplicate(recent_items)
        
        LOGGER.info(f"after_dedup={len(unique_items)}")
        
        # 3. 评分和排序
        scored_items = self.scorer.score_batch(unique_items)
        
        # 4. 选择前 N 条
        selected = scored_items[: self.settings.max_news_items]
        
        # 5. 标记为已推送
        await self.store.mark_pushed([item.fingerprint for item in selected])
        
        # 6. 构建上下文
        context = self._build_context(selected)
        
        LOGGER.info(f"digest_complete items={len(selected)}")
        return context
    
    def _filter_recent(self, items: list[NewsItem]) -> list[NewsItem]:
        """过滤最近 24 小时的新闻."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        return [item for item in items if item.published_at >= cutoff]
    
    async def _deduplicate(self, items: list[NewsItem]) -> list[NewsItem]:
        """去重 - 移除已推送的条目."""
        result = []
        for item in items:
            if not await self.store.is_pushed(item.fingerprint):
                result.append(item)
        return result
    
    def _build_context(self, items: list[NewsItem]) -> DigestContext:
        """构建渲染上下文."""
        now = datetime.now()
        
        if not items:
            return DigestContext(
                date_str=now.strftime("%Y-%m-%d"),
                market_temperature="中性",
                headline="今日暂无高置信度新资讯",
                cards=[],
            )
        
        # 计算市场温度
        avg_importance = sum(item.importance for item in items) / len(items)
        if avg_importance >= 2.3:
            temperature = "偏热"
        elif avg_importance >= 1.8:
            temperature = "中性偏热"
        else:
            temperature = "中性"
        
        # 构建卡片
        cards = []
        for idx, item in enumerate(items, start=1):
            cards.append({
                "rank": idx,
                "title": item.title[:70],
                "summary": self._make_summary(item),
                "source": item.source,
                "time": item.published_at.strftime("%H:%M UTC"),
                "url": item.url,
            })
        
        return DigestContext(
            date_str=now.strftime("%Y-%m-%d"),
            market_temperature=temperature,
            headline=items[0].title[:88],
            cards=cards,
        )
    
    def _make_summary(self, item: NewsItem) -> str:
        """生成摘要."""
        if item.language == "zh":
            text = item.content or item.title
            return text[:90]
        return (item.content or item.title).replace("\n", " ")[:90]
```

Create: `src/crypto_daily_agent/application/__init__.py`

```python
"""应用服务层."""

from crypto_daily_agent.application.digest_service import DigestService

__all__ = ["DigestService"]
```

- [ ] **Step 2: 提交**

```bash
git add src/crypto_daily_agent/application/
git commit -m "feat: Add DigestService with full pipeline integration"
```

---

### Task 10: 实现 CLI 入口

**Files:**
- Create: `src/crypto_daily_agent/cli.py`
- Modify: `deploy/crypto-daily.timer`

**Context:** 创建新的命令行接口，修复 systemd timer 时区

- [ ] **Step 1: 实现 CLI**

Create: `src/crypto_daily_agent/cli.py`

```python
"""命令行接口."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from crypto_daily_agent.config import Settings
from crypto_daily_agent.application.digest_service import DigestService
from crypto_daily_agent.infrastructure.render.renderer import ImageRenderer
from crypto_daily_agent.infrastructure.sender import EmailSender


def setup_logging(output_dir: Path) -> None:
    """配置日志."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "agent.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


async def cmd_once(settings: Settings) -> None:
    """执行一次资讯汇总."""
    setup_logging(settings.output_dir)
    
    service = DigestService(settings)
    context = await service.run()
    
    # 渲染图片
    renderer = ImageRenderer(settings.output_dir)
    image_path = renderer.render(context)
    
    print(f"Digest generated: {image_path}")
    
    # 发送邮件（如果启用）
    if settings.enable_email:
        sender = EmailSender(settings)
        await sender.send_digest(image_path, context)


def cmd_config_test(settings: Settings) -> None:
    """测试配置."""
    print("Configuration Test")
    print("=" * 40)
    print(f"TZ: {settings.tz}")
    print(f"Daily Push Time: {settings.daily_push_time}")
    print(f"Max News Items: {settings.max_news_items}")
    print(f"Storage Backend: {settings.storage_backend}")
    print(f"Email Enabled: {settings.enable_email}")
    print(f"Output Dir: {settings.output_dir}")
    print(f"State Dir: {settings.state_dir}")
    print("=" * 40)
    print("✓ Configuration loaded successfully")


def main() -> None:
    """主入口."""
    parser = argparse.ArgumentParser(
        prog="crypto_daily_agent",
        description="每日加密资讯图片推送 Agent",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # once 命令
    once_parser = subparsers.add_parser("once", help="执行一次资讯汇总")
    
    # loop 命令（调度器）
    loop_parser = subparsers.add_parser("loop", help="启动定时调度")
    
    # config-test 命令
    subparsers.add_parser("config-test", help="测试配置")
    
    args = parser.parse_args()
    
    # 加载配置
    settings = Settings()
    
    if args.command == "once":
        asyncio.run(cmd_once(settings))
    elif args.command == "loop":
        # TODO: 实现调度器
        print("Scheduler not yet implemented in v2.0")
        sys.exit(1)
    elif args.command == "config-test":
        cmd_config_test(settings)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 修复 systemd timer 时区**

Modify: `deploy/crypto-daily.timer`

```ini
[Unit]
Description=Run Crypto Daily Digest at 08:00 BJT

[Timer]
# 修复前: OnCalendar=*-*-* 00:00:00 UTC (错误)
# 修复后: 使用本地时间 08:00
OnCalendar=*-*-* 08:00:00
Persistent=true
Unit=crypto-daily.service

[Install]
WantedBy=timers.target
```

- [ ] **Step 3: 提交**

```bash
git add src/crypto_daily_agent/cli.py deploy/crypto-daily.timer
git commit -m "feat: Add CLI interface and fix systemd timer timezone"
```

---

## Phase 6: 遗留代码迁移

### Task 11: 迁移旧采集器

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/collectors/coindesk.py`
- Create: `src/crypto_daily_agent/infrastructure/collectors/theblock.py`
- Create: `src/crypto_daily_agent/infrastructure/collectors/newsapi.py`
- Create: `src/crypto_daily_agent/infrastructure/collectors/x_list.py`

**Context:** 将旧采集器迁移到新的插件化架构

- [ ] **Step 1: 迁移 CoinDesk 采集器**

Create: `src/crypto_daily_agent/infrastructure/collectors/coindesk.py`

```python
"""CoinDesk RSS 采集器."""

from datetime import datetime, timezone
from typing import ClassVar

import feedparser

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class CoinDeskCollector(SourceCollector):
    """CoinDesk RSS 采集器."""
    
    name: ClassVar[str] = "coindesk"
    priority: ClassVar[int] = 30
    
    RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 CoinDesk 新闻."""
        feed = feedparser.parse(self.RSS_URL)
        items = []
        
        for entry in feed.entries[:20]:
            published = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            items.append(NewsItem(
                source="CoinDesk",
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                published_at=published,
                content=entry.get("summary", "")[:500],
                language="en",
            ))
        
        return items
```

- [ ] **Step 2: 迁移 TheBlock 采集器（原 Onchain RSS）**

Create: `src/crypto_daily_agent/infrastructure/collectors/theblock.py`

```python
"""TheBlock RSS 采集器（原 Onchain RSS）."""

from datetime import datetime, timezone
from typing import ClassVar

import feedparser

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class TheBlockCollector(SourceCollector):
    """TheBlock RSS 采集器 - 机构级链上分析."""
    
    name: ClassVar[str] = "theblock"
    priority: ClassVar[int] = 40
    
    RSS_URL = "https://www.theblock.co/rss.xml"
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 TheBlock 新闻."""
        feed = feedparser.parse(self.RSS_URL)
        items = []
        
        for entry in feed.entries[:20]:
            published = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            items.append(NewsItem(
                source="TheBlock",
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                published_at=published,
                content=entry.get("summary", "")[:500],
                language="en",
            ))
        
        return items
```

- [ ] **Step 3: 迁移 NewsAPI 采集器**

Create: `src/crypto_daily_agent/infrastructure/collectors/newsapi.py`

```python
"""NewsAPI 采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class NewsAPICollector(SourceCollector):
    """NewsAPI 采集器."""
    
    name: ClassVar[str] = "newsapi"
    priority: ClassVar[int] = 50
    
    def __init__(self, settings: Settings):
        self.api_key = settings.newsapi_key
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        """需要 API key 才可用."""
        return bool(self.api_key)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 NewsAPI 新闻."""
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "crypto OR bitcoin OR ethereum",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 25,
            "apiKey": self.api_key,
        }
        headers = {"User-Agent": "crypto-daily-agent/2.0"}
        
        try:
            data = await http_client.get(url, params=params, headers=headers)
        except Exception:
            return []
        
        items = []
        for article in data.get("articles", []):
            published_str = article.get("publishedAt", "")
            try:
                published = datetime.fromisoformat(
                    published_str.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            except ValueError:
                published = datetime.now(timezone.utc)
            
            source_name = article.get("source", {}).get("name", "NewsAPI")
            
            items.append(NewsItem(
                source=source_name,
                title=article.get("title", "").strip(),
                url=article.get("url", ""),
                published_at=published,
                content=article.get("description", "") or article.get("content", ""),
                language="en",
            ))
        
        return items
```

- [ ] **Step 4: 迁移 X (Twitter) 采集器**

Create: `src/crypto_daily_agent/infrastructure/collectors/x_list.py`

```python
"""X (Twitter) 列表采集器."""

from datetime import datetime, timezone
from typing import ClassVar

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import NewsItem
from crypto_daily_agent.infrastructure.collectors.base import SourceCollector
from crypto_daily_agent.infrastructure.collectors.registry import register_collector
from crypto_daily_agent.utils.http_client import HttpClient


@register_collector
class XListCollector(SourceCollector):
    """X (Twitter) 账号列表采集器."""
    
    name: ClassVar[str] = "x_list"
    priority: ClassVar[int] = 20
    
    # 预定义账号 ID 列表
    ACCOUNT_IDS = [
        "44196397",  # elonmusk (示例)
        "783214",    # X official (示例)
    ]
    
    def __init__(self, settings: Settings):
        self.bearer_token = settings.x_bearer_token
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        """需要 Bearer token 才可用."""
        return bool(self.bearer_token)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 X 推文."""
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        items = []
        
        for user_id in self.ACCOUNT_IDS:
            try:
                url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {
                    "max_results": 5,
                    "tweet.fields": "created_at",
                }
                
                data = await http_client.get(url, params=params, headers=headers)
                tweets = data.get("data", [])
                
                for tweet in tweets:
                    created = tweet.get("created_at", "")
                    try:
                        published = datetime.fromisoformat(
                            created.replace("Z", "+00:00")
                        )
                    except ValueError:
                        published = datetime.now(timezone.utc)
                    
                    tweet_id = tweet.get("id", "")
                    text = tweet.get("text", "")
                    
                    items.append(NewsItem(
                        source="X",
                        title=text.split("\n")[0][:120],
                        url=f"https://x.com/i/web/status/{tweet_id}",
                        published_at=published,
                        content=text,
                        language="en",
                    ))
            except Exception:
                continue
        
        return items
```

- [ ] **Step 5: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/collectors/coindesk.py
 git add src/crypto_daily_agent/infrastructure/collectors/theblock.py
 git add src/crypto_daily_agent/infrastructure/collectors/newsapi.py
 git add src/crypto_daily_agent/infrastructure/collectors/x_list.py
 git commit -m "feat: Migrate all collectors to new plugin architecture"
```

---

## Phase 7: 渲染和发送层

### Task 12: 实现图片渲染器

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/render/renderer.py`

**Context:** 迁移并改进原有的图片渲染功能

- [ ] **Step 1: 实现渲染器**

Create: `src/crypto_daily_agent/infrastructure/render/renderer.py`

```python
"""图片渲染器."""

from pathlib import Path
from datetime import datetime
from jinja2 import Template

from crypto_daily_agent.models import DigestContext


class ImageRenderer:
    """HTML 转 PNG 渲染器."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, context: DigestContext) -> Path:
        """渲染摘要为 PNG 图片."""
        template_path = Path(__file__).parent / "template.html"
        html = Template(template_path.read_text(encoding="utf-8")).render(
            date_str=context.date_str,
            market_temperature=context.market_temperature,
            headline=context.headline,
            cards=context.cards,
        )
        
        ts = datetime.now().strftime("%Y%m%d")
        output_path = self.output_dir / f"crypto_digest_{ts}.png"
        temp_html = output_path.with_suffix(".html")
        temp_html.write_text(html, encoding="utf-8")
        
        try:
            self._render_with_playwright(temp_html, output_path)
        except Exception:
            self._render_with_pil(context, output_path)
        
        return output_path
    
    def _render_with_playwright(self, html_path: Path, output_path: Path) -> None:
        """使用 Playwright 渲染."""
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1520})
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
    
    def _render_with_pil(self, context: DigestContext, output_path: Path) -> None:
        """使用 PIL 降级渲染."""
        from PIL import Image, ImageDraw
        
        img = Image.new("RGB", (1080, 1520), color=(28, 34, 40))
        draw = ImageDraw.Draw(img)
        
        # 绘制标题
        draw.text((48, 56), str(context.date_str), fill=(190, 198, 207))
        draw.text((48, 100), str(context.headline)[:80], fill=(214, 221, 227))
        
        # 绘制卡片
        y = 170
        for card in context.cards[:8]:
            draw.text((48, y), f"#{card['rank']} {card['title'][:60]}", 
                     fill=(159, 178, 196))
            y += 48
        
        img.save(output_path, format="PNG")
```

- [ ] **Step 2: 复制模板文件**

将原有的 `agent/render/template.html` 复制到新的位置:

Create: `src/crypto_daily_agent/infrastructure/render/template.html`

（复制原有内容，略）

- [ ] **Step 3: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/render/
git commit -m "feat: Add image renderer with Playwright and PIL fallback"
```

---

### Task 13: 实现邮件发送器

**Files:**
- Create: `src/crypto_daily_agent/infrastructure/sender.py`

**Context:** 迁移并改进邮件发送功能

- [ ] **Step 1: 实现发送器**

Create: `src/crypto_daily_agent/infrastructure/sender.py`

```python
"""邮件发送器."""

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from crypto_daily_agent.config import Settings
from crypto_daily_agent.models import DigestContext

LOGGER = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send_digest(self, image_path: Path, context: DigestContext) -> None:
        """发送每日摘要邮件."""
        if not self._is_configured():
            raise ValueError("SMTP settings are incomplete")
        
        subject = f"[Crypto Daily] {context.date_str} 市场资讯"
        body = self._build_body(context)
        
        try:
            await self._send_email(subject, body, image_path)
            LOGGER.info(f"email_sent file={image_path}")
        except Exception as exc:
            LOGGER.exception(f"email_send_failed error={exc}")
            # 尝试发送告警邮件
            await self._send_alert(f"推送失败: {exc}")
            raise
    
    def _is_configured(self) -> bool:
        """检查邮件配置是否完整."""
        return all([
            self.settings.smtp_host,
            self.settings.smtp_user,
            self.settings.smtp_password,
            self.settings.email_from,
            self.settings.email_to,
        ])
    
    def _build_body(self, context: DigestContext) -> str:
        """构建邮件正文."""
        lines = [
            f"今日为你筛选 {len(context.cards)} 条加密资讯。",
            f"市场温度：{context.market_temperature}",
            "详见附件图片。",
        ]
        return "\n".join(lines)
    
    async def _send_email(self, subject: str, body: str, attachment: Path) -> None:
        """发送邮件."""
        msg = MIMEMultipart()
        msg["From"] = self.settings.email_from
        msg["To"] = self.settings.email_to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # 添加附件
        with open(attachment, "rb") as f:
            attachment_data = MIMEApplication(f.read(), _subtype="png")
        attachment_data.add_header(
            "Content-Disposition", 
            "attachment", 
            filename=attachment.name
        )
        msg.attach(attachment_data)
        
        # 发送
        with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.sendmail(
                self.settings.email_from,
                [self.settings.email_to],
                msg.as_string(),
            )
    
    async def _send_alert(self, message: str) -> None:
        """发送告警邮件."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.settings.email_from
            msg["To"] = self.settings.email_to
            msg["Subject"] = "[Crypto Daily][ALERT] 推送失败"
            msg.attach(MIMEText(
                f"{message}\n请检查日志与配置。",
                "plain",
                "utf-8",
            ))
            
            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.sendmail(
                    self.settings.email_from,
                    [self.settings.email_to],
                    msg.as_string(),
                )
        except Exception as exc:
            LOGGER.error(f"alert_email_failed error={exc}")
```

- [ ] **Step 2: 提交**

```bash
git add src/crypto_daily_agent/infrastructure/sender.py
git commit -m "feat: Add email sender with alert fallback"
```

---

## Phase 8: 最终集成

### Task 14: 更新 README 和文档

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README**

更新 `README.md` 以反映新的安装和使用方式（内容根据实际 README 结构编写）。

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: Update README for v2.0"
```

---

### Task 15: 完整测试运行

**Files:**
- Run: 所有测试

- [ ] **Step 1: 运行完整测试套件**

```bash
pytest tests/ -v --cov=crypto_daily_agent --cov-report=term-missing
```

Expected: All tests pass

- [ ] **Step 2: 运行配置测试**

```bash
python -m crypto_daily_agent config-test
```

Expected: Configuration loaded successfully

- [ ] **Step 3: 最终提交**

```bash
git add .
git commit -m "chore: Complete v2.0 refactoring"
```

---

## 实现计划完成

**总计**: 15 个 Tasks，约 60-80 个具体 Steps  
**预估时间**: 3-4 天（按 subagent-driven-development 执行）  
**保存位置**: `docs/superpowers/plans/2026-03-24-crypto-daily-refactor-implementation.md`

---

**下一步**: 使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans` 执行此计划。

建议执行方式：**Subagent-Driven**（推荐）
- 每个 Task 由独立 subagent 执行
- 每 Task 完成后进行两阶段审查
- 更快迭代，更高质量
