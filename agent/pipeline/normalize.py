from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Set

from agent.models import NewsItem


def build_fingerprint(item: NewsItem) -> str:
    base = f"{item.source}|{item.title}|{item.url}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def score_item(item: NewsItem) -> float:
    score = 1.0
    title = item.title.lower()
    if "binance" in title or "币安" in item.title:
        score += 1.2
    if "bitcoin" in title or "btc" in title:
        score += 0.9
    if "ethereum" in title or "eth" in title:
        score += 0.7
    if item.source in {"Binance", "X"}:
        score += 0.5
    return score


def filter_recent(items: List[NewsItem], now_utc: datetime | None = None) -> List[NewsItem]:
    now_utc = now_utc or datetime.now(tz=timezone.utc)
    lower = now_utc - timedelta(hours=24)
    return [i for i in items if i.published_at >= lower]


def deduplicate(items: List[NewsItem]) -> List[NewsItem]:
    seen_titles: Set[str] = set()
    result: List[NewsItem] = []
    for i in items:
        key = "".join(ch for ch in i.title.lower() if ch.isalnum())[:80]
        if not key or key in seen_titles:
            continue
        seen_titles.add(key)
        result.append(i)
    return result


def load_state(path: Path) -> Dict[str, bool]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: Path, fingerprints: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {fp: True for fp in fingerprints}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def remove_pushed(items: List[NewsItem], pushed_state: Dict[str, bool]) -> List[NewsItem]:
    result: List[NewsItem] = []
    for i in items:
        i.fingerprint = build_fingerprint(i)
        if not pushed_state.get(i.fingerprint):
            result.append(i)
    return result


def process(items: List[NewsItem], max_items: int, state_path: Path) -> List[NewsItem]:
    recent = filter_recent(items)
    unseen = remove_pushed(recent, load_state(state_path))
    unique = deduplicate(unseen)
    for item in unique:
        item.importance = score_item(item)
    unique.sort(key=lambda x: (x.importance, x.published_at), reverse=True)
    selected = unique[:max_items]
    save_state(state_path, [i.fingerprint for i in selected if i.fingerprint])
    return selected
