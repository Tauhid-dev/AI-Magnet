# Security Checklist

## Security Goals

- Keep tenant-owned data isolated by `tenant_id`.
- Prevent business portal tokens from authorizing super admin APIs.
- Prevent super admin tokens from authorizing business portal APIs.
- Keep RAG retrieval tenant-scoped.
- Avoid logging secrets and unnecessary customer PII.
- Audit super admin access to tenant data.
- Require safe production runtime configuration.

## Tenant Isolation

Every tenant-owned model must include `tenant_id`. Service and route queries must filter by the verified tenant context before returning records.

PR-03 adds database-level same-tenant protections for the high-risk parent/child relationships. Composite constraints now prevent a child row from referencing a parent owned by a different tenant for business users, document chunks, messages, leads, notification settings, and notification deliveries.

High-risk paths that require tests:

- Business portal leads.
- Business portal conversations.
- Business portal analytics.
- Widget conversation messages.
- RAG document retrieval.
- Notification delivery records.
- Admin support context.

## Authentication Boundaries

Business portal sessions and super admin sessions use separate HMAC secrets and token payloads. A token from one portal must not authorize the other portal.

Production authentication now uses password verification, session-version revocation, failed-login lockout, HttpOnly/SameSite cookies for browser sessions, and mandatory TOTP enforcement for active `super_admin` records. In production, super-admin login and existing session validation fail closed when MFA is disabled or no valid MFA secret is configured. Unsafe cookie-authenticated writes require `X-AI-Magnet-CSRF`.

Production hardening still required before public launch:

- Add admin MFA enrollment/rotation UX.
- Add operational incident response runbooks.

## Rate Limiting And Abuse Controls

Application-level rate limiting supports two explicit backends:

- `RATE_LIMIT_BACKEND=memory` for local development and tests only.
- `RATE_LIMIT_BACKEND=redis` for production.

Production startup validation rejects non-Redis rate limiting. Redis-backed limits coordinate across backend instances and cover the same sensitive scopes used by the API routes: admin login, business login, widget initialisation, chat start/message, portal writes, and high-risk admin writes. If Redis is unavailable while Redis limiting is selected, protected endpoints fail closed with HTTP 503 and `/ready` reports degraded rate-limit readiness.

Nginx IP-level limits remain defence in depth, not the sole protection.

## Production Runtime Guardrails

In `APP_ENV=production`, the backend rejects startup when:

- `BUSINESS_PORTAL_SESSION_SECRET` is a known placeholder.
- `ADMIN_PORTAL_SESSION_SECRET` is a known placeholder.
- `CORS_ALLOWED_ORIGINS` contains `*`.
- `ENABLE_API_DOCS=true`.
- `AUTH_COOKIE_SECURE=false`.
- `APP_LOG_FORMAT` is not `json`.
- `RATE_LIMIT_BACKEND` is not `redis`.
- `RATE_LIMIT_REDIS_KEY_PREFIX` is missing or `RATE_LIMIT_REDIS_TIMEOUT_SECONDS` is invalid.
- `DATABASE_URL` uses SQLite, default credentials, or placeholder credentials.
- `REDIS_URL` points to localhost instead of a private service hostname.
- OpenAI-compatible AI is selected without `AI_API_KEY`.
- SMTP/email provider settings are missing.
- `PUBLIC_BASE_URL` is not HTTPS.
- `BACKUP_ENCRYPTION_PASSPHRASE` is missing or weak.
- `DOCUMENT_STORAGE_ROOT` is missing.
- Document upload size/page limits are invalid.
- Document malware scanning is disabled or misconfigured.

Use strong random secrets from a password manager or cloud secret store. Do not commit `.env` files.

## PII Handling

Customer PII includes names, phone numbers, emails, suburbs, job details, and conversation history.

Rules:

- Do not include raw contact details in admin aggregate analytics.
- Limit support context to operational fields and contact-presence flags unless full access is explicitly required.
- Do not log request bodies containing conversation content or contact details.
- Send only relevant tenant knowledge and recent chat context to the AI provider.
- Redact likely PII fields before writing audit attributes.
- Do not expose background job payloads through tenant or admin APIs; sensitive ingestion payloads are redacted after terminal job completion/failure.
- Use the admin privacy export endpoint for tenant review requests instead of ad hoc database dumps.
- Use tenant offboarding and confirmed deletion workflows to enforce beta-scope retention/deletion decisions.

## AI and RAG Privacy

RAG retrieval must filter by tenant before scoring and returning chunks. Similar documents from another tenant must not influence answers. PR-08 uses a PostgreSQL/pgvector retrieval query with tenant and `knowledge_documents.status = 'ingested'` filters inside SQL for production, with a SQLite-only fallback for local tests.

Website and sitemap ingestion must also remain tenant-scoped. PR-06 stores each approved source in `website_sources`, each crawl row in `website_crawl_pages`, and each generated document with source metadata on `knowledge_documents`. The crawler rejects unsafe SSRF targets, revalidates redirects, applies crawl limits, respects basic `robots.txt` disallow rules, and only ingests URLs that match the approved source domain.

Document ingestion must remain tenant-scoped and private. PR-07 stores uploaded files under `DOCUMENT_STORAGE_ROOT`, never in public frontend/Nginx paths, and file-backed jobs carry only `document_id` instead of raw bytes. Upload validation enforces allowed beta types, size limits, filename sanitisation, MIME/extension/signature checks, UTF-8 text checks, DOCX package checks, PDF signature checks, and deterministic basic malware screening. Scanned PDFs fail closed with `ocr_status=required` until a production OCR path is explicitly enabled and validated.

Retrieved RAG excerpts are untrusted reference material. PR-08 wraps excerpts with source labels, returns source citations to the chat API/widget, records prompt-injection pattern flags, and returns the configured no-answer fallback without calling the LLM when no tenant chunk clears the similarity threshold.

AI provider configuration must come from environment variables:

- `AI_PROVIDER`
- `AI_API_BASE_URL`
- `AI_API_KEY`
- `AI_EMBEDDING_MODEL`
- `AI_CHAT_MODEL`

Never put provider keys in frontend code, widget code, roadmap assets, docs, or committed `.env` files.

## Audit Logging

Audit these actions:

- Tenant creation.
- Tenant detail access.
- Tenant support context access.
- Tenant status changes.
- Privacy export generation.
- Tenant offboarding.
- Tenant data deletion.
- Admin login/logout and global administrative actions.

Tenant audit logs remain scoped by `tenant_id`. Global admin audit logs are stored separately so critical administrative evidence can survive tenant deletion. Audit logs should avoid secrets and raw customer message bodies.

## Deployment Security

Before production:

- Use `docker-compose.prod.yml`, not the development `docker-compose.yml`.
- Terminate HTTPS at Nginx or a trusted upstream proxy with HSTS enabled.
- Restrict database and Redis to private Docker networking with no host port publishing.
- Configure encrypted backups and restore tests.
- Set `NEXT_PUBLIC_API_BASE_URL=/api` when serving through Nginx.
- Disable API docs in production.
- Replace local console email delivery with SMTP settings.
- Review npm and Python dependency advisories through CI security scans.
- Preserve request/correlation IDs across Nginx and backend logs.

## Current Residual Risks

- No automated backup job exists yet.
- Backup scripts and renewal commands exist, but the first VPS backup/restore drill has not been executed.
- TLS certificate automation is documented, but the first live certificate issuance has not been executed.
- Production PostgreSQL/Redis private topology exists in `docker-compose.prod.yml`, but VPS port/firewall validation remains a release check.
- CI security scans exist, but PR-05 requires its first remote run to pass before relying on them as release evidence.
- Live PostgreSQL plus pgvector migration/startup validation path exists, but has not been run against a VPS/staging database.
- Durable worker queue code exists, but first live worker/Redis smoke validation remains a release check.
- PR-06 website/sitemap crawler is bounded and SSRF-hardened in repository tests, but first controlled crawl against real customer-like websites remains a release check before pilot onboarding.
- PR-07 document ingestion supports text, Markdown, PDF text extraction, and DOCX extraction with private storage and tests; production OCR runtime and full malware/quarantine integration remain gated launch checks.
