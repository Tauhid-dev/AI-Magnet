# Current Production Status

Last updated: 2026-05-29

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

PR-09: Customer Onboarding, Agent Testing and Widget Installation Experience.

Status: not_started. PR-01 through PR-08 are verified and PR-09 is the next permitted phase.

## Last Completed Phase

PR-08.

## Next Permitted Phase

`Implement production phase PR-09`

Do not start PR-10 or later unless explicitly requested. PR-09 depends on PR-08 and is now the next ordered production remediation phase.

## Production Go/No-Go

| Target | Current status |
|---|---|
| Gate A: Controlled Internal Demo, synthetic/sample data only | GO WITH CONDITIONS |
| Gate B: Secure Private Internet Demo | REPOSITORY READY WITH CONDITIONS after PR-05; live VPS smoke, remote CI evidence, and owner approval still required |
| Gate C: Real Customer Pilot | NO-GO until PR-01 through PR-10 verified |
| Gate D: Paid Beta | NO-GO until PR-01 through PR-11 verified |
| Gate E: Public Production Launch | NO-GO until PR-12 final audit and explicit owner approval |

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

## Unresolved Critical Risks

- No unresolved critical repository-controlled PR-08 blockers remain. Live VPS validation of TLS, firewall, backups, restore, worker health, Redis reachability, controlled real-site crawl smoke, controlled document-upload smoke, and production-equivalent PostgreSQL/pgvector RAG smoke is still required before broader operation.

## Unresolved High Risks

- Customer onboarding, knowledge setup, agent testing, and widget installation UX are not yet beta-complete.
- Monitoring, metering, quotas, and cost protection are incomplete.
- Billing/entitlement controls for paid beta are missing.
- Scanned-document OCR runtime remains gated and not implemented.
- First remote CI run for the pushed PR-08 branch will be required.
- First VPS certificate issuance/renewal, backup/restore drill, worker/Redis smoke, controlled real-site crawl and document-upload smoke, and live PostgreSQL/pgvector RAG smoke run are pending release-gate validation.

## Last Validation Commands

Latest PR-08 validation commands:

- `backend/.venv/bin/python -m ruff check backend/app backend/tests` - pass.
- `backend/.venv/bin/python -m pytest backend/tests/rag/test_ingestion_and_retrieval.py backend/tests/rag/test_rag_safety_eval.py backend/tests/chat/test_chat_api.py` - pass, 15 tests.
- `backend/.venv/bin/python -m pytest backend/tests` - pass, 87 tests.
- `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr08_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini upgrade head` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr08_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini downgrade 20260529_0010` - pass.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
- `docker compose config` - pass.
- `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` - pass.
- Production compose port check for `postgres` and `redis` - pass, no published host ports.
- `backend/.venv/bin/pip-audit -r backend/requirements.txt -r backend/requirements-dev.txt` - pass.
- `backend/.venv/bin/python -m bandit -q -r backend/app` - pass.
- Secret pattern scan - pass, no matches.
- `npm audit --audit-level=high` - pass for high severity; npm reported moderate transitive PostCSS advisories through Next.js.
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
