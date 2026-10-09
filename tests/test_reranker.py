import pytest
from app.providers.rerank.cross_encoder import CrossEncoderReranker


def test_cross_encoder_reranker():
    reranker = CrossEncoderReranker()
    query = "What is the annual leave policy?"
    candidates = [
        "Employees get 20 days of paid annual leave each year.",
        "The kitchen fridge is cleaned every Friday.",
        "Company laptops must be returned upon resignation.",
    ]

    ranked = reranker.rerank(query, candidates)
    assert len(ranked) == 3
    # Top candidate index should be 0 ("paid annual leave")
    top_idx, top_score = ranked[0]
    assert top_idx == 0
    assert isinstance(top_score, float)
