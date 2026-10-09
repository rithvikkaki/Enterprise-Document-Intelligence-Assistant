from typing import List
from app.core.config import settings
from app.providers.embeddings.base import BaseEmbeddingProvider
from app.providers.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider


class EmbeddingService:
    def __init__(self):
        # Default local HuggingFace provider
        self.provider: BaseEmbeddingProvider = HuggingFaceEmbeddingProvider()

    def generate_embedding(self, text: str) -> List[float]:
        return self.provider.embed_text(text)

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_batch(texts)
