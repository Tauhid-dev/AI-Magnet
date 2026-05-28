# PR-07: Secure Document Ingestion, Storage and OCR Path

Status: verified

## Purpose

Allow real customer knowledge documents to be uploaded and processed safely.

## Why It Is Needed

Current ingestion supports only JSON-submitted text/Markdown. PDF is explicitly unsupported. Real customer onboarding needs safe file upload, extraction, storage, delete/refresh, and source tracking.

## Preconditions

- PR-05 is verified.
- Queue/job status is available for file extraction/indexing.

## In-Scope Work

- Multipart file upload for agreed beta types, at minimum PDF and DOCX where practical, retaining text/Markdown.
- File type, MIME, signature, size, page, and filename checks.
- Tenant-owned storage decision: secure local or object storage abstraction with non-public access.
- Malware/quarantine scanning plan or implementation suitable for launch gate.
- PDF text extraction and scanned-document OCR path or clearly gated OCR support.
- Extraction error states, job progress, re-index, refresh, and delete controls.
- Tests for unsupported, malformed, oversized, and cross-tenant cases.

## Out-Of-Scope Work

- Website/sitemap ingestion, handled in PR-06.
- RAG retrieval/citation quality, handled in PR-08.

## Source Areas Likely Affected

- `backend/app/rag/extraction.py`
- `backend/app/rag/ingestion.py`
- `backend/app/models/knowledge.py`
- `backend/migrations/`
- `backend/app/api/business_portal.py`
- `frontend/app/portal/documents/page.tsx`
- `backend/tests/rag/`
- `frontend/tests/`

## Detailed Tasks

- [x] Inspect current text ingestion and document schema.
- [x] Decide storage and extraction libraries.
- [x] Add upload validation and limits.
- [x] Add PDF/DOCX extraction path.
- [x] Add OCR gate or implementation path.
- [x] Add secure storage lifecycle and delete/refresh.
- [x] Add portal file upload UI.
- [x] Add malformed/oversize/unsupported/cross-tenant tests.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- File extraction fixtures.
- API upload tests.
- Tenant isolation tests.
- Worker job status tests.
- Frontend lint/typecheck/test/build.

## Security Considerations

Never trust MIME or filename alone. Protect from oversized files, decompression bombs, malicious content, and public file exposure.

## Migration And Rollback Notes

Migration `20260529_0010_pr07_secure_document_ingestion.py` adds file size, SHA-256, malware scan, extraction, and OCR metadata. Rollback removes metadata columns and index but does not remove private stored files; operators must delete orphaned storage explicitly if rolling back after uploads.

## Evidence

- `backend/app/rag/document_validation.py`
- `backend/app/rag/document_storage.py`
- `backend/app/rag/extraction.py`
- `backend/app/jobs/handlers.py`
- `backend/app/api/business_portal.py`
- `backend/migrations/versions/20260529_0010_pr07_secure_document_ingestion.py`
- `frontend/app/portal/documents/page.tsx`
- `docs/document-ingestion.md`
- `backend/tests/rag/test_secure_document_ingestion.py`
- `backend/.venv/bin/python -m pytest backend/tests` - pass, 81 tests.
- `backend/.venv/bin/python -m ruff check backend/app backend/tests` - pass.
- SQLite Alembic upgrade head and downgrade to `20260528_0009` - pass.
- `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` - pass.
- `pip-audit`, `bandit`, secret pattern scan, and `npm audit --audit-level=high` - pass for configured gates; npm reports moderate Next.js/PostCSS advisories.

## Blockers

No repository-controlled PR-07 blockers remain. Scanned-document OCR runtime is intentionally gated and remains a future explicit implementation path before OCR can be claimed in production.

## Completion Criteria

Supported business documents can be safely uploaded, processed, traced to sources, and deleted/refreshed under tenant boundaries.
