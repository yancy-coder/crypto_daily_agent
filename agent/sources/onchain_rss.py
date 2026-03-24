from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import feedparser

from agent.models import NewsItem
from agent.sources.base import SourceCollector


class OnchainRssCollector(SourceCollector):
    """Uses The Block RSS as a lightweight on-chain/institutional signal source."""

    def fetch(self) -> List[NewsItem]:
        feed = feedparser.parse("https://www.theblock.co/rss.xml")
        items: List[NewsItem] = []
        for e in feed.entries[:20]:
            published = datetime.now(tz=timezone.utc)
            if getattr(e, "published_parsed", None):
                published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            items.append(
                NewsItem(
                    source="TheBlock",
                    title=e.get("title", "").strip(),
                    url=e.get("link", ""),
                    published_at=published,
                    content=e.get("summary", "")[:500],
                    language="en",
                )
            )
        return items
