import pytest


def test_rrf_formula_calculation():
    k = 60
    # Formula: score(doc) = sum(1 / (k + rank))

    # Document A is rank 1 in vector search, rank 2 in FTS
    score_a = (1.0 / (k + 1)) + (1.0 / (k + 2))

    # Document B is rank 2 in vector search, rank 1 in FTS
    score_b = (1.0 / (k + 2)) + (1.0 / (k + 1))

    # Document C is rank 3 in vector search only
    score_c = 1.0 / (k + 3)

    assert score_a == score_b
    assert score_a > score_c
    assert abs(score_a - 0.032522) < 0.001
