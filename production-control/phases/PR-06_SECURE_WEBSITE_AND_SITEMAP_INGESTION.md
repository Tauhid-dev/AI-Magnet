# PR-06: Secure Website and Sitemap Ingestion

Status: verified

## Purpose

Deliver the product-defining ability for a tenant to add a website or sitemap and build tenant-owned RAG knowledge securely.

## Why It Is Needed

The current MVP supports manual text/Markdown ingestion only. Real businesses need approved website/sitemap ingestion, but crawler features can create SSRF, abuse, and data-quality risks if implemented casually.

## Preconditions

- PR-05 is verified.
- Queue/job status is available for crawl and indexing progress.
- Tenant/domain authorization strategy is understood.

## In-Scope Work

- Website URL and sitemap submission APIs/UI.
- Tenant ownership and approved-domain checks suitable for beta.
- Safe HTTP crawl/extraction pipeline for permitted public pages.
- SSRF protections for localhost, private networks, internal/cloud metadata, DNS rebinding, redirects, non-HTTP protocols, and oversized responses.
- Robots policy decision, crawl depth/page count/content size/time limits, canonical URL/deduplication, and error handling.
- Refresh, re-index, delete controls, crawl history, and status visibility.
- Sanitized content storage with source URL/title metadata.
- Tests including malicious URL, redirect, and internal-IP scenarios.

## Out-Of-Scope Work

- Browser/Playwright crawling unless ordinary crawler cannot support required customer sites.
- OCR/document ingestion, handled in PR-07.
- RAG answer citations, handled in PR-08.

## Source Areas Likely Affected

- `backend/app/rag/`
- `backend/app/workers/`
- `backend/app/models/`
- `backend/migrations/`
- `backend/app/api/business_portal.py`
- `frontend/app/portal/documents/page.tsx` or new knowledge setup routes
- `backend/tests/`
- `frontend/tests/`

## Detailed Tasks

- [x] Inspect current document ingestion and tenant business website fields.
- [x] Design crawl/source models and job flow.
- [x] Implement URL/sitemap submission with tenant ownership.
- [x] Implement SSRF-safe fetch and redirect validation.
- [x] Implement crawl limits, deduplication, and status.
- [x] Add refresh/delete history.
- [x] Add portal UI for website/sitemap ingestion.
- [x] Add malicious URL and cross-tenant tests.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Unit tests for URL validation and SSRF protections.
- Integration tests for sitemap/crawl job creation.
- API and UI tests for tenant scoping.
- Worker tests for crawl success/failure.

## Security Considerations

Crawler must never access localhost, private IPs, link-local addresses, metadata endpoints, file URLs, or unauthorised domains.

## Migration And Rollback Notes

Expect new source/crawl/job tables. Reversible migrations required.

## Evidence

- Backend source/crawl models and same-tenant constraints: `backend/app/models/knowledge.py`, `backend/migrations/versions/20260528_0009_pr06_website_sitemap_ingestion.py`.
- SSRF URL validation and redirect checks: `backend/app/rag/web_security.py`, `backend/app/rag/web_fetcher.py`.
- HTML/sitemap extraction and robots support: `backend/app/rag/web_extraction.py`, `backend/app/rag/robots.py`.
- Crawl orchestration and tenant document indexing: `backend/app/rag/website_ingestion.py`.
- Durable crawl job handler: `backend/app/jobs/service.py`, `backend/app/jobs/handlers.py`.
- Business portal APIs and UI: `backend/app/api/business_portal.py`, `backend/app/schemas/business_portal.py`, `frontend/app/portal/documents/page.tsx`, `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`.
- Security/operational documentation: `docs/website-ingestion.md`, `docs/security.md`.
- Validation:
  - `backend/.venv/bin/python -m pytest backend/tests/rag/test_website_ingestion.py` - pass, 13 tests.
  - `backend/.venv/bin/python -m pytest backend/tests` - pass, 76 tests.
  - SQLite Alembic upgrade head and downgrade to `20260528_0008` - pass.
  - `backend/.venv/bin/ruff check backend/app backend/tests` - pass.
  - `npm run typecheck` - pass.
  - `npm run lint` - pass.

## Residual Follow-Up

- First controlled crawl against customer-like public sites remains a Gate B/Gate C release-gate smoke check.
- Browser/Playwright crawling remains conditional and is not required unless ordinary HTTP crawling fails target beta sites.
- Stronger DNS/file-based domain verification can be added later if beta risk requires it; PR-06 uses authenticated tenant ownership plus configured business-domain matching.

## Blockers

None for repository implementation. Live controlled crawl smoke remains release-gate evidence.

## Completion Criteria

An authorized business can safely submit its website/sitemap, see indexing status, and build/delete/refresh tenant-contained knowledge without unsafe network fetches.
