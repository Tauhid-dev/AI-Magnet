# PR-04: Production Infrastructure, TLS, Secrets, Backups and CI Security

Status: not_started

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

- [ ] Design production Compose topology.
- [ ] Remove public DB/Redis port exposure from production config.
- [ ] Add TLS/HSTS/cert renewal configuration and docs.
- [ ] Harden backend/frontend/container runtime where practical.
- [ ] Add production secret validation tests.
- [ ] Add backup and restore scripts/runbook.
- [ ] Add Postgres/pgvector migration validation path.
- [ ] Add CI dependency, secret, and SAST scans.
- [ ] Add request correlation ID and PII-safe logging baseline.
- [ ] Update status/risk/validation/visual artifacts.

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

To be filled during PR-04.

## Blockers

Requires PR-01 through PR-03 for secure internet exposure assumptions.

## Completion Criteria

A production topology is configured, documented, and statically validated; public data services are private by design; backup/restore and security scan paths exist.
