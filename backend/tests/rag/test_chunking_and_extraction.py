import pytest

from app.rag.chunking import chunk_text
from app.rag.extraction import extract_text


def test_chunk_text_uses_overlap_without_empty_chunks():
    chunks = chunk_text(
        "one two three four five six seven",
        chunk_size=3,
        overlap=1,
    )

    assert chunks == [
        "one two three",
        "three four five",
        "five six seven",
    ]


def test_extract_text_accepts_markdown_bytes():
    extracted = extract_text(b"# Services\nEmergency plumbing", "text/markdown")

    assert "Emergency plumbing" in extracted


def test_extract_text_rejects_unsupported_types():
    with pytest.raises(ValueError, match="Unsupported content type"):
        extract_text(b"%PDF-1.4", "application/pdf")
