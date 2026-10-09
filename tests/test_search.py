import pytest
from app.services.embedding_service import EmbeddingService


def test_huggingface_embeddings():
    service = EmbeddingService()
    emb = service.generate_embedding("Enterprise Document Intelligence Platform")
    assert len(emb) == 384
    assert isinstance(emb, list)

    batch_embs = service.generate_batch_embeddings(["Text 1", "Text 2"])
    assert len(batch_embs) == 2
    assert len(batch_embs[0]) == 384
