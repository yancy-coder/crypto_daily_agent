from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import requests

from agent.config import Settings
from agent.models import NewsItem
from agent.sources.base import SourceCollector


class XListCollector(SourceCollector):
    """
    Fetches latest posts from a predefined account list.
    Requires X_BEARER_TOKEN and configured user IDs.
    """

    ACCOUNT_IDS = [
        "44196397",  # elonmusk (example; can customize)
        "783214",  # X official (example)
    ]

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch(self) -> List[NewsItem]:
        if not self.settings.x_bearer_token:
            return []

        headers = {"Authorization": f"Bearer {self.settings.x_bearer_token}"}
        items: List[NewsItem] = []
        for uid in self.ACCOUNT_IDS:
            try:
                resp = requests.get(
                    f"https://api.twitter.com/2/users/{uid}/tweets",
                    params={"max_results": 5, "tweet.fields": "created_at"},
                    headers=headers,
                    timeout=self.settings.request_timeout_seconds,
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])
            except Exception:
                continue

            for t in data:
                created = t.get("created_at", "")
                try:
                    published = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except ValueError:
                    published = datetime.now(tz=timezone.utc)
                tweet_id = t.get("id", "")
                items.append(
                    NewsItem(
                        source="X",
                        title=t.get("text", "").split("\n")[0][:120],
                        url=f"https://x.com/i/web/status/{tweet_id}",
                        published_at=published,
                        content=t.get("text", ""),
                        language="en",
                    )
                )
        return items
