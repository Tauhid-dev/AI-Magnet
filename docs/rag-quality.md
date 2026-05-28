# RAG Retrieval, Citations, and Safety

Last updated: 2026-05-29

## Production Retrieval Path

The production retrieval path uses PostgreSQL/pgvector SQL in `backend/app/rag/retrieval.py`.

- Query embeddings are passed as bound pgvector literals.
- Tenant filtering is inside the SQL `WHERE` clause.
- Only `knowledge_documents.status = 'ingested'` chunks are eligible.
- Results are bounded by `RAG_TOP_K` and `RAG_SIMILARITY_THRESHOLD`.
- PostgreSQL retrieval indexes are added in `backend/migrations/versions/20260529_0011_pr08_pgvector_retrieval_indexes.py`.

SQLite/local tests use a Python scoring fallback so the repository test suite remains lightweight. The fallback keeps the same tenant/status filters and thresholds, but it is not the production scale path.

## Citations

Chat responses now return citation metadata in `citations`.

Each citation includes:

- citation id such as `S1`
- document id and chunk id
- chunk index
- score
- filename
- source type
- source title
- source URL when available

The widget displays source links for cited answers. Backend tests cover citation correctness and wrong-tenant exclusion.

## Safety Controls

Retrieved content is treated as untrusted reference material.

`backend/app/rag/safety.py`:

- formats retrieved chunks with source labels
- bounds prompt context length using `RAG_MAX_CONTEXT_CHARS`
- detects common prompt-injection patterns in visitor prompts and retrieved excerpts
- records safety flags in chat responses and usage events
- estimates prompt/response tokens for PR-10 quota and cost controls

When no chunk clears the threshold, the chat service returns `RAG_NO_ANSWER_MESSAGE` without calling the chat provider.

## Validation

Focused PR-08 validation:

```bash
backend/.venv/bin/python -m pytest backend/tests/rag/test_ingestion_and_retrieval.py backend/tests/rag/test_rag_safety_eval.py backend/tests/chat/test_chat_api.py
backend/.venv/bin/python -m ruff check backend/app backend/tests
```

Required staging/VPS validation before real customer pilot:

```bash
scripts/validate_pgvector_migrations.sh
```

Then run a controlled tenant ingest/chat smoke against production-equivalent PostgreSQL and confirm:

- pgvector extension is available
- migrations reach head
- retrieval returns tenant-owned citations only
- low-confidence/no-answer behavior is acceptable for launch copy
- usage logs include retrieval latency and estimated token signals
