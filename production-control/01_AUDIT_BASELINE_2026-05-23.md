# Audit Baseline 2026-05-23

Last updated: 2026-05-28

## Baseline Source

Primary audit pack:

- `docs/audit/2026-05-23-end-to-end/master-audit-report.md`
- `docs/audit/2026-05-23-end-to-end/audit-summary.json`
- `docs/audit/2026-05-23-end-to-end/security-findings.md`
- `docs/audit/2026-05-23-end-to-end/production-readiness-checklist.md`
- `docs/audit/2026-05-23-end-to-end/missing-items-checklist.md`

## Historical Scores

| Area | Score |
|---|---:|
| Repository health | 72/100 |
| Architecture quality | 68/100 |
| Security | 42/100 |
| Scalability | 38/100 |
| SaaS readiness | 58/100 |
| Production readiness | 35/100 |
| RAG quality | 47/100 |
| UX quality | 50/100 |
| DevOps maturity | 52/100 |
| Overall project completion | 68/100 |
| MVP readiness | 63/100 |
| Enterprise readiness | 20/100 |

## Historical Go/No-Go

| Target | Baseline judgement |
|---|---|
| Internal MVP demo | GO WITH CONDITIONS |
| MVP public launch | NO-GO |
| Paid beta | NO-GO |
| Real customer onboarding | NO-GO |
| Production deployment | NO-GO |
| Enterprise usage | NO-GO |

## Current Verification Snapshot

This PR-00 run inspected current code and config enough to classify the audit blockers. It did not implement remediation.

| Finding | Audit status | Current verification | PR phase |
|---|---|---|---|
| Business auth is email-only | Critical open | Resolved in PR-01: business login now requires password verification, failed-login lockout, session version, logout revocation, and tests | PR-01 |
| Admin auth is email-only | Critical open | Resolved in PR-01: admin login now requires password verification and supports required TOTP MFA, lockout, session revocation, and tests | PR-01 |
| Secure browser session strategy missing | High open | Resolved across PR-01/PR-02: frontend no longer stores bearer tokens, browser sessions use HttpOnly cookies, unsafe cookie-auth writes require CSRF confirmation, and CSP is set | PR-01/PR-02 |
| Rate limiting missing | Critical open | Mitigated in PR-02: app-level rate limits cover public/login/widget/admin surfaces; distributed/proxy enforcement remains PR-04/PR-05 | PR-02 |
| Widget origin controls incomplete | High open | Mitigated in PR-02: normalized allowed-origin enforcement and key lifecycle controls were added; production env enforcement remains PR-04 validation | PR-02 |
| Tenant DB integrity incomplete | High open | Resolved in PR-03: composite same-tenant constraints and attack tests cover high-risk parent/child links | PR-03 |
| Privacy export/delete/offboarding missing | High open | Resolved in PR-03 for beta-scope admin workflows: export, offboarding, retention, and confirmed deletion APIs/UI were added | PR-03 |
| Global admin audit handling incomplete | High open | Resolved in PR-03: `global_audit_logs` records platform admin actions and deletion-surviving evidence with redacted attributes | PR-03 |
| PostgreSQL host port exposed in dev Compose | Critical production blocker | Resolved for production in PR-04: `docker-compose.prod.yml` keeps PostgreSQL internal with no published host port; dev compose remains local-only | PR-04 |
| Redis host port exposed in dev Compose | Critical production blocker | Resolved for production in PR-04: `docker-compose.prod.yml` keeps Redis internal with no published host port; dev compose remains local-only | PR-04 |
| HTTPS/TLS/HSTS missing | Critical open | Mitigated in PR-04: production Nginx TLS/HSTS and ACME renewal path added; first live certificate issuance remains release evidence | PR-04 |
| Scheduled encrypted backups and restore test missing | Critical open | Mitigated in PR-04: encrypted backup/restore scripts and restore drill runbook added; first VPS restore drill remains release evidence | PR-04 |
| Production secret validation incomplete | High open | Resolved in PR-04: production validation covers sessions, secure cookies, DB, Redis, AI, SMTP, public URL, frontend API path, JSON logs, and backup passphrase | PR-04 |
| Live PostgreSQL/pgvector validation missing | High open | Mitigated in PR-04: production-equivalent pgvector migration smoke script added; first staging/VPS run remains release evidence | PR-04 |
| Dependency/security scans missing | High open | Mitigated in PR-04: CI security job added for pip-audit, npm audit, secret pattern scan, and Bandit; first remote run pending | PR-04 |
| Structured logs/correlation IDs/PII-safe logging incomplete | High open | Mitigated in PR-04: request/correlation ID middleware and JSON production logs added; full monitoring/log review remains PR-10 | PR-04/PR-10 |
| Worker queue is placeholder | High open | Still open: `backend/app/workers/runner.py` sleeps and does not consume jobs | PR-05 |
| Website/sitemap ingestion missing | High open | Still open: no crawler/sitemap ingestion module or UI found | PR-06 |
| Browser crawler missing | Conditional | Deferred/conditional: implement only if ordinary crawler cannot support required sites | PR-06 optional |
| PDF/DOCX/OCR ingestion missing | High open | Still open: `backend/app/rag/extraction.py` supports text/Markdown only | PR-07 |
| RAG retrieval not scalable | High open | Still open: `backend/app/rag/retrieval.py` scores tenant chunks in Python | PR-08 |
| RAG citations/safety/evals missing | High open | Still open: chat responses do not expose source citations or RAG eval suite | PR-08 |
| Onboarding/agent test/widget setup UX incomplete | High open | Still open: portal pages exist, but no full production onboarding or agent sandbox workflow | PR-09 |
| Monitoring/metering/quotas/cost controls missing | High open | Still open: usage logs exist but no quotas, cost accounting, alerts, or full monitoring | PR-10 |
| Incident-response and restore runbook validation missing | High open | Still open: no validated incident response, restore drill, or operational recovery runbook evidence found | PR-04/PR-10 |
| Billing/entitlements missing | High for paid beta | Still open: future-module docs only | PR-11 |
| Streaming chat missing | Conditional | Deferred/conditional UX enhancement unless chosen for beta | PR-09/PR-12 optional |
| Public SEO/marketing site missing | Conditional | Deferred growth-track work, not a production-security blocker | Deferred |
| Voice/SMS/WhatsApp/marketplace/mobile/CRM/multi-region/n8n/Ollama | Deferred | Still deferred unless explicitly requested | Deferred |

## Baseline Interpretation

The original MVP Phase 0-10 roadmap remains useful historical build evidence. It must not be used as proof that production remediation is complete. The `PR-*` roadmap created in `production-control/` is the source of truth for production readiness from 2026-05-28 forward.

## Checklist Reconciliation Notes

- Items that appeared only in the missing-items checklist but are security or production blockers were elevated into PR-01, PR-02, PR-03, PR-04, or PR-05 instead of being treated as optional backlog.
- The production readiness checklist and security findings override optimistic feature-completion claims where code/config evidence is weak or missing.
- Browser/Playwright crawling, streaming chat, and public SEO/marketing pages are conditional or growth-track items, not mandatory production-security blockers.
- Premium modules remain deferred: voice AI, SMS/WhatsApp, marketplace, mobile apps, advanced CRM, multi-region, n8n runtime, and local Ollama runtime.
