# Missing Items Checklist

Repository root: `/Users/thuda/Desktop/Resources/Personal/Projects/AI-Magnet`

## Critical Missing Items

| Item | Status | Severity | Evidence | Required fix |
|---|---|---|---|---|
| Production-grade business auth | MISSING | CRITICAL | `backend/app/business/auth.py` logs in by tenant slug and email only | Add verified magic link/password/IdP, session revocation, MFA option, audit. |
| Production-grade admin auth | MISSING | CRITICAL | `backend/app/admin/auth.py` logs in by email only | Add MFA/IdP/passwordless verification and admin session controls. |
| Rate limiting | MISSING | CRITICAL | `docs/security.md` lists no rate limiting; no middleware found | Add per-IP/per-tenant limits for login, widget, chat, ingestion, admin. |
| Website crawling | MISSING | HIGH | No crawler module/routes | Add controlled crawler with allowlist, robots policy, SSRF protection, crawl limits. |
| Sitemap ingestion | MISSING | HIGH | No sitemap parser | Add sitemap fetch/parse/import workflow with tenant scoping. |
| Browser-based crawling | MISSING | MEDIUM | No Playwright/browser crawler | Add only if product requires JS-heavy website ingestion. |
| OCR/PDF/DOCX support | MISSING | HIGH | `backend/app/rag/extraction.py` rejects non-text types | Add safe extractors, scan/limits, tests. |
| Source citations | MISSING | HIGH | Chat response contains assistant text only | Return document/chunk/source metadata in chat response and UI. |
| Streaming chat | MISSING | MEDIUM | Chat API is synchronous POST response | Add SSE/WebSocket streaming if required by UX. |
| Real worker queue | MISSING | HIGH | `backend/app/workers/runner.py` sleeps only | Add Celery/RQ/async worker processing ingestion/notification jobs. |
| Redis queue usage | MISSING | MEDIUM | Redis exists in Compose but no job code uses it | Connect queue framework or remove dependency until used. |
| TLS automation | MISSING | CRITICAL | `infra/nginx/default.conf` listens on port 80 only | Add HTTPS config, HSTS, cert renewal. |
| Automated backups | MISSING | CRITICAL | `docs/deployment.md` has manual backup command only | Add scheduled encrypted backups and restore tests. |
| Public website/SEO | MISSING | LOW/MEDIUM | `frontend/app/page.tsx` redirects to `/portal` | Add public marketing/SEO pages if GTM requires them. |
| Billing implementation | MISSING | HIGH for paid launch | `docs/future-modules/billing.md` is planning only | Add plans, entitlements, Stripe integration, webhooks, quotas. |
| Quotas and cost controls | MISSING | HIGH | Usage logs exist, no enforcement | Add per-tenant budgets, token accounting, ingestion limits. |
| Widget origin management UI | MISSING | HIGH | `WidgetService` supports origins but portal creates unrestricted config | Add configure/revoke/rotate allowed origins in portal. |
| Production file upload protection | MISSING | HIGH | Portal sends JSON text, no upload security controls | Add size/type/content scanning, object storage, malware plan. |
| Prompt injection defenses | MISSING | HIGH | No document/query sanitizer or policy filter found | Add ingestion prompt-injection checks and answer guardrails. |
| Monitoring/alerting | MISSING | HIGH | Basic health only | Add metrics, logs, traces, alerts, dashboards. |

## Partially Implemented Items Needing Improvement

| Item | Current state | Improvement needed |
|---|---|---|
| Tenant isolation | App-level filters and tests exist | Add DB-level parent/child tenant consistency constraints and broader tests. |
| RAG vector search | pgvector column/index exists | Query through pgvector with tenant filter, thresholds, and pagination. |
| AI provider abstraction | OpenAI-compatible and deterministic providers exist | Add retries, streaming, usage capture, provider router, fallback/local provider. |
| Email notifications | DB delivery records and SMTP provider exist | Move delivery/retry to worker, add settings UI, delivery webhooks/bounce tracking. |
| Analytics | Transactional aggregate snapshots exist | Add retention, rollups, cache/materialized views, billing-safe event pipeline. |
| DevOps | Compose and CI exist | Add production Compose/manifests, image builds, deploy pipeline, security scans. |
| UX | Main portal/admin pages exist | Add onboarding, validation, mobile/accessibility testing, empty/error states. |
| Documentation | Good planning docs exist | Add incident response, operational runbooks, restore procedure verification. |

## Explicitly Non-MVP But Requested In Audit

These are missing because the original project docs treated them as future scope or did not include them in MVP:

- Voice AI runtime.
- SMS and WhatsApp runtime.
- Stripe billing runtime.
- Full marketplace.
- Mobile app.
- Advanced CRM.
- AI phone calling.
- Multi-region infrastructure.
- n8n automation runtime.
- Local Ollama runtime provider.

