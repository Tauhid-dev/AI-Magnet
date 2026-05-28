# Risk Register

Last updated: 2026-05-28

| Risk ID | Severity | Description | Evidence | Affected phase | Mitigation | Residual risk | Status |
|---|---|---|---|---|---|---|---|
| R-001 | CRITICAL | Business authentication is email-only and does not verify mailbox ownership | `backend/app/business/auth.py` | PR-01 | Implemented password verification, lockout, HttpOnly cookie session, logout revocation, and tests | Password reset/self-service onboarding UX remains future work | resolved_pr01 |
| R-002 | CRITICAL | Super admin authentication is email-only | `backend/app/admin/auth.py` | PR-01 | Implemented password verification, TOTP MFA enforcement support, lockout, logout revocation, and tests | MFA enrollment/rotation UI remains future work | resolved_pr01 |
| R-003 | HIGH | Browser session/token strategy stores sensitive tokens client-side | `frontend/lib/auth/session.ts`, `frontend/lib/auth/admin-session.ts` | PR-01 | Frontend no longer stores bearer tokens; browser sessions use HttpOnly/SameSite cookies | CSRF/CSP/security-header review remains PR-02 | mitigated_pr01 |
| R-004 | CRITICAL | Public endpoint rate limiting and abuse controls are missing | `docs/security.md`, no rate-limit middleware/config found | PR-02 | Add app/proxy rate limits, abuse logs, tests | Brute force, spam, AI cost abuse | open |
| R-005 | HIGH | Widget keys can be unrestricted by origin | `backend/app/widget/service.py`, `backend/app/api/business_portal.py` | PR-02 | Require allowed origins in production, add rotate/revoke/domain controls | Widget abuse from unauthorized origins | open |
| R-006 | HIGH | Tenant parent/child DB consistency is not enforced | migrations and models lack composite same-tenant constraints | PR-03 | Add constraints/checks/tests for documents/chunks/messages/leads/usage/notifications | Cross-tenant data linkage bug risk | open |
| R-007 | HIGH | Privacy lifecycle, export, delete, retention, and offboarding are missing | Audit checklist and no workflow found | PR-03 | Implement lifecycle model, APIs, docs, tests | Privacy/compliance gaps | open |
| R-008 | HIGH | Global admin audit model is incomplete | Tenant-scoped audit logs only | PR-03 | Add global or nullable-tenant audit strategy | Admin actions may be unaudited | open |
| R-009 | CRITICAL | PostgreSQL publishes host port 5432 in current Compose | `docker-compose.yml` | PR-04 | Create production topology with private DB networking | Public DB exposure if deployed incorrectly | open |
| R-010 | CRITICAL | Redis publishes host port 6379 in current Compose and lacks production protection | `docker-compose.yml` | PR-04 | Private Redis networking, auth/protection if needed | Public Redis exposure if deployed incorrectly | open |
| R-011 | CRITICAL | HTTPS/TLS/HSTS and certificate renewal are missing | `infra/nginx/default.conf`, `docs/deployment.md` | PR-04 | Add production Nginx TLS/HSTS/renewal path | PII/session exposure in transit | open |
| R-012 | CRITICAL | Scheduled encrypted backups and tested restore procedure are missing | `docs/deployment.md` manual command only | PR-04 | Add backup scripts/docs/tests/runbook | Data loss risk | open |
| R-013 | HIGH | Production secret validation is incomplete | `backend/app/core/config.py` | PR-04 | Validate DB, Redis, AI, SMTP/email, frontend/API production config | Misconfigured production startup | open |
| R-014 | HIGH | Live PostgreSQL plus pgvector migration/startup validation is missing | Audit notes and CI only use SQLite migration | PR-04 | Add production-equivalent Postgres/pgvector validation | Schema mismatch at launch | open |
| R-015 | HIGH | CI lacks dependency vulnerability, secret, and static security scanning | `.github/workflows/ci.yml` | PR-04 | Add pip/npm audit, secret scan, SAST | Known vulnerable dependency risk | open |
| R-016 | HIGH | Structured logs, request/correlation IDs, and PII-safe logging are incomplete | Basic logging only | PR-04/PR-10 | Add correlation middleware, structured log policy, PII redaction checks | Incident response blind spots | open |
| R-017 | HIGH | Worker queue processing is placeholder only | `backend/app/workers/runner.py` sleeps | PR-05 | Implement real queue with retries/job visibility | Lost/slow ingestion and notification workflows | open |
| R-018 | HIGH | Website/sitemap ingestion is missing | No crawler/sitemap module found | PR-06 | Implement safe crawler with SSRF/domain/crawl limits | Product-defining workflow missing | open |
| R-019 | HIGH | Document/PDF/DOCX/OCR ingestion is missing | `backend/app/rag/extraction.py` supports text/Markdown only | PR-07 | Add safe upload, extraction, storage, delete/refresh | Real customer docs cannot be safely processed | open |
| R-020 | HIGH | RAG retrieval is not scalable and lacks citations/safety evals | `backend/app/rag/retrieval.py`, chat API response | PR-08 | Use SQL pgvector tenant query, citations, thresholds, prompt-injection tests | Incorrect or ungrounded answers | open |
| R-021 | HIGH | Onboarding and agent testing UX is incomplete | Portal pages exist but no production flow | PR-09 | Add onboarding, knowledge setup, sandbox, widget domain/key UX | Manual setup blocks beta | open |
| R-022 | HIGH | Monitoring, metering, quotas, and cost controls are incomplete | Usage logs only | PR-10 | Add metrics, quotas, cost accounting, alerts | Provider cost abuse and blind ops | open |
| R-023 | HIGH | Billing/entitlements are missing for paid beta | Future-module docs only | PR-11 | Add entitlements/manual or provider billing controls | Paid usage cannot be safely managed | open |
| R-024 | CONDITIONAL | Browser/Playwright crawling may be needed for JS-heavy sites | No browser crawler found | PR-06 optional | Implement only if ordinary crawler fails target sites | Some sites may ingest poorly | deferred_conditional |
| R-025 | CONDITIONAL | Streaming chat is missing | Sync chat POST response only | PR-09/PR-12 optional | Add only if beta UX requires it | Lower perceived responsiveness | deferred_conditional |
| R-026 | CONDITIONAL | Public SEO/marketing pages are missing | Root redirects to portal | Deferred | Growth-track work | No direct production security impact | deferred |
| R-027 | DEFERRED | Voice, SMS/WhatsApp, marketplace, mobile, advanced CRM, multi-region, n8n, Ollama runtime are not implemented | Future-module docs only | Deferred | Keep out of remediation unless explicitly requested | Scope creep | deferred |
| R-028 | HIGH | Incident-response and restore runbook validation are missing | No validated incident response or restore drill evidence found | PR-04/PR-10 | Add incident and restore runbooks, smoke tests, and validation evidence | Recovery uncertainty during outage/data loss | open |
