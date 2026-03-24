"""主服务 - 每日资讯汇总."""

import logging
from datetime import datetime, timedelta, timezone

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
        if self.settings.storage_backend == "json":
            return JsonStateStore(
                self.settings.state_dir / "cache.json",
                cleanup_days=self.settings.storage_cleanup_days,
            )
        raise NotImplementedError("SQLite backend not yet implemented")
    
    async def run(self) -> DigestContext:
        """执行一次资讯汇总."""
        LOGGER.info("digest_run_started")
        
        async with HttpClient(self.settings.request_timeout_seconds) as http_client:
            all_items = await registry.collect_all(self.settings, http_client)
        
        LOGGER.info(f"collected_total={len(all_items)}")
        
        recent_items = self._filter_recent(all_items)
        unique_items = await self._deduplicate(recent_items)
        LOGGER.info(f"after_dedup={len(unique_items)}")
        
        scored_items = self.scorer.score_batch(unique_items)
        selected = scored_items[:self.settings.max_news_items]
        
        await self.store.mark_pushed([item.fingerprint for item in selected])
        context = self._build_context(selected)
        
        LOGGER.info(f"digest_complete items={len(selected)}")
        return context
    
    def _filter_recent(self, items: list[NewsItem]) -> list[NewsItem]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        return [item for item in items if item.published_at >= cutoff]
    
    async def _deduplicate(self, items: list[NewsItem]) -> list[NewsItem]:
        result = []
        for item in items:
            if not await self.store.is_pushed(item.fingerprint):
                result.append(item)
        return result
    
    def _build_context(self, items: list[NewsItem]) -> DigestContext:
        now = datetime.now()
        if not items:
            return DigestContext(
                date_str=now.strftime("%Y-%m-%d"),
                market_temperature="中性",
                headline="今日暂无高置信度新资讯",
                cards=[],
            )
        
        avg_importance = sum(item.importance for item in items) / len(items)
        temperature = "偏热" if avg_importance >= 2.3 else "中性偏热" if avg_importance >= 1.8 else "中性"
        
        cards = []
        for idx, item in enumerate(items, start=1):
            cards.append({
                "rank": idx,
                "title": item.title[:70],
                "summary": (item.content or item.title)[:90] if item.language == "zh" else (item.content or item.title).replace("\n", " ")[:90],
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
