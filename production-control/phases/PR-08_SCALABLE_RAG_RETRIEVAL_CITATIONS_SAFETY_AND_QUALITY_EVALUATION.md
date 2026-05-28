# PR-08: Scalable RAG Retrieval, Citations, Safety and Quality Evaluation

Status: verified

## Purpose

Make answers grounded, traceable, scalable, and safer for customer-facing use.

## Why It Is Needed

Current retrieval loads all tenant chunks and scores in Python. Chat responses do not return source citations, thresholds, or safety evidence. This will not scale or meet beta trust requirements.

## Preconditions

- PR-06 and PR-07 are verified.
- Knowledge sources have reliable provenance metadata.

## In-Scope Work

- Move retrieval to database-side pgvector SQL with tenant filtering inside the query.
- Add indexes and bounded top-K/threshold behavior.
- Return citation/source metadata through backend APIs and show it in test/widget/portal experiences where appropriate.
- Ensure refresh/delete consistency and provenance traceability.
- Treat ingested documents as untrusted data, not executable instructions.
- Add prompt-injection handling for ingested content and visitor prompts.
- Add no-answer/low-confidence fallback behavior.
- Add RAG evaluation fixtures for grounded answers, missing knowledge, wrong tenant, malicious instructions, and citation correctness.
- Track latency, token, and cost signals needed for quotas.

## Out-Of-Scope Work

- Full billing enforcement, handled in PR-10/PR-11.
- Streaming chat unless chosen later.

## Source Areas Likely Affected

- `backend/app/rag/retrieval.py`
- `backend/app/rag/scoring.py`
- `backend/app/chat/service.py`
- `backend/app/schemas/chat.py`
- `backend/app/models/knowledge.py`
- `backend/migrations/`
- `widget/chat-widget.js`
- `frontend/`
- `backend/tests/rag/`
- `backend/tests/chat/`

## Detailed Tasks

- [x] Inspect current vector type, migrations, and retrieval tests.
- [x] Implement SQL pgvector retrieval with tenant filter.
- [x] Add thresholds and no-answer fallback.
- [x] Add citations/source response schema.
- [x] Add citation display where appropriate.
- [x] Add prompt-injection safety handling.
- [x] Add RAG eval fixture suite.
- [x] Add latency/token/cost measurement seam.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- PostgreSQL/pgvector integration test or documented staging validation.
- RAG evaluation tests.
- Wrong-tenant retrieval tests.
- Chat API citation tests.
- Frontend/widget checks if UI changes.

## Security Considerations

Retrieved content is untrusted. It must not override system/developer instructions or expose unrelated tenant data.

## Migration And Rollback Notes

Index changes or source metadata changes require reversible migrations and performance notes.

## Evidence

- SQL pgvector retrieval path with tenant/status filters: `backend/app/rag/retrieval.py`.
- PostgreSQL retrieval indexes: `backend/migrations/versions/20260529_0011_pr08_pgvector_retrieval_indexes.py`.
- RAG safety prompt assembly and prompt-injection pattern flags: `backend/app/rag/safety.py`.
- Chat API citation response and RAG metadata: `backend/app/schemas/chat.py`, `backend/app/api/chat.py`, `backend/app/chat/service.py`.
- Widget citation display: `widget/chat-widget.js`.
- RAG quality documentation: `docs/rag-quality.md`.
- RAG/citation/safety evaluation fixtures: `backend/tests/rag/test_rag_safety_eval.py`.
- Retrieval threshold/citation tests: `backend/tests/rag/test_ingestion_and_retrieval.py`.
- Validation:
  - `backend/.venv/bin/python -m pytest backend/tests/rag/test_ingestion_and_retrieval.py backend/tests/rag/test_rag_safety_eval.py backend/tests/chat/test_chat_api.py` - pass, 15 tests.
  - `backend/.venv/bin/python -m ruff check backend/app backend/tests` - pass.

## Blockers

No repository-controlled PR-08 blockers remain. Production-equivalent PostgreSQL/pgvector staging smoke remains release-gate evidence before real customer pilot.

## Completion Criteria

Tenant-grounded responses use scalable retrieval, provide source evidence, fail safely when unsupported, and pass defined safety/quality tests.
