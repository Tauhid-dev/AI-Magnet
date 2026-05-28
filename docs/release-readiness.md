# Release Readiness Review

## Production Remediation Status

The historical MVP Phase 9 prepared the development deployment path. Production remediation PR-01 through PR-04 now add authentication hardening, abuse controls, tenant/privacy integrity, and a production infrastructure path. PR-05 is still required before Gate B can move.

## Completed Readiness Items

- CI workflow added for backend tests, Ruff linting, Alembic migration validation, frontend lint/type/test/build, and Docker Compose config validation.
- Docker Compose includes backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx.
- Nginx reverse proxy config added with `/api` backend routing and frontend fallback routing.
- Production runtime guardrails added for unsafe session secrets, wildcard CORS, enabled API docs, insecure cookies, placeholder database/Redis/AI/SMTP/backup configuration, and non-JSON production logging.
- Production compose added with no public PostgreSQL or Redis host ports.
- Production Nginx TLS/HSTS template and Let's Encrypt renewal path added.
- Encrypted backup and restore scripts added.
- PostgreSQL/pgvector migration smoke validation path added.
- CI security scans added for Python dependency audit, npm audit, secret pattern scan, and backend SAST.
- Request/correlation ID logging baseline added.
- Security headers added to API responses.
- Security-focused backend tests added for production config, response headers, cross-portal token rejection, and tenant-scoped analytics.
- Deployment guide added for OCI VPS-style single-host deployment.
- Security checklist added for tenant isolation, auth boundaries, PII handling, AI/RAG privacy, and residual risks.

## Checks Expected Before Merge

Run:

```bash
python3 -m pytest backend/tests
python3 -m compileall backend/app backend/tests backend/migrations
python3 -m ruff check backend/app backend/tests
docker compose config
docker compose --env-file .env.production.example -f docker-compose.prod.yml config
sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh
cd frontend && npm run lint && npm run typecheck && npm test && npm run build
```

If Ruff is unavailable locally, install backend dev dependencies in a virtual environment:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
backend/.venv/bin/python -m ruff check backend/app backend/tests
```

## Known Pre-Production Gaps

- Gate B remains blocked until PR-05 implements a real queue/worker and job visibility.
- TLS certificate issuance and renewal commands are documented but not executed on the VPS yet.
- Encrypted backup scripts exist, but the first scheduled backup and restore drill must be run on staging/VPS before launch.
- Live PostgreSQL/pgvector migration validation script exists, but must be run on production-equivalent infrastructure before launch.
- CI security scans must pass on the remote branch before relying on them as release evidence.
- Worker service is still deployment wiring and does not process a real queue yet.

## Release Recommendation

Use this state for continued controlled internal review. Do not treat it as secure private internet demo ready until PR-05 is verified and the PR-04 VPS validation commands have been run successfully.
