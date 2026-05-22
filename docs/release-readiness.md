# MVP Release Readiness Review

## Phase 9 Status

Phase 9 prepares the MVP for reliable development and first deployment review. It does not add premium modules or production billing/voice/SMS features.

## Completed Readiness Items

- CI workflow added for backend tests, Ruff linting, Alembic migration validation, frontend lint/type/test/build, and Docker Compose config validation.
- Docker Compose includes backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx.
- Nginx reverse proxy config added with `/api` backend routing and frontend fallback routing.
- Production runtime guardrails added for unsafe session secrets, wildcard CORS, and enabled API docs.
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
cd frontend && npm run lint && npm run typecheck && npm test && npm run build
```

If Ruff is unavailable locally, install backend dev dependencies in a virtual environment:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
backend/.venv/bin/python -m ruff check backend/app backend/tests
```

## Known Pre-Production Gaps

- Authentication remains MVP email/session based and needs production-grade login before public launch.
- Rate limiting is not implemented.
- TLS certificate automation is not included.
- Automated backups are documented but not scheduled.
- Worker service is wired for deployment but does not process a queue yet.
- Live PostgreSQL migration validation should be run in the target environment.

## Release Recommendation

Use this state for continued MVP review and controlled local/staging deployment. Do not treat it as public production-ready until auth hardening, rate limiting, TLS, backups, and live-environment migration checks are complete.
