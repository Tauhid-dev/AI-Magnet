# PR-08: Scalable RAG Retrieval, Citations, Safety and Quality Evaluation

Status: not_started

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

- [ ] Inspect current vector type, migrations, and retrieval tests.
- [ ] Implement SQL pgvector retrieval with tenant filter.
- [ ] Add thresholds and no-answer fallback.
- [ ] Add citations/source response schema.
- [ ] Add citation display where appropriate.
- [ ] Add prompt-injection safety handling.
- [ ] Add RAG eval fixture suite.
- [ ] Add latency/token/cost measurement seam.
- [ ] Update status/risk/validation/visual artifacts.

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

To be filled during PR-08.

## Blockers

Requires source provenance from PR-06/PR-07.

## Completion Criteria

Tenant-grounded responses use scalable retrieval, provide source evidence, fail safely when unsupported, and pass defined safety/quality tests.
