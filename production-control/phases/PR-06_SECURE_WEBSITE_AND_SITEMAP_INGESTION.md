# PR-06: Secure Website and Sitemap Ingestion

Status: not_started

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

- [ ] Inspect current document ingestion and tenant business website fields.
- [ ] Design crawl/source models and job flow.
- [ ] Implement URL/sitemap submission with tenant ownership.
- [ ] Implement SSRF-safe fetch and redirect validation.
- [ ] Implement crawl limits, deduplication, and status.
- [ ] Add refresh/delete history.
- [ ] Add portal UI for website/sitemap ingestion.
- [ ] Add malicious URL and cross-tenant tests.
- [ ] Update status/risk/validation/visual artifacts.

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

To be filled during PR-06.

## Blockers

Requires PR-05 queue/job status.

## Completion Criteria

An authorized business can safely submit its website/sitemap, see indexing status, and build/delete/refresh tenant-contained knowledge without unsafe network fetches.
