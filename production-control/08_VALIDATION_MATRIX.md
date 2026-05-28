# Validation Matrix

Last updated: 2026-05-28

Status values: `pass`, `fail`, `not_run`, `partial`, `blocked`.

| Requirement | Phase | Unit | Integration/API | Migration/DB | Frontend/E2E | Security | CI/static | VPS/staging/manual | Current status | Evidence model |
|---|---|---|---|---|---|---|---|---|---|---|
| Verified business/admin auth | PR-01 | required | required | required if schema changes | required | required | required | manual smoke | pass | backend tests, frontend build, migration upgrade/downgrade |
| Secure cookie/token/CSRF/CSP session strategy | PR-01/PR-02 | required | required | optional | required | required | required | manual browser | pass | HttpOnly cookie sessions, CSRF confirmation header tests, CSP/security headers |
| Rate limiting and abuse controls | PR-02 | required | required | optional | optional | required | required | manual curl/abuse checks | pass | App-level limiter tests and production env validation |
| Widget origin/key controls | PR-02 | required | required | optional | required | required | required | manual embed test | pass | Positive/negative origin tests and lifecycle API tests |
| Tenant DB integrity | PR-03 | required | required | required | optional | required | required | staging migration | pass | migration and cross-tenant attack tests |
| Privacy export/delete/offboarding | PR-03 | required | required | required | required if UI | required | required | manual lifecycle test | pass | deletion/export fixtures and admin API/frontend controls |
| Global admin audit events | PR-03 | required | required | required if schema changes | required if UI | required | required | manual audit review | pass | audit trail tests |
| Production private DB/Redis topology | PR-04 | optional | optional | optional | optional | required | required | required | pass | production compose config, no published DB/Redis ports, runbook |
| TLS/HSTS/renewal path | PR-04 | optional | optional | optional | optional | required | required | required | pass | Nginx TLS/HSTS templates, bootstrap template, certbot/renewal docs |
| Secret validation | PR-04 | required | required | optional | optional | required | required | manual env smoke | pass | production startup failure/acceptance tests |
| Scheduled encrypted backups and restore | PR-04 | optional | optional | required | optional | required | required | required | partial | scripts and restore runbook exist; first VPS restore drill pending |
| Live PostgreSQL plus pgvector validation | PR-04 | optional | optional | required | optional | optional | required | required | partial | validation script exists; first staging/VPS run pending |
| Dependency/secret/SAST CI scans | PR-04 | optional | optional | optional | optional | required | required | optional | partial | CI jobs added; first remote run pending |
| Structured logs/correlation IDs/PII-safe logging | PR-04/PR-10 | required | required | optional | optional | required | required | manual log review | partial | request/correlation baseline tests pass; PR-10 owns full monitoring/log review |
| Real queue worker and job visibility | PR-05 | required | required | required if schema changes | required if UI | required | required | manual worker smoke | pass | job enqueue/process/retry/failure/idempotency tests, job APIs, worker health check config |
| Website/sitemap ingestion SSRF safety | PR-06 | required | required | required | required | required | required | staging safe crawl | pass | malicious URL tests, redirect/private DNS tests, crawl status, source UI, and migration smoke pass; controlled real-site crawl remains release-gate evidence |
| Document/PDF/DOCX/OCR ingestion safety | PR-07 | required | required | required | required | required | required | manual upload test | not_run | file fixtures and deletion tests |
| SQL pgvector retrieval/citations/RAG safety | PR-08 | required | required | required | required if UI | required | required | staging RAG eval | not_run | eval fixtures and source checks |
| Onboarding/agent/widget UX | PR-09 | optional | required | optional | required | required | required | browser smoke | not_run | e2e tests and UX checklist |
| Monitoring/metering/quotas/cost controls | PR-10 | required | required | required | required if UI | required | required | manual alert/limit checks | not_run | metrics and quota tests |
| Billing/entitlements/paid-beta controls | PR-11 | required | required | required | required | required | required | manual paid-beta review | not_run | entitlement tests and gate record |
| Final production launch audit | PR-12 | required | required | required | required | required | required | required | not_run | final audit report and owner approval |

## PR-00 Validation

| Check | Status | Evidence |
|---|---|---|
| Production status JSON valid | pass | `python3 -m json.tool production-control/status/production-status.json` |
| Markdown/SVG/HTML artifacts created | pass | `production-control/` file inventory includes memory, status, phase, and visual artifacts |
| Whitespace diff clean | pass | `git diff --check` |
| Product runtime unchanged | pass | PR-00 changes are limited to `AGENTS.md` and `production-control/**` |

## PR-01 Validation

| Check | Status | Evidence |
|---|---|---|
| Business/admin email-only login removed | pass | Login schemas require password; email-only tests return 422 |
| Business password auth, logout, revocation, lockout | pass | `backend/tests/business/test_business_portal_api.py` |
| Admin password auth, TOTP MFA path, logout, revocation, lockout | pass | `backend/tests/admin/test_admin_api.py` |
| Cross-portal token boundaries preserved | pass | `backend/tests/security/test_security_boundaries.py` |
| Migration upgrade/downgrade | pass | Alembic SQLite upgrade head and downgrade base |
| Backend full test suite | pass | `python3 -m pytest backend/tests` - 48 passed |
| Backend lint | pass | `python3 -m ruff check backend` |
| Frontend typecheck/lint/test/build | pass | `npm run typecheck`, `npm test`, `npm run lint`, `npm run build` |

## PR-02 Validation

| Check | Status | Evidence |
|---|---|---|
| Business/admin login and public endpoint rate limiting | pass | `backend/app/core/rate_limit.py`; business login/widget init tests |
| Widget origin enforcement | pass | `backend/tests/chat/test_chat_api.py` positive/negative origin coverage |
| Widget key lifecycle controls | pass | `backend/tests/business/test_business_portal_api.py` create/update origins/rotate/disable/revoke coverage |
| Cookie-auth CSRF confirmation and CSP headers | pass | `backend/tests/business/test_business_portal_api.py`; `backend/tests/security/test_security_boundaries.py` |
| Backend full test suite | pass | `python3 -m pytest backend/tests` - 54 passed |
| Backend lint | pass | `python3 -m ruff check backend/app backend/tests` |
| Frontend typecheck/lint/test/build | pass | `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` |
| Migration/DB changes | pass | No schema migration required for PR-02 |

## PR-03 Validation

| Check | Status | Evidence |
|---|---|---|
| Same-tenant database constraints reject cross-tenant links | pass | `backend/tests/security/test_pr03_tenant_integrity.py` |
| Privacy export/offboard/delete APIs and global audit | pass | `backend/tests/admin/test_admin_api.py` |
| Backend full test suite | pass | `python3 -m pytest backend/tests` - 56 passed |
| Backend lint | pass | `python3 -m ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | Alembic SQLite upgrade head and downgrade to `20260528_0006` |
| Frontend typecheck/lint/test/build | pass | `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` |

## PR-04 Validation

| Check | Status | Evidence |
|---|---|---|
| Production secret/config validation | pass | `python3 -m pytest backend/tests/test_config.py backend/tests/test_health.py` - 8 passed |
| Backend full test suite | pass | `python3 -m pytest backend/tests` - 59 passed |
| Backend compile/lint | pass | `python3 -m compileall backend/app backend/tests backend/migrations`; `python3 -m ruff check backend/app backend/tests` |
| Development compose static config | pass | `docker compose config` |
| Production compose static config | pass | `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` |
| Production DB/Redis no published ports | pass | Generated production compose checked for no `published:` ports under `postgres` or `redis` |
| Backup/restore/pgvector script syntax | pass | `sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh` |
| SQLite migration smoke | pass | `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr04_alembic_20260528.db python3 -m alembic -c backend/alembic.ini upgrade head` |
| Frontend typecheck/lint/test/build | pass | `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` |
| Docker image build | not_run | Attempted locally, but Docker daemon was unavailable |
| Live VPS cert/backup/restore/pgvector smoke | not_run | Documented for release-gate execution; not executed in PR-04 |

## PR-05 Validation

| Check | Status | Evidence |
|---|---|---|
| Durable job model and migration | pass | `backend/app/models/job.py`; `backend/migrations/versions/20260528_0008_pr05_background_jobs.py` |
| Document ingestion job success and payload redaction | pass | `backend/tests/workers/test_background_jobs.py` |
| Retry/backoff/idempotency/failure visibility | pass | `backend/tests/workers/test_background_jobs.py` |
| Notification delivery job processing and usage logging | pass | `backend/tests/workers/test_background_jobs.py` |
| Tenant/admin job visibility APIs | pass | `backend/tests/business/test_business_portal_api.py`; `backend/tests/admin/test_admin_api.py` |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 63 passed |
| Backend compile/lint | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations`; `backend/.venv/bin/ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | SQLite upgrade head and downgrade to `20260528_0007` |
| Compose worker healthcheck config | pass | `docker compose config`; `docker compose --env-file .env.production.example -f docker-compose.prod.yml config`; production data-services port check |
| Production-control status and visuals | pass | `python3 -m json.tool production-control/status/production-status.json`; SVG parse check; `git diff --check` |
| Live VPS worker/Redis smoke | not_run | Repository phase does not deploy to VPS; run before Gate B operation |

## PR-06 Validation

| Check | Status | Evidence |
|---|---|---|
| URL, DNS, local/private IP, metadata, and protocol rejection | pass | `backend/tests/rag/test_website_ingestion.py` |
| Redirect-to-private-target rejection | pass | `backend/tests/rag/test_website_ingestion.py` |
| Website source crawl creates tenant documents and crawl history | pass | `backend/tests/rag/test_website_ingestion.py` |
| Sitemap source filters to approved domain | pass | `backend/tests/rag/test_website_ingestion.py` |
| Business-domain source authorization | pass | `backend/tests/rag/test_website_ingestion.py` |
| Portal source API queues tenant crawl job | pass | `backend/tests/rag/test_website_ingestion.py` |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 76 passed |
| Backend compile/lint | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations`; `backend/.venv/bin/ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | SQLite upgrade head and downgrade to `20260528_0008` |
| Frontend typecheck/lint/test/build | pass | `npm run typecheck`; `npm run lint`; `npm test`; `npm run build` |
| Compose static config | pass | `docker compose config`; `docker compose --env-file .env.production.example -f docker-compose.prod.yml config`; production data-service port check |
| Dependency and static security scans | pass | `backend/.venv/bin/pip-audit -r backend/requirements.txt -r backend/requirements-dev.txt`; `backend/.venv/bin/python -m bandit -q -r backend/app`; secret pattern scan; `npm audit --audit-level=high` passed high threshold with a moderate transitive PostCSS advisory noted |
| Production-control status and visuals | pass | `python3 -m json.tool production-control/status/production-status.json`; SVG parse check; `git diff --check` |
| Controlled real-site crawl smoke | not_run | Repository phase does not crawl live customer sites; run before real pilot usage |
