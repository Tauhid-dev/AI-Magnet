# Current Production Status

Last updated: 2026-05-29

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

No automatic production implementation phase is active.

Status: PR-12A repository security corrections are verified. Public production launch remains NO-GO pending owner-approved live validation evidence and explicit launch approval.

## Last Completed Phase

PR-12A.

## Next Permitted Phase

There is no next automatic PR implementation phase. The next safe commands are explicit owner-directed release actions, such as:

- `Run owner-approved staging validation`
- `Review PR-12A launch evidence`
- `Prepare production deployment plan`

Do not perform live deployment, DNS/TLS changes, payment activation, production database migration, or real customer onboarding unless explicitly requested.

## Production Go/No-Go

| Target | Current status |
|---|---|
| Gate A: Controlled Internal Demo, synthetic/sample data only | GO WITH CONDITIONS |
| Gate B: Secure Private Internet Demo | REPOSITORY READY WITH CONDITIONS after PR-05; live VPS smoke, remote CI evidence, and owner approval still required |
| Gate C: Real Customer Pilot | REPOSITORY READY WITH CONDITIONS after PR-10; live VPS/staging smoke, alerting/log destination setup, controlled quota-limit smoke, backup/restore, worker/Redis, crawl/document/RAG smoke, and owner approval still required |
| Gate D: Paid Beta | REPOSITORY READY WITH CONDITIONS after PR-11; owner pricing/tax/refund approval, support readiness, remote CI, VPS/staging smoke, and explicit paid-beta approval still required |
| Gate E: Public Production Launch | NO-GO. PR-12A repository security corrections are complete, but external VPS/staging evidence and explicit owner approval are still required |

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

## Unresolved Critical Risks

- No unresolved critical repository-controlled implementation blockers remain for PR-01 through PR-12A.
- Public production launch is still a NO-GO because live VPS/staging validation, restore drill evidence, remote CI evidence, and explicit owner launch approval are not recorded.

## Unresolved High Risks

- Paid-beta live operation still requires owner approval for pricing, GST/tax handling, refund terms, support process, and manual invoicing acceptance.
- Scanned-document OCR runtime remains gated and not implemented; do not claim scanned-PDF OCR support.
- First remote CI run for the pushed PR-12A branch is required.
- First VPS certificate issuance/renewal, backup/restore drill, worker/Redis smoke, controlled real-site crawl and document-upload smoke, live PostgreSQL/pgvector RAG smoke, `/ready` smoke, log/alert destination verification, and controlled quota-limit smoke run are pending release-gate validation.

## Last Validation Commands

Latest PR-12A validation commands:

- Focused mandatory production super-admin MFA tests - pass, 4 tests.
- Focused Redis-backed rate-limit tests - pass, 5 tests.
- `backend/.venv/bin/python -m pytest backend/tests` - pass, 106 tests.
- `backend/.venv/bin/python -m ruff check backend/app backend/tests` - pass.
- `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr12a_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini upgrade head` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr12a_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini downgrade 20260529_0011` - pass.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
- `docker compose config` - pass.
- `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` - pass.
- Production Compose JSON check for `postgres` and `redis` published ports - pass, no published ports.
- `sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh` - pass.
- `backend/.venv/bin/python -m bandit -q -r backend/app` - pass.
- `backend/.venv/bin/pip-audit -r backend/requirements.txt -r backend/requirements-dev.txt` - pass, no known Python vulnerabilities.
- Secret pattern scan - pass, no matches.
- `npm audit --audit-level=high` - pass at high threshold; moderate transitive PostCSS advisory through Next.js remains noted.
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
