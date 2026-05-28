"""RAG safety and prompt construction helpers."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from app.rag.retrieval import RetrievalCitation, RetrievalResult


PROMPT_INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b", re.IGNORECASE),
    re.compile(r"\b(system|developer)\s+(prompt|message|instructions?)\b", re.IGNORECASE),
    re.compile(r"\breveal\s+(secrets?|api\s*keys?|tokens?|credentials?)\b", re.IGNORECASE),
    re.compile(r"\bother\s+tenants?\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+(a\s+)?(system|developer|admin)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class RagPromptContext:
    """Safe prompt context assembled from retrieved tenant-owned chunks."""

    context: str
    citations: list[RetrievalCitation]
    safety_flags: list[str]
    top_score: float | None
    prompt_chars: int
    estimated_prompt_tokens: int


def build_safe_rag_context(
    results: list[RetrievalResult],
    *,
    visitor_message: str,
    max_chars: int,
) -> RagPromptContext:
    """Format retrieved chunks as untrusted excerpts with bounded size."""
    flags: set[str] = set()
    if looks_like_prompt_injection(visitor_message):
        flags.add("visitor_prompt_injection_pattern")

    blocks: list[str] = []
    citations: list[RetrievalCitation] = []
    remaining_chars = max(0, max_chars)
    for index, result in enumerate(results, start=1):
        citation = result.citation
        citation = RetrievalCitation(
            citation_id=f"S{index}",
            document_id=citation.document_id,
            chunk_id=citation.chunk_id,
            chunk_index=citation.chunk_index,
            score=citation.score,
            filename=citation.filename,
            source_type=citation.source_type,
            source_title=citation.source_title,
            source_url=citation.source_url,
        )
        content = normalise_context_text(result.chunk.content)
        if looks_like_prompt_injection(content):
            flags.add("context_prompt_injection_pattern")
        source_label = citation.source_title or citation.source_url or citation.filename
        prefix = f"[{citation.citation_id}] Source: {source_label}\nExcerpt: "
        budget = remaining_chars - len(prefix)
        if budget <= 0:
            break
        excerpt = content[:budget]
        remaining_chars -= len(prefix) + len(excerpt)
        blocks.append(f"{prefix}{excerpt}")
        citations.append(citation)
        if remaining_chars <= 0:
            break

    context = "\n\n".join(blocks)
    return RagPromptContext(
        context=context,
        citations=citations,
        safety_flags=sorted(flags),
        top_score=max((result.score for result in results), default=None),
        prompt_chars=len(context),
        estimated_prompt_tokens=estimate_tokens(context),
    )


def normalise_context_text(value: str) -> str:
    """Collapse control characters while preserving readable context."""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", value)
    return re.sub(r"\s+", " ", cleaned).strip()


def looks_like_prompt_injection(value: str) -> bool:
    """Return true for common prompt-injection instruction patterns."""
    return any(pattern.search(value) for pattern in PROMPT_INJECTION_PATTERNS)


def estimate_tokens(value: str) -> int:
    """Cheap token estimate for usage metering until provider token data is wired."""
    if not value:
        return 0
    return max(1, math.ceil(len(value) / 4))
