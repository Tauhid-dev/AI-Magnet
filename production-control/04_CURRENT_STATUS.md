# Current Production Status

Last updated: 2026-05-29

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

PR-11: Billing, Compliance Controls and Paid Beta Readiness.

Status: not_started. PR-01 through PR-10 are verified and PR-11 is the next permitted phase.

## Last Completed Phase

PR-10.

## Next Permitted Phase

`Implement production phase PR-11`

Do not start PR-12 unless explicitly requested. PR-11 depends on PR-10 and is now the next ordered production remediation phase.

## Production Go/No-Go

| Target | Current status |
|---|---|
| Gate A: Controlled Internal Demo, synthetic/sample data only | GO WITH CONDITIONS |
| Gate B: Secure Private Internet Demo | REPOSITORY READY WITH CONDITIONS after PR-05; live VPS smoke, remote CI evidence, and owner approval still required |
| Gate C: Real Customer Pilot | REPOSITORY READY WITH CONDITIONS after PR-10; live VPS/staging smoke, alerting/log destination setup, controlled quota-limit smoke, backup/restore, worker/Redis, crawl/document/RAG smoke, and owner approval still required |
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
- PR-09 implemented business profile setup, setup checklist/readiness UX, tenant knowledge/job status views, source-grounded agent sandbox with citations, widget title branding/copy controls, safer cookie-session hydration, leads/conversations loading/error states, and validation/browser smoke coverage.
- PR-10 implemented tenant usage metering, configurable quota/cost limits, graceful quota blocking, `/ready` readiness checks, estimated token/cost capture for chat and sandbox tests, admin/portal quota visibility, website crawl completion/failure usage events, and an operations monitoring/incident runbook.

## Unresolved Critical Risks

- No unresolved critical repository-controlled PR-10 blockers remain. Live VPS validation of TLS, firewall, backups, restore, worker health, Redis reachability, controlled real-site crawl smoke, controlled document-upload smoke, production-equivalent PostgreSQL/pgvector RAG smoke, log/alert destination setup, and quota-limit smoke is still required before broader operation.

## Unresolved High Risks

- Billing/entitlement controls for paid beta are missing.
- Scanned-document OCR runtime remains gated and not implemented.
- First remote CI run for the pushed PR-10 branch will be required.
- First VPS certificate issuance/renewal, backup/restore drill, worker/Redis smoke, controlled real-site crawl and document-upload smoke, live PostgreSQL/pgvector RAG smoke, `/ready` smoke, log/alert destination verification, and controlled quota-limit smoke run are pending release-gate validation.

## Last Validation Commands

Latest PR-10 validation commands:

- `backend/.venv/bin/python -m pytest backend/tests/usage/test_quota_service.py backend/tests/chat/test_chat_api.py backend/tests/test_health.py` - pass, 12 tests.
- `backend/.venv/bin/ruff check backend/app backend/tests` - pass.
- `backend/.venv/bin/python -m pytest backend/tests` - pass, 93 tests.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
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
