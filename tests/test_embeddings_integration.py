import os
import pytest
from app.providers.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider


@pytest.mark.integration
def test_real_huggingface_embedding_generation():
    """Real HuggingFace SentenceTransformer integration test (Part 6 verification)."""
    # Force real model loading (disable testing synthetic bypass)
    os.environ["TESTING"] = "false"
    try:
        provider = HuggingFaceEmbeddingProvider()
        
        # 1. Single Text Embedding
        text = "Enterprise Document Intelligence Platform local vector embedding test"
        vector = provider.embed_text(text)

        # 2. Verify numeric and exact 384 dimension
        assert isinstance(vector, list)
        assert len(vector) == 384
        assert all(isinstance(val, float) for val in vector)

        # 3. Batch Embeddings
        texts = ["First document text chunk", "Second document text chunk"]
        batch_vectors = provider.embed_batch(texts)
        assert len(batch_vectors) == 2
        assert len(batch_vectors[0]) == 384
        assert len(batch_vectors[1]) == 384
    finally:
        os.environ["TESTING"] = "true"
