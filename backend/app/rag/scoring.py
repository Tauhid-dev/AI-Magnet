"""RAG retrieval scoring helpers."""

from __future__ import annotations

import math


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for two vectors."""
    if not left or not right or len(left) != len(right):
        return 0.0
    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    denominator = left_norm * right_norm
    if denominator == 0:
        return 0.0
    return dot_product / denominator
