# PR-04: Production Infrastructure, TLS, Secrets, Backups and CI Security

Status: verified

## Purpose

Create a secure deployable production topology for the OCI VPS environment without performing live deployment unless separately instructed.

## Why It Is Needed

Current Compose is development-oriented, publishes PostgreSQL and Redis to host ports, runs frontend dev server, lacks TLS/HSTS/certificate renewal, has incomplete production secret validation, lacks scheduled backups, and CI lacks security scans.

## Preconditions

- PR-01 through PR-03 are verified or explicitly documented as blocked.
- No live VPS deployment should be performed in this phase unless separately instructed.

## In-Scope Work

- Separate production Compose/configuration from development setup.
- Ensure PostgreSQL does not publish host port 5432 in production.
- Ensure Redis does not publish host port 6379 in production and is protected on private networking.
- Add Nginx HTTPS/TLS/HSTS configuration and certificate renewal path.
- Harden containers, users, health checks, restart policies, and runtime validation.
- Complete secret validation for session, database, Redis, AI provider, SMTP/email provider, and frontend/API configuration.
- Add scheduled encrypted backup and tested restore procedure/scripts.
- Add live PostgreSQL plus pgvector migration/startup/smoke-test validation path.
- Add dependency vulnerability scanning, secret scanning, and static security scanning in CI.
- Add minimum operational structured logs, request/correlation IDs, and PII-safe logging requirements.
- Update deployment/runbook and rollback plan.

## Out-Of-Scope Work

- Real VPS deployment, DNS changes, firewall changes, or live database migration unless explicitly requested.
- Full monitoring stack beyond minimum logging/correlation requirements; PR-10 completes monitoring.

## Source Areas Likely Affected

- `docker-compose.yml`
- `docker-compose.prod.yml` or equivalent
- `backend/Dockerfile`
- `infra/nginx/`
- `.github/workflows/ci.yml`
- `.env.example`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `docs/deployment.md`
- `docs/security.md`
- `backend/tests/`

## Detailed Tasks

- [x] Design production Compose topology.
- [x] Remove public DB/Redis port exposure from production config.
- [x] Add TLS/HSTS/cert renewal configuration and docs.
- [x] Harden backend/frontend/container runtime where practical.
- [x] Add production secret validation tests.
- [x] Add backup and restore scripts/runbook.
- [x] Add Postgres/pgvector migration validation path.
- [x] Add CI dependency, secret, and SAST scans.
- [x] Add request correlation ID and PII-safe logging baseline.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- `docker compose -f ... config`
- Backend config/security tests.
- CI workflow syntax/static validation.
- Backup/restore dry-run or documented VPS validation command.
- Production-equivalent Postgres/pgvector migration smoke command documented.

## Security Considerations

Never expose DB/Redis publicly in production config. Never commit secrets. TLS and backups are launch blockers.

## Migration And Rollback Notes

No application DB schema expected unless logging/config tables are added. Rollback production config changes by restoring previous config files.

## Evidence

- Production compose and private data networking: `docker-compose.prod.yml`, `.env.production.example`.
- Production Nginx TLS/HSTS and ACME templates: `infra/nginx/templates/prod.conf.template`, `infra/nginx/templates/bootstrap.conf.template`.
- Hardened containers: `backend/Dockerfile`, `frontend/Dockerfile`, `.dockerignore`.
- Secret/runtime validation and request IDs: `backend/app/core/config.py`, `backend/app/core/logging.py`, `backend/app/main.py`.
- Backup/restore/pgvector validation scripts: `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh`, `scripts/validate_pgvector_migrations.sh`.
- CI security scans and production compose checks: `.github/workflows/ci.yml`.
- Deployment/security/runbook docs: `docs/deployment.md`, `docs/security.md`, `docs/release-readiness.md`.
- Validation:
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
  - Docker image build attempted but not run locally because the Docker daemon was unavailable.

## Blockers

None for PR-04 static implementation. Gate B remains blocked until PR-05 is verified and the first remote CI/VPS validation confirms production image builds, certificate issuance/renewal, backup/restore, and pgvector migration smoke.

## Completion Criteria

A production topology is configured, documented, and statically validated; public data services are private by design; backup/restore and security scan paths exist.

Completion criteria met for repository-controlled PR-04 scope on 2026-05-28. Live deployment, DNS, firewall, certificate issuance, production database migration, and restore drills remain release-gate validation steps and were not executed.
