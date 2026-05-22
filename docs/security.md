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

Production hardening still required before public launch:

- Replace email-only MVP login with passwordless magic link, password plus MFA, or external identity provider.
- Add rate limiting to login and public widget endpoints.
- Add session revocation or rotation strategy.
- Add operational incident response runbooks.

## Production Runtime Guardrails

In `APP_ENV=production`, the backend rejects startup when:

- `BUSINESS_PORTAL_SESSION_SECRET` is a known placeholder.
- `ADMIN_PORTAL_SESSION_SECRET` is a known placeholder.
- `CORS_ALLOWED_ORIGINS` contains `*`.
- `ENABLE_API_DOCS=true`.

Use strong random secrets from a password manager or cloud secret store. Do not commit `.env` files.

## PII Handling

Customer PII includes names, phone numbers, emails, suburbs, job details, and conversation history.

Rules:

- Do not include raw contact details in admin aggregate analytics.
- Limit support context to operational fields and contact-presence flags unless full access is explicitly required.
- Do not log request bodies containing conversation content or contact details.
- Send only relevant tenant knowledge and recent chat context to the AI provider.

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
- Future destructive actions such as deletion or export.

Audit logs should avoid secrets and raw customer message bodies.

## Deployment Security

Before production:

- Terminate HTTPS at Nginx or a trusted upstream proxy.
- Restrict database and Redis ports to private networking.
- Configure backups and restore tests.
- Set `NEXT_PUBLIC_API_BASE_URL=/api` when serving through Nginx.
- Disable API docs in production.
- Replace local console email delivery with SMTP settings.
- Review npm and Python dependency advisories.

## Current Residual Risks

- MVP auth is not production-grade yet.
- No rate limiting exists yet.
- No automated backup job exists yet.
- No TLS certificate automation is included yet.
- Worker queue framework is not selected yet; the current worker service is deployment wiring.
