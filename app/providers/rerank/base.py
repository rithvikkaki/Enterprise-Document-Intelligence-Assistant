from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: List[str]) -> List[Tuple[int, float]]:
        """Rank candidate texts against query. Returns list of (candidate_index, rerank_score)."""
        pass
