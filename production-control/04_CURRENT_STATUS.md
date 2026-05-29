# Current Production Status

Last updated: 2026-05-30

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

No product implementation phase is active. PR-13A repository remediation is complete at repository level.

Status: PR-13A closed the three PR-13 High repository findings for worker job claiming, rate-limit abuse analytics, and reproducible browser evidence. Public production launch remains NO-GO pending owner-approved live VPS/staging validation evidence and explicit launch approval.

## Last Completed Phase

PR-13A.

## Next Permitted Phase

The next recommended safe command is:

- `Implement external validation phase PR-14 using owner-approved VPS/staging environment and synthetic data only`

Do not perform live deployment, DNS/TLS changes, payment activation, production database migration, or real customer onboarding unless explicitly requested.

## Production Go/No-Go

| Target | Current status |
|---|---|
| Gate A: Controlled Internal Demo, synthetic/sample data only | GO WITH CONDITIONS |
| Gate B: Secure Private Internet Demo | CONDITIONAL. Repository High findings are closed, but live VPS smoke, remote CI evidence, target MFA/rate-limit smoke, and owner approval are still required |
| Gate C: Real Customer Pilot | NO-GO until PR-14 live VPS/staging smoke, alerting/log destination setup, controlled quota-limit smoke, backup/restore, worker/Redis, crawl/document/RAG smoke, and owner approval are recorded |
| Gate D: Paid Beta | NO-GO until PR-14 evidence, owner pricing/tax/refund approval, support readiness, remote CI, VPS/staging smoke, and explicit paid-beta approval are recorded |
| Gate E: Public Production Launch | NO-GO. Repository remediation is complete, but external VPS/staging evidence and explicit owner approval remain |

## Baseline

- Audit date: 2026-05-23.
- Production readiness score: 35/100.
- PR-01 implemented production password auth, admin MFA support, HttpOnly browser session cookies, session revocation, failed-login lockout, frontend login/logout updates, and validation tests.
- PR-02 implemented app-level public/API rate limiting, CSRF confirmation for cookie-auth unsafe writes, CSP/security-header review, production widget-origin enforcement config, widget key lifecycle APIs, portal controls, and validation tests.
- PR-03 implemented same-tenant database integrity constraints, tenant offboarding/export/delete lifecycle APIs, global admin audit logs that survive tenant deletion, PII-redacted audit attributes, frontend admin lifecycle controls, and validation tests.
- PR-04 implemented a separate production Compose topology with private PostgreSQL/Redis networking, production Nginx TLS/HSTS templates, certificate renewal path, stronger production secret validation, encrypted backup/restore scripts, pgvector migration smoke script, CI security scans, and request/correlation ID logging.
- PR-05 implemented a durable database-backed job ledger, Redis wake signals, worker heartbeats, retry/backoff/idempotency, failed-job visibility, tenant/admin job APIs, async document-ingestion jobs, async notification-delivery jobs, worker health checks, and validation tests.
- PR-06 implemented tenant-owned website/sitemap sources, SSRF-safe URL and redirect validation, bounded crawler settings, robots.txt handling, crawl page history, queued `rag.website_crawl` jobs, source metadata on generated knowledge documents, portal source controls, and validation tests.
- PR-07 implemented authenticated multipart document upload for text, Markdown, PDF, and DOCX; private tenant file storage; upload validation; deterministic basic malware screening; PDF/DOCX extraction; OCR-required gating for scanned PDFs; file-backed worker jobs without raw payloads; refresh/delete controls; portal file upload UX; and validation tests.
- PR-08 implemented PostgreSQL/pgvector SQL retrieval with tenant/status filters, retrieval indexes, bounded top-K/threshold behavior, no-answer fallback, source citations through the chat API and widget, prompt-injection safety flags for retrieved content and visitor prompts, and RAG evaluation fixtures.
- PR-09 implemented business profile setup, setup checklist/readiness UX, tenant knowledge/job status views, source-grounded agent sandbox with citations, widget title branding/copy controls, safer cookie-session hydration, leads/conversations loading/error states, and validation/browser smoke coverage.
- PR-10 implemented tenant usage metering, configurable quota/cost limits, graceful quota blocking, `/ready` readiness checks, estimated token/cost capture for chat and sandbox tests, admin/portal quota visibility, website crawl completion/failure usage events, and an operations monitoring/incident runbook.
- PR-11 implemented tenant-scoped manual paid-beta subscriptions, beta plan catalog, admin entitlement assignment controls, business billing/compliance visibility, subscription-aware quota enforcement, subscription export in privacy workflows, docs, and validation tests. Stripe/payment-provider automation remains deferred.
- PR-12 created the final validation package, release evidence checklist, VPS/staging validation runbook, rollback/restore runbook, final GO/NO-GO statement, and updated production-control launch-gate status. It did not perform live deployment.
- PR-12A corrected independent-review repository security gaps: production active `super_admin` accounts now require configured TOTP MFA, Redis-backed application rate limiting is required for production, and readiness reports admin MFA/rate-limit backend health.
- PR-13 performed the post-merge full repository audit, created `docs/production-audit/post-pr12a-final-audit/`, and found high remediation needs for worker concurrency-safe claiming, persisted rate-limit abuse analytics, and reproducible browser/e2e evidence.
- PR-13A implemented concurrency-safe job acquisition, persisted privacy-safe rate-limit abuse events, added Playwright mocked browser evidence for supported portal/admin flows, wired browser E2E into CI, and updated production-control status while keeping public launch NO-GO.

## Unresolved Critical Risks

- No unresolved critical repository-controlled implementation blocker is recorded after PR-13A.
- Public production launch is still a NO-GO because live VPS/staging validation, restore drill evidence, remote CI evidence for this branch, and explicit owner launch approval are not recorded.

## Unresolved High Risks

- PR-13A closed AUD-HIGH-001 in repository code/tests. Production PostgreSQL `FOR UPDATE SKIP LOCKED` job acquisition still needs owner-approved staging/VPS multi-worker smoke before horizontal scaling is trusted.
- PR-13A closed AUD-HIGH-002 in repository code/tests. Live Redis/rate-limit abuse analytics smoke remains PR-14 external evidence.
- PR-13A closed AUD-HIGH-003 with mocked Playwright browser tests. Live backend-integrated customer/admin/widget smoke remains PR-14 external evidence.
- Paid-beta live operation still requires owner approval for pricing, GST/tax handling, refund terms, support process, and manual invoicing acceptance.
- Scanned-document OCR runtime remains gated and not implemented; do not claim scanned-PDF OCR support.
- Remote CI evidence for the merged/audit branch is required.
- First VPS certificate issuance/renewal, backup/restore drill, worker/Redis smoke, controlled real-site crawl and document-upload smoke, live PostgreSQL/pgvector RAG smoke, `/ready` smoke, log/alert destination verification, and controlled quota-limit smoke run are pending release-gate validation.

## Last Validation Commands

Latest PR-13A validation commands:

- Focused worker concurrency tests: `backend/.venv/bin/python -m pytest backend/tests/workers/test_background_jobs.py -q` - pass, 11 tests.
- Focused rate-limit analytics tests: `backend/.venv/bin/python -m pytest backend/tests/security/test_rate_limit_backend.py backend/tests/analytics/test_usage_analytics.py backend/tests/business/test_business_portal_api.py backend/tests/chat/test_chat_api.py backend/tests/admin/test_admin_api.py -q` - pass, 44 tests.
- `backend/.venv/bin/python -m pytest backend/tests -q` - pass, 116 tests.
- `backend/.venv/bin/python -m ruff check backend/app backend/tests` - pass.
- `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations` - pass.
- SQLite Alembic upgrade/downgrade/upgrade smoke using `/private/tmp/ai_magnet_pr13a_alembic.sqlite` - pass.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
- `npm run test:e2e` - pass, 5 mocked Chromium browser tests.
- `docker compose config` - pass.
- `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` - pass.
- Production Compose JSON check for `postgres` and `redis` published ports - pass, no published ports.
- `backend/.venv/bin/python -m bandit -q -r backend/app` - pass.
- `backend/.venv/bin/python -m pip_audit -r backend/requirements.txt -r backend/requirements-dev.txt` - pass after sandbox escalation, no known Python vulnerabilities.
- Secret pattern scan - pass, no matches.
- `npm audit --audit-level=high` - pass after sandbox escalation at high threshold; moderate transitive PostCSS advisory through Next.js remains noted.
- `npx npm@10 ci` - pass after regenerating `frontend/package-lock.json` with npm 10 to include missing `@emnapi/runtime` and `@emnapi/core` entries for GitHub Actions.
- `python3 -m json.tool production-control/status/production-status.json` - pass.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('production-control/visual/production-roadmap-status.svg'); print('svg ok')"` - pass.
- `git diff --check` - pass.

## Important Links

- Roadmap: `production-control/02_MASTER_PRODUCTION_ROADMAP.md`
- Phase graph: `production-control/03_PHASE_DEPENDENCY_GRAPH.md`
- Decisions: `production-control/05_DECISIONS_LOG.md`
- Execution log: `production-control/06_EXECUTION_LOG.md`
- Risk register: `production-control/07_RISK_REGISTER.md`
- Validation matrix: `production-control/08_VALIDATION_MATRIX.md`
- Release gates: `production-control/09_RELEASE_GATES.md`
- Status JSON: `production-control/status/production-status.json`
- Visual dashboard: `production-control/visual/production-status-dashboard.html`
- Mermaid status: `production-control/visual/production-roadmap-status.mmd`
- SVG status: `production-control/visual/production-roadmap-status.svg`
