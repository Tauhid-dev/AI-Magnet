# PR-07: Secure Document Ingestion, Storage and OCR Path

Status: not_started

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

- [ ] Inspect current text ingestion and document schema.
- [ ] Decide storage and extraction libraries.
- [ ] Add upload validation and limits.
- [ ] Add PDF/DOCX extraction path.
- [ ] Add OCR gate or implementation path.
- [ ] Add secure storage lifecycle and delete/refresh.
- [ ] Add portal file upload UI.
- [ ] Add malformed/oversize/unsupported/cross-tenant tests.
- [ ] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- File extraction fixtures.
- API upload tests.
- Tenant isolation tests.
- Worker job status tests.
- Frontend lint/typecheck/test/build.

## Security Considerations

Never trust MIME or filename alone. Protect from oversized files, decompression bombs, malicious content, and public file exposure.

## Migration And Rollback Notes

Storage paths and extraction state may require schema changes. Rollback must not orphan sensitive files.

## Evidence

To be filled during PR-07.

## Blockers

Requires queue/job reliability from PR-05.

## Completion Criteria

Supported business documents can be safely uploaded, processed, traced to sources, and deleted/refreshed under tenant boundaries.
