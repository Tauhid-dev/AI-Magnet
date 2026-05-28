# Current Production Status

Last updated: 2026-05-28

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

PR-02: Public API Abuse Protection, Widget Origin Controls and API Security.

Status: not_started. PR-01 is verified and PR-02 is the next permitted phase.

## Last Completed Phase

PR-01.

## Next Permitted Phase

`Implement production phase PR-02`

Do not start PR-03 or later until PR-02 is implemented or explicitly marked blocked with safe independent subtasks documented.

## Production Go/No-Go

| Target | Current status |
|---|---|
| Gate A: Controlled Internal Demo, synthetic/sample data only | GO WITH CONDITIONS |
| Gate B: Secure Private Internet Demo | NO-GO until PR-01 through PR-05 verified |
| Gate C: Real Customer Pilot | NO-GO until PR-01 through PR-10 verified |
| Gate D: Paid Beta | NO-GO until PR-01 through PR-11 verified |
| Gate E: Public Production Launch | NO-GO until PR-12 final audit and explicit owner approval |

## Baseline

- Audit date: 2026-05-23.
- Production readiness score: 35/100.
- PR-01 implemented production password auth, admin MFA support, HttpOnly browser session cookies, session revocation, failed-login lockout, frontend login/logout updates, and validation tests.

## Unresolved Critical Risks

- Public endpoint rate limiting and abuse controls are missing.
- PostgreSQL must not publish host port 5432 in production.
- Redis must not publish host port 6379 in production and must be protected on private networking.
- Production HTTPS/TLS/HSTS and renewal path are missing.
- Scheduled encrypted backups and tested restore procedure are missing.

## Unresolved High Risks

- CSRF/CSP review and broader public API security hardening remain PR-02 work.
- Production secret validation is incomplete.
- Live PostgreSQL plus pgvector validation is missing.
- Tenant privacy lifecycle, export, delete, and offboarding are missing.
- Global administrator audit-event handling is incomplete.
- CI lacks dependency vulnerability, secret, and static security scanning.
- Structured logs, request/correlation IDs, and PII-safe logging controls are incomplete.
- Worker queue processing is a placeholder.
- Website/sitemap ingestion and secure document ingestion are missing.
- RAG retrieval is not scalable and lacks citations/safety evaluation.
- Monitoring, metering, quotas, and cost protection are incomplete.
- Billing/entitlement controls for paid beta are missing.

## Last Validation Commands

Latest PR-01 validation commands:

- `python3 -m pytest backend/tests` - pass, 48 tests.
- `python3 -m ruff check backend` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr01_alembic.db python3 -m alembic -c backend/alembic.ini upgrade head` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr01_alembic.db python3 -m alembic -c backend/alembic.ini downgrade base` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run lint` - pass.
- `npm run build` - pass.
- `python3 -m json.tool production-control/status/production-status.json` - pass.

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
