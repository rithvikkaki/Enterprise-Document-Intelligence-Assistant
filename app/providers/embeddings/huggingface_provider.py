import os
import math
from typing import List
from app.core.config import settings
from app.core.logging import logger
from app.providers.embeddings.base import BaseEmbeddingProvider


class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model = None
        self._initialized = False

    def _init_model(self):
        if not self._initialized:
            # Fast synthetic fallback during automated unit test runs
            if os.environ.get("TESTING") == "true" or settings.ENVIRONMENT == "testing":
                self._model = None
                self._initialized = True
                return

            try:
                os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded local HuggingFace embedding model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {str(e)}. Using synthetic embedding fallback.")
                self._model = None
            self._initialized = True

    def _generate_synthetic_vector(self, text: str) -> List[float]:
        """Deterministic 384-dim synthetic normalized vector for offline/testing fallback."""
        vec = [0.0] * self.dimension
        for idx, char in enumerate(text[:200]):
            pos = (ord(char) * (idx + 1)) % self.dimension
            vec[pos] += math.sin(idx + 1)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed_text(self, text: str) -> List[float]:
        self._init_model()
        if self._model:
            try:
                emb = self._model.encode(text, convert_to_numpy=True)
                return emb.tolist()
            except Exception as e:
                logger.warning(f"Embedding encoding error: {str(e)}")
        return self._generate_synthetic_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._init_model()
        if self._model:
            try:
                embs = self._model.encode(texts, batch_size=settings.EMBEDDING_BATCH_SIZE, convert_to_numpy=True)
                return [e.tolist() for e in embs]
            except Exception as e:
                logger.warning(f"Batch embedding encoding error: {str(e)}")
        return [self._generate_synthetic_vector(t) for t in texts]
