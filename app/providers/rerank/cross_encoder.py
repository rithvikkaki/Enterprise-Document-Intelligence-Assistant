import os
from typing import List, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.providers.rerank.base import BaseReranker


class CrossEncoderReranker(BaseReranker):
    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self._model = None
        self._initialized = False

    def _init_model(self):
        if not self._initialized:
            if os.environ.get("TESTING") == "true" or settings.ENVIRONMENT == "testing":
                self._model = None
                self._initialized = True
                return

            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
                logger.info(f"Loaded local CrossEncoder reranker model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not load CrossEncoder model '{self.model_name}': {str(e)}")
                self._model = None
            self._initialized = True

    def rerank(self, query: str, candidates: List[str]) -> List[Tuple[int, float]]:
        if not candidates:
            return []

        self._init_model()
        if self._model:
            try:
                pairs = [[query, text] for text in candidates]
                scores = self._model.predict(pairs)
                indexed_scores = [(idx, float(score)) for idx, score in enumerate(scores)]
                indexed_scores.sort(key=lambda x: x[1], reverse=True)
                return indexed_scores
            except Exception as e:
                logger.warning(f"CrossEncoder prediction error: {str(e)}")

        # Fallback ranking if cross-encoder model is not loaded
        indexed_scores = [(idx, 1.0 / (idx + 1)) for idx in range(len(candidates))]
        return indexed_scores
