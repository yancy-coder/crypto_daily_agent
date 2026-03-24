from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from agent.models import NewsItem


class SourceCollector(ABC):
    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        raise NotImplementedError
