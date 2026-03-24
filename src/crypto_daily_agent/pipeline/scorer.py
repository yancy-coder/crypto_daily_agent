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
        return {
            "binance": self.weights.binance,
            "币安": self.weights.binance,
            "bitcoin": self.weights.bitcoin_keyword,
            "btc": self.weights.bitcoin_keyword,
            "ethereum": self.weights.ethereum_keyword,
            "eth": self.weights.ethereum_keyword,
        }
    
    def _build_source_weights(self) -> dict[str, float]:
        return {
            "Binance": self.weights.tier1_source,
            "X": self.weights.tier1_source,
            "CoinDesk": self.weights.tier2_source,
            "TheBlock": self.weights.tier2_source,
        }
    
    def score(self, item: NewsItem) -> float:
        score = 1.0
        title_lower = item.title.lower()
        for keyword, weight in self._keywords.items():
            if keyword in title_lower:
                score += weight
        score += self._source_weights.get(item.source, 0.0)
        item.importance = round(score, 2)
        return item.importance
    
    def score_batch(self, items: list[NewsItem]) -> list[NewsItem]:
        for item in items:
            self.score(item)
        return sorted(items, key=lambda x: (x.importance, x.published_at), reverse=True)
