"""Document text extraction helpers."""

from __future__ import annotations


SUPPORTED_TEXT_TYPES = {
    "text/plain",
    "text/markdown",
    "application/x-markdown",
}


def extract_text(content: bytes, content_type: str | None = None) -> str:
    """Extract text from supported document bytes."""
    normalized_type = (content_type or "text/plain").split(";")[0].strip().lower()
    if normalized_type not in SUPPORTED_TEXT_TYPES:
        raise ValueError(f"Unsupported content type for Phase 3 ingestion: {content_type}")
    return content.decode("utf-8")
