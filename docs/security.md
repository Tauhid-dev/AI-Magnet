# Security Checklist

## MVP Security Goals

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

Production authentication now uses password verification, session-version revocation, failed-login lockout, HttpOnly/SameSite cookies for browser sessions, and admin TOTP enforcement when MFA is enabled. Unsafe cookie-authenticated writes require `X-AI-Magnet-CSRF`.

Production hardening still required before public launch:

- Add admin MFA enrollment/rotation UX.
- Move abuse controls from single-process app memory to production proxy/distributed enforcement where needed.
- Add operational incident response runbooks.

## Production Runtime Guardrails

In `APP_ENV=production`, the backend rejects startup when:

- `BUSINESS_PORTAL_SESSION_SECRET` is a known placeholder.
- `ADMIN_PORTAL_SESSION_SECRET` is a known placeholder.
- `CORS_ALLOWED_ORIGINS` contains `*`.
- `ENABLE_API_DOCS=true`.
- `AUTH_COOKIE_SECURE=false`.
- `APP_LOG_FORMAT` is not `json`.
- `DATABASE_URL` uses SQLite, default credentials, or placeholder credentials.
- `REDIS_URL` points to localhost instead of a private service hostname.
- OpenAI-compatible AI is selected without `AI_API_KEY`.
- SMTP/email provider settings are missing.
- `PUBLIC_BASE_URL` is not HTTPS.
- `BACKUP_ENCRYPTION_PASSPHRASE` is missing or weak.

Use strong random secrets from a password manager or cloud secret store. Do not commit `.env` files.

## PII Handling

Customer PII includes names, phone numbers, emails, suburbs, job details, and conversation history.

Rules:

- Do not include raw contact details in admin aggregate analytics.
- Limit support context to operational fields and contact-presence flags unless full access is explicitly required.
- Do not log request bodies containing conversation content or contact details.
- Send only relevant tenant knowledge and recent chat context to the AI provider.
- Redact likely PII fields before writing audit attributes.
- Use the admin privacy export endpoint for tenant review requests instead of ad hoc database dumps.
- Use tenant offboarding and confirmed deletion workflows to enforce beta-scope retention/deletion decisions.

## AI and RAG Privacy

RAG retrieval must filter by tenant before scoring and returning chunks. Similar documents from another tenant must not influence answers.

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
- CI security scans exist, but PR-04 requires their first remote run to pass before relying on them as release evidence.
- Live PostgreSQL plus pgvector migration/startup validation path exists, but has not been run against a VPS/staging database.
- Worker queue framework is not selected yet; the current worker service is deployment wiring.
