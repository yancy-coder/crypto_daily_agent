# Crypto Daily Agent 重构设计文档

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 crypto_daily_agent 重构为现代化、可测试、可扩展的每日加密资讯推送系统

**Architecture:** 分层架构（Application → Pipeline → Infrastructure），插件化采集器，依赖注入，Pydantic 配置验证

**Tech Stack:** Python 3.11+, Pydantic Settings, pytest, pytest-asyncio, aiosqlite (可选)

---

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      Entry Points                            │
│  (CLI: --once, --loop, --config-test, --health-check)       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Digest    │  │  Scheduler  │  │   Health Monitor    │  │
│  │   Service   │  │   Service   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Collect  │→ │ Normalize│→ │ Summarize│→ │  Render  │    │
│  │ (Plugin) │  │ (Filter) │  │ (Score)  │  │ (Image)  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Collector │  │  Store   │  │ Renderer │  │  Sender  │    │
│  │ Registry │  │(JSON/SQL)│  │(Playwright)│ │ (Email)  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 文件结构重构

```
crypto_daily_agent/
├── pyproject.toml              # 新增: 现代 Python 项目配置
├── pytest.ini                 # 新增: 测试配置
├── .env.example               # 已存在: 更新示例
├── README.md                  # 已存在: 更新文档
├── src/
│   └── crypto_daily_agent/    # 新增: 源码目录 (PEP 420)
│       ├── __init__.py
│       ├── __main__.py        # 新增: python -m 入口
│       ├── cli.py             # 新增: 命令行接口
│       ├── config.py          # 重构: Pydantic Settings
│       ├── container.py       # 新增: 依赖注入容器
│       ├── models.py          # 重构: 完整数据模型
│       ├── exceptions.py      # 新增: 自定义异常
│       ├── application/
│       │   ├── __init__.py
│       │   ├── digest_service.py      # 新增: 主服务
│       │   ├── scheduler_service.py   # 新增: 调度服务
│       │   └── health_service.py      # 新增: 健康检查
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── collector.py           # 重构: 采集协调器
│       │   ├── normalizer.py          # 重构: 数据规范化
│       │   ├── summarizer.py          # 重构: 摘要生成
│       │   └── scorer.py              # 新增: 可配置评分
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── collectors/
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # 重构: 抽象基类
│       │   │   ├── registry.py        # 新增: 注册表
│       │   │   ├── binance.py         # 重构
│       │   │   ├── coindesk.py        # 重构
│       │   │   ├── newsapi.py         # 重构
│       │   │   ├── theblock.py        # 重构 (原 onchain)
│       │   │   ├── x_list.py          # 重构
│       │   │   └── coinmarketcap.py   # 新增
│       │   ├── storage/
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # 新增: 存储抽象
│       │   │   ├── json_store.py      # 新增: JSON 实现
│       │   │   └── sqlite_store.py    # 新增: SQLite 实现
│       │   ├── renderer.py            # 重构: 图片渲染
│       │   └── sender.py              # 重构: 邮件发送
│       └── utils/
│           ├── __init__.py
│           ├── logging_config.py      # 新增: 结构化日志
│           └── http_client.py         # 新增: 共享 HTTP 客户端
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # 新增: pytest fixtures
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_models.py
│   │   ├── test_scorer.py
│   │   ├── test_normalizer.py
│   │   └── test_storage.py
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   └── test_collectors.py
│   └── fixtures/
│       └── sample_news.json
├── deploy/
│   ├── crypto-daily.service   # 已存在: 修复时区
│   └── crypto-daily.timer     # 已存在: 修复时区
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-03-24-crypto-daily-refactor-design.md
```

---

## 3. 核心组件详细设计

### 3.1 配置系统 (Pydantic Settings)

```python
# src/crypto_daily_agent/config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class ScoringWeights(BaseModel):
    binance: float = 1.2
    bitcoin_keyword: float = 0.9
    ethereum_keyword: float = 0.7
    tier1_source: float = 0.5  # Binance, X
    tier2_source: float = 0.3  # CoinDesk, TheBlock

class Settings(BaseSettings):
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
    scoring_weights: ScoringWeights = ScoringWeights()
    storage_backend: Literal["json", "sqlite"] = "json"
    storage_cleanup_days: int = Field(default=7, ge=1, le=30)
    
    # 路径配置
    output_dir: Path = Path("output")
    state_dir: Path = Path("state")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
```

### 3.2 插件化采集器系统

```python
# src/crypto_daily_agent/infrastructure/collectors/base.py
from abc import ABC, abstractmethod
from typing import ClassVar

class SourceCollector(ABC):
    """数据源采集器抽象基类"""
    name: ClassVar[str]
    priority: ClassVar[int] = 100  # 优先级，越小越优先
    
    @abstractmethod
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取新闻条目"""
        raise NotImplementedError
    
    @property
    def is_available(self) -> bool:
        """检查采集器是否可用（配置是否完整）"""
        return True

# src/crypto_daily_agent/infrastructure/collectors/registry.py
class CollectorRegistry:
    """采集器注册表 - 自动发现和管理采集器"""
    
    def __init__(self):
        self._collectors: dict[str, type[SourceCollector]] = {}
    
    def register(self, collector_class: type[SourceCollector]) -> type[SourceCollector]:
        """装饰器：注册采集器"""
        self._collectors[collector_class.name] = collector_class
        return collector_class
    
    def get_available_collectors(self, settings: Settings) -> list[SourceCollector]:
        """获取所有可用的采集器实例"""
        instances = []
        for name, cls in sorted(self._collectors.items(), 
                               key=lambda x: x[1].priority):
            try:
                instance = cls(settings)
                if instance.is_available:
                    instances.append(instance)
            except Exception:
                logger.warning(f"Failed to initialize collector: {name}")
        return instances

# 全局注册表实例
registry = CollectorRegistry()
register_collector = registry.register

# 使用示例
@register_collector
class BinanceCollector(SourceCollector):
    name = "binance"
    priority = 10
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        ...
```

### 3.3 存储抽象层 (解决状态文件无限增长)

```python
# src/crypto_daily_agent/infrastructure/storage/base.py
class StateStore(ABC):
    """状态存储抽象 - 支持多种后端"""
    
    @abstractmethod
    async def is_pushed(self, fingerprint: str) -> bool:
        """检查是否已推送"""
        raise NotImplementedError
    
    @abstractmethod
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        """标记为已推送"""
        raise NotImplementedError
    
    @abstractmethod
    async def cleanup_old(self, days: int = 7) -> int:
        """清理 N 天前的旧记录，返回清理数量"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_stats(self) -> dict[str, int]:
        """获取存储统计"""
        raise NotImplementedError

# src/crypto_daily_agent/infrastructure/storage/json_store.py
class JsonStateStore(StateStore):
    """JSON 文件实现 - 带自动清理"""
    
    def __init__(self, file_path: Path, cleanup_days: int = 7):
        self.file_path = file_path
        self.cleanup_days = cleanup_days
        self._cache: dict[str, datetime] = {}
        self._load()
    
    async def mark_pushed(self, fingerprints: list[str]) -> None:
        now = datetime.now(timezone.utc)
        for fp in fingerprints:
            self._cache[fp] = now
        await self._save()
        
        # 自动触发清理（如果记录数超过阈值）
        if len(self._cache) > 1000:
            await self.cleanup_old(self.cleanup_days)
    
    async def cleanup_old(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        old_keys = [k for k, v in self._cache.items() if v < cutoff]
        for k in old_keys:
            del self._cache[k]
        await self._save()
        return len(old_keys)

# src/crypto_daily_agent/infrastructure/storage/sqlite_store.py
class SQLiteStateStore(StateStore):
    """SQLite 实现 - 更适合大量数据"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with aiosqlite.connect(self.db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS pushed_items (
                    fingerprint TEXT PRIMARY KEY,
                    pushed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pushed_at 
                ON pushed_items(pushed_at)
            """)
    
    async def cleanup_old(self, days: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM pushed_items WHERE pushed_at < datetime('now', '-{} days')".format(days)
            )
            await db.commit()
            return cursor.rowcount
```

### 3.4 可配置评分系统

```python
# src/crypto_daily_agent/pipeline/scorer.py
class NewsScorer:
    """可配置的新闻重要性评分器"""
    
    def __init__(self, weights: ScoringWeights):
        self.weights = weights
        self._keywords = {
            "binance": weights.binance,
            "币安": weights.binance,
            "bitcoin": weights.bitcoin_keyword,
            "btc": weights.bitcoin_keyword,
            "ethereum": weights.ethereum_keyword,
            "eth": weights.ethereum_keyword,
        }
    
    def score(self, item: NewsItem) -> float:
        """计算新闻重要性得分"""
        score = 1.0
        title_lower = item.title.lower()
        
        # 关键词加权
        for keyword, weight in self._keywords.items():
            if keyword in title_lower:
                score += weight
        
        # 来源加权
        source_weights = {
            "Binance": self.weights.tier1_source,
            "X": self.weights.tier1_source,
            "CoinDesk": self.weights.tier2_source,
            "TheBlock": self.weights.tier2_source,
        }
        score += source_weights.get(item.source, 0)
        
        return round(score, 2)
```

### 3.5 CoinMarketCap 价格数据集成

```python
# src/crypto_daily_agent/infrastructure/collectors/coinmarketcap.py
@register_collector
class CoinMarketCapCollector(SourceCollector):
    """
    获取加密货币价格数据作为市场温度参考
    """
    name = "coinmarketcap"
    priority = 5  # 最高优先级
    
    def __init__(self, settings: Settings):
        self.api_key = settings.coinmarketcap_api_key
        self.timeout = settings.request_timeout_seconds
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def fetch(self, http_client: HttpClient) -> list[NewsItem]:
        """获取 BTC/ETH 24h 价格变化"""
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }
        params = {"symbol": "BTC,ETH", "convert": "USD"}
        
        response = await http_client.get(url, headers=headers, params=params)
        data = response.json()
        
        items = []
        for symbol in ["BTC", "ETH"]:
            quote = data["data"][symbol]["quote"]["USD"]
            change_24h = quote["percent_change_24h"]
            
            items.append(NewsItem(
                source="CoinMarketCap",
                title=f"{symbol} 24h Change: {change_24h:+.2f}%",
                url=f"https://coinmarketcap.com/currencies/{symbol.lower()}/",
                published_at=datetime.now(timezone.utc),
                content=f"Price: ${quote['price']:.2f}, 24h Change: {change_24h:.2f}%",
                language="en",
                importance=2.0 if abs(change_24h) > 5 else 1.0,
            ))
        
        return items
```

---

## 4. 修复清单

### 4.1 Bug 修复

| 问题 | 严重程度 | 修复方案 |
|------|---------|---------|
| 状态文件无限增长 | 🔴 高 | `cleanup_old()` 方法 + 自动触发机制 |
| systemd timer 时区错误 | 🔴 高 | 修复为 `OnCalendar=*-*-* 08:00:00` |
| 评分权重硬编码 | 🟡 中 | `ScoringWeights` 配置类 |
| 错误处理复杂 | 🟡 中 | 自定义异常 + 结构化日志 |
| 缺少 CoinMarketCap | 🟡 中 | 新增采集器 |
| 无测试覆盖 | 🔴 高 | 完整测试套件 |

### 4.2 时区修复详情

```ini
# deploy/crypto-daily.timer
[Unit]
Description=Run Crypto Daily Digest at 08:00 BJT

[Timer]
# 修复前: OnCalendar=*-*-* 00:00:00 UTC (UTC 时间，错误)
# 修复后: 使用本地时间 08:00
OnCalendar=*-*-* 08:00:00
Persistent=true
Unit=crypto-daily.service

[Install]
WantedBy=timers.target
```

---

## 5. 测试策略

### 5.1 测试覆盖目标

| 模块 | 测试类型 | 目标覆盖率 |
|------|---------|-----------|
| config.py | 单元测试 | 100% |
| models.py | 单元测试 | 100% |
| scorer.py | 单元测试 | 100% |
| storage/*.py | 单元测试 | 100% |
| collectors/*.py | 单元测试 + mock | 80% |
| pipeline/*.py | 集成测试 | 80% |
| 完整流程 | E2E 测试 | 关键路径 |

### 5.2 关键 Fixtures

```python
# tests/conftest.py
@pytest.fixture
def test_settings() -> Settings:
    """测试配置 - 内存存储 + 禁用邮件"""
    return Settings(
        storage_backend="json",
        enable_email=False,
        max_news_items=5,
    )

@pytest.fixture
async def temp_storage(tmp_path: Path):
    """临时存储实例"""
    store = JsonStateStore(tmp_path / "test_state.json")
    yield store
    # 自动清理

@pytest.fixture
def sample_news_items() -> list[NewsItem]:
    """示例新闻数据"""
    return [
        NewsItem(...),
        NewsItem(...),
    ]
```

---

## 6. 迁移计划

### 6.1 向后兼容

- 保留 `.env` 配置格式，完全兼容
- 旧 `agent/` 目录保留直到迁移完成
- `state/cache.json` 可自动迁移到新格式

### 6.2 新 CLI 接口

```bash
# 原有命令
python -m agent.main --once
python -m agent.main --loop

# 新增命令
python -m crypto_daily_agent --once
python -m crypto_daily_agent --loop
python -m crypto_daily_agent --config-test    # 验证配置
python -m crypto_daily_agent --health-check   # 健康检查
python -m crypto_daily_agent --version
```

---

## 7. 性能目标

| 指标 | 当前 | 目标 | 优化方案 |
|------|------|------|---------|
| 采集时间 | ~30s | <20s | 异步并发采集 |
| 内存占用 | ~100MB | <80MB | 流式处理 |
| 状态文件大小 | 无限增长 | <1MB | 自动清理 |
| 测试运行时间 | N/A | <30s | 并行测试 |

---

**Design complete. Ready for spec review.**

---

## 8. 设计决策记录 (ADR)

### ADR 1: 为什么选择 Pydantic Settings？
- **考虑:** 手动解析 os.getenv vs Pydantic
- **决策:** 使用 Pydantic Settings
- **理由:** 类型安全、自动验证、环境变量映射、文档生成

### ADR 2: 为什么选择插件化采集器？
- **考虑:** 硬编码列表 vs 注册表模式
- **决策:** 装饰器注册表
- **理由:** 新增采集器无需修改核心代码，符合开闭原则

### ADR 3: 为什么支持 SQLite？
- **考虑:** 仅 JSON vs 多后端支持
- **决策:** 抽象存储层，支持 JSON 和 SQLite
- **理由:** SQLite 更适合大量数据，JSON 适合简单部署

---

*Document version: 1.0*  
*Created: 2026-03-24*  
*Status: Ready for review*
