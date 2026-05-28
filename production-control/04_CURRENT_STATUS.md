# Current Production Status

Last updated: 2026-05-28

## Read First

This is the quick-resume page for production remediation. Future Codex sessions should read this file before executing any `PR-*` phase.

## Current Active Phase

PR-05: Real Async Queue, Worker Reliability and Job Visibility.

Status: not_started. PR-01 through PR-04 are verified and PR-05 is the next permitted phase.

## Last Completed Phase

PR-04.

## Next Permitted Phase

`Implement production phase PR-05`

Do not start PR-06 or later until PR-05 is implemented or explicitly marked blocked with safe independent subtasks documented.

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
- PR-02 implemented app-level public/API rate limiting, CSRF confirmation for cookie-auth unsafe writes, CSP/security-header review, production widget-origin enforcement config, widget key lifecycle APIs, portal controls, and validation tests.
- PR-03 implemented same-tenant database integrity constraints, tenant offboarding/export/delete lifecycle APIs, global admin audit logs that survive tenant deletion, PII-redacted audit attributes, frontend admin lifecycle controls, and validation tests.
- PR-04 implemented a separate production Compose topology with private PostgreSQL/Redis networking, production Nginx TLS/HSTS templates, certificate renewal path, stronger production secret validation, encrypted backup/restore scripts, pgvector migration smoke script, CI security scans, and request/correlation ID logging.

## Unresolved Critical Risks

- No unresolved critical repository-controlled PR-04 blockers remain. Live VPS validation of TLS, firewall, backups, and restore is still required before launch gates can move.

## Unresolved High Risks

- Worker queue processing is a placeholder.
- Website/sitemap ingestion and secure document ingestion are missing.
- RAG retrieval is not scalable and lacks citations/safety evaluation.
- Monitoring, metering, quotas, and cost protection are incomplete.
- Billing/entitlement controls for paid beta are missing.
- First remote CI security scan run is pending on the pushed PR-04 branch.
- First VPS certificate issuance/renewal, backup/restore drill, and live PostgreSQL/pgvector smoke run are pending release-gate validation.

## Last Validation Commands

Latest PR-04 validation commands:

- `python3 -m pytest backend/tests/test_config.py backend/tests/test_health.py` - pass, 8 tests.
- `python3 -m pytest backend/tests` - pass, 59 tests.
- `python3 -m compileall backend/app backend/tests backend/migrations` - pass.
- `python3 -m ruff check backend/app backend/tests` - pass.
- `docker compose config` - pass.
- `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` - pass.
- Production compose port check for `postgres` and `redis` - pass, no published host ports.
- `sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh` - pass.
- `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr04_alembic_20260528.db python3 -m alembic -c backend/alembic.ini upgrade head` - pass.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
- `python3 -m json.tool production-control/status/production-status.json` - pass.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('production-control/visual/production-roadmap-status.svg'); print('svg ok')"` - pass.
- `git diff --check` - pass.
- Docker image build attempted but not run locally because Docker daemon was unavailable.

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
