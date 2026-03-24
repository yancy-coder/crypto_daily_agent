from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from agent.models import NewsItem


def zh_summary(item: NewsItem) -> str:
    if item.language == "zh":
        text = item.content or item.title
        return text[:90]
    # Lightweight fallback without LLM dependency.
    return (item.content or item.title).replace("\n", " ")[:90]


def build_render_context(items: List[NewsItem]) -> Dict[str, object]:
    now = datetime.now().strftime("%Y-%m-%d")
    if not items:
        return {
            "date_str": now,
            "market_temperature": "中性",
            "headline": "今日暂无高置信度新资讯",
            "cards": [],
        }

    cards = []
    for idx, it in enumerate(items, start=1):
        cards.append(
            {
                "rank": idx,
                "title": it.title[:70],
                "summary": zh_summary(it),
                "source": it.source,
                "time": it.published_at.strftime("%H:%M UTC"),
                "url": it.url,
            }
        )
    avg = sum(i.importance for i in items) / len(items)
    temp = "偏热" if avg >= 2.3 else "中性偏热" if avg >= 1.8 else "中性"
    return {
        "date_str": now,
        "market_temperature": temp,
        "headline": items[0].title[:88],
        "cards": cards,
    }
