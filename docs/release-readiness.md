# Release Readiness Review

Last updated: 2026-05-29

## Production Remediation Status

The historical MVP Phase 0-10 work remains build evidence. Production remediation PR-01 through PR-12 is the current release-readiness track.

PR-01 through PR-11 are verified in repository-controlled code, tests, docs, and production-control status artifacts. PR-12 records the final validation package and launch gate. Public production launch remains NO-GO until owner-approved live evidence and explicit launch approval are recorded.

## Completed Repository Readiness Items

- Production authentication with password verification, admin MFA support, HttpOnly/SameSite browser sessions, revocation, lockout, and tests.
- Public/API abuse controls with rate limiting, widget origin enforcement, widget key lifecycle controls, CSRF confirmation, CSP/security headers, and tests.
- Same-tenant database integrity constraints, privacy export/delete/offboarding workflow, PII-redacted global admin audit logs, and tenant isolation tests.
- Separate production Compose topology with private PostgreSQL/Redis networking, Nginx TLS/HSTS templates, certificate renewal path, restart policies, health checks, and no public data-service ports.
- Production secret/config validation for sessions, database, Redis, AI, SMTP/email, frontend/API config, backups, cookies, and logging.
- Encrypted backup and restore scripts plus PostgreSQL/pgvector migration smoke path.
- CI checks for backend tests, Ruff, compile, Alembic, frontend lint/type/test/build, Compose config, dependency audit, npm audit, secret scan, and Bandit.
- Durable database-backed background job ledger, Redis wake signals, worker heartbeats, retry/backoff, failure visibility, and async document/notification jobs.
- Secure website/sitemap ingestion with SSRF-safe URL/redirect/DNS checks, robots handling, crawl limits, source history, and portal controls.
- Secure text/Markdown/PDF/DOCX document upload with private storage, file validation, PDF/DOCX extraction, gated scanned-PDF OCR status, refresh/delete controls, and tests.
- SQL pgvector retrieval path with tenant/status filters, bounded top-K/threshold behavior, source citations, no-answer fallback, prompt-injection safety handling, and RAG evaluation fixtures.
- Customer onboarding, knowledge setup, agent sandbox with citations, widget setup/branding/key controls, and portal UX states.
- Metering, quotas, estimated token/cost controls, readiness endpoint, admin/portal usage views, and operations runbook.
- Manual paid-beta entitlements, plan catalog, admin assignment controls, subscription-aware quota enforcement, portal billing visibility, and paid-beta documentation.
- PR-12 launch validation pack under `docs/production-launch/`.

## Checks Expected Before Merge

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests
backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations
backend/.venv/bin/python -m ruff check backend/app backend/tests
DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr12_alembic.db backend/.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
docker compose config
docker compose --env-file .env.production.example -f docker-compose.prod.yml config
sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh
cd frontend && npm run lint && npm run typecheck && npm test && npm run build
```

Security checks:

```bash
backend/.venv/bin/python -m bandit -q -r backend/app
backend/.venv/bin/pip-audit -r backend/requirements.txt -r backend/requirements-dev.txt
cd frontend && npm audit --audit-level=high
```

## Known Pre-Production Gaps

- Remote CI must pass for the final PR-12 branch before relying on it as release evidence.
- TLS certificate issuance and renewal commands are documented but not executed on the VPS in this repository pass.
- Encrypted backup scripts exist, but the first scheduled backup and restore drill must be run on staging/VPS before launch.
- Live PostgreSQL/pgvector migration and RAG smoke must be run on production-equivalent infrastructure before launch.
- Worker/Redis health, controlled crawl/document upload, quota-limit, alert/log destination, and `/ready` smoke must be run on the target host before real customer use.
- Owner approval for pricing, GST/tax handling, refund terms, support process, and explicit launch scope is still required.
- Scanned-document OCR runtime remains gated and must not be claimed as available until separately implemented and validated.

## Release Recommendation

Controlled internal demo remains GO WITH CONDITIONS. Secure private demo, real customer pilot, and paid beta are repository-ready with conditions. Public production launch remains NO-GO until the PR-12 external evidence checklist is complete and the owner explicitly approves launch.
