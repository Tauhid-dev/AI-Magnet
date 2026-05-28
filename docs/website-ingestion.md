# Website And Sitemap Ingestion

PR-06 adds tenant-owned website and sitemap ingestion through the existing background job ledger.

## Workflow

1. A signed-in business portal user submits a `website` or `sitemap` source.
2. The backend validates that the URL is public HTTP(S), rejects unsafe targets, and records a tenant-owned `website_sources` row.
3. A `rag.website_crawl` background job is queued.
4. The worker fetches pages with crawl limits, extracts text and titles, stores crawl history in `website_crawl_pages`, and indexes each page as a tenant-scoped `knowledge_documents` row.
5. Refresh queues another crawl for the same source. Delete removes the source, crawl rows, and generated knowledge documents.

## Security Controls

- Only `http` and `https` URLs are allowed.
- URLs with embedded credentials are rejected.
- Localhost, loopback, private, link-local, reserved, multicast, unspecified, and known cloud metadata IPs are rejected.
- Hostnames are DNS-resolved before fetch and every redirect target is revalidated.
- Submitted pages must remain on the approved source domain.
- Tenant businesses with a configured `website_url` may only add sources on that domain or its subdomains.
- Crawl limits are enforced by `WEBSITE_CRAWL_MAX_PAGES`, `WEBSITE_CRAWL_MAX_DEPTH`, `WEBSITE_CRAWL_MAX_BYTES`, and `WEBSITE_CRAWL_MAX_REDIRECTS`.
- `robots.txt` `User-agent: *` disallow rules are respected when `WEBSITE_CRAWL_RESPECT_ROBOTS=true`.

## Beta Domain Authorization Decision

For beta scope, the authenticated tenant owner controls website/sitemap submission. If the business profile has a `website_url`, submissions must match that domain. If no business website is configured yet, the submitted source domain becomes the approved source domain for that tenant source. Stronger DNS or file-based domain verification can be added later if customer risk requires it.

## Environment Settings

```env
WEBSITE_CRAWL_USER_AGENT=AI-MagnetBot/0.1 (+https://example.com/ai-magnet-bot)
WEBSITE_CRAWL_TIMEOUT_SECONDS=10
WEBSITE_CRAWL_MAX_PAGES=10
WEBSITE_CRAWL_MAX_DEPTH=1
WEBSITE_CRAWL_MAX_BYTES=1048576
WEBSITE_CRAWL_MAX_REDIRECTS=5
WEBSITE_CRAWL_RESPECT_ROBOTS=true
```

## Validation

Targeted tests:

```bash
backend/.venv/bin/python -m pytest backend/tests/rag/test_website_ingestion.py
```

Migration smoke:

```bash
DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr06_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr06_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini downgrade 20260528_0008
```
