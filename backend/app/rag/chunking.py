"""Text chunking helpers for RAG ingestion."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    if not words:
        return []

    safe_chunk_size = max(chunk_size, 1)
    safe_overlap = min(max(overlap, 0), safe_chunk_size - 1)
    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = min(start + safe_chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - safe_overlap

    return chunks
