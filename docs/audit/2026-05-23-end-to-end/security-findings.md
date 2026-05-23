# Security Findings

Repository root: `/Users/thuda/Desktop/Resources/Personal/Projects/AI-Magnet`

## Critical Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| SEC-001 | CRITICAL | Business portal login is email-only and does not verify mailbox ownership. | `backend/app/business/auth.py` lines 39-63 | Anyone who knows an active tenant slug and business email can obtain a session. | Replace with verified magic link, password plus MFA, or external IdP. Add lockout/rate limits. |
| SEC-002 | CRITICAL | Super admin login is email-only. | `backend/app/admin/auth.py` lines 40-56 | A known admin email can receive an admin token without password/MFA. | Add MFA-backed admin auth before any real deployment. |
| SEC-003 | CRITICAL | No rate limiting exists for login, widget init, or chat endpoints. | `docs/security.md` lists this as residual risk; no rate-limit middleware found | Brute force, spam, cost abuse, and AI token exhaustion. | Add reverse proxy and app-level rate limits per IP, widget key, tenant, and account. |
| SEC-004 | CRITICAL | TLS is not configured or automated. | `infra/nginx/default.conf` listens on `80`; `docs/deployment.md` says add cert automation | Credentials, chat PII, and admin traffic can be exposed if deployed as-is. | Add HTTPS config, certificate automation, HSTS, secure proxy headers. |
| SEC-005 | CRITICAL | PostgreSQL and Redis are published to host by default. | `docker-compose.yml` publishes `5432` and `6379` | Accidental public exposure on VPS/firewall misconfiguration. | Remove host port publishing in production, use private networks, add Redis auth if exposed internally. |

## High Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| SEC-006 | HIGH | Widget config allows any origin when allowed origins are unset. | `backend/app/widget/service.py` lines 96-107; portal creates key without origins in `backend/app/api/business_portal.py` lines 275-295 | A leaked public widget key can be used from any site. | Require allowed origins for production and add portal UI/API to manage them. |
| SEC-007 | HIGH | File ingestion lacks production upload controls. | `backend/app/api/business_portal.py` lines 122-156; `backend/app/rag/extraction.py` lines 6-18 | Oversized, malicious, or unsupported payloads are not handled safely. | Add multipart upload limits, MIME validation, scanning plan, storage isolation, and robust errors. |
| SEC-008 | HIGH | Prompt-injection defenses are absent. | `backend/app/chat/service.py` lines 207-223 | Tenant documents or visitors can influence AI behavior beyond intended context. | Add ingestion sanitization, prompt-injection detection, answer policy checks, and tests. |
| SEC-009 | HIGH | Real queue retry processing is missing. | `backend/app/workers/runner.py` lines 13-35 | Failed notifications/ingestions may not be retried without foreground request path. | Add queue consumer and scheduled retry processing. |
| SEC-010 | HIGH | Production secret validation is incomplete. | `backend/app/core/config.py` lines 128-150 | Backend validates session secrets/CORS/docs only; SMTP/AI/DB/Redis may still be unsafe. | Enforce required production settings for AI, email, DB password, Redis, and frontend API base. |
| SEC-011 | HIGH | DB does not enforce same-tenant parent/child relationships. | `backend/migrations/versions/20260522_0001_initial_tenant_schema.py`; `20260522_0002_document_chunks_vector.py` | Application bugs could attach child records to parents from other tenants. | Add composite constraints or service-level invariant checks with tests. |

## Medium Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| SEC-012 | MEDIUM | Tokens are stored in browser localStorage. | `frontend/lib/auth/session.ts`, `frontend/lib/auth/admin-session.ts` | XSS could steal tokens. | Harden frontend, consider HttpOnly secure cookies, CSP, short TTL and revocation. |
| SEC-013 | MEDIUM | Security headers are incomplete for production. | `backend/app/core/security.py`, `infra/nginx/default.conf` | No CSP/HSTS; frame policy may conflict with widget strategy if served same origin. | Add CSP, HSTS at TLS layer, explicit widget hosting policy. |
| SEC-014 | MEDIUM | Admin audit is tenant-scoped only. | `backend/app/models/usage.py`, `backend/app/api/admin.py` | Global admin actions may not fit cleanly. | Add global audit event model or nullable tenant audit strategy. |
| SEC-015 | MEDIUM | Dependency/security scanning is not in CI. | `.github/workflows/ci.yml` | Known vulnerabilities may be missed. | Add npm audit policy, pip-audit/Safety, secret scan, SAST. |

## Positive Findings

- Tenant-owned ORM mixin enforces required `tenant_id` at model level.
- Backend tests cover cross-portal token rejection and several tenant isolation paths.
- Production runtime rejects placeholder portal session secrets, wildcard CORS, and enabled API docs.
- API responses add `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy`.
- Admin support context avoids returning raw customer phone/name fields.
- AI provider secrets are kept in backend environment variables.

