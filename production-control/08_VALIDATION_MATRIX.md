# Validation Matrix

Last updated: 2026-05-30

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
| Real queue worker and job visibility | PR-05/PR-13A | required | required | required if schema changes | required if UI | required | required | manual worker smoke | pass | job enqueue/process/retry/failure/idempotency tests, job APIs, worker health check config, atomic claim/concurrency tests |
| Website/sitemap ingestion SSRF safety | PR-06 | required | required | required | required | required | required | staging safe crawl | pass | malicious URL tests, redirect/private DNS tests, crawl status, source UI, and migration smoke pass; controlled real-site crawl remains release-gate evidence |
| Document/PDF/DOCX/OCR ingestion safety | PR-07 | required | required | required | required | required | required | manual upload test | pass | upload validation, DOCX/PDF extraction/OCR gate tests, tenant API refresh/delete tests, private storage and worker tests |
| SQL pgvector retrieval/citations/RAG safety | PR-08 | required | required | required | required if UI | required | required | staging RAG eval | pass | SQL retrieval path, citation/schema/widget tests, RAG safety fixtures, SQLite migration smoke; production-equivalent pgvector smoke remains release-gate evidence |
| Onboarding/agent/widget UX | PR-09/PR-13A | optional | required | optional | required | required | required | browser smoke | pass | backend API tests, frontend static/type/lint/build, committed Playwright mocked browser tests |
| Monitoring/metering/quotas/cost controls | PR-10/PR-13A | required | required | optional | required if UI | required | required | manual alert/limit checks | pass | quota/metering/readiness tests, persisted rate-limit abuse analytics, admin/portal UI checks, operations runbook |
| Billing/entitlements/paid-beta controls | PR-11 | required | required | required | required | required | required | manual paid-beta review | pass | manual entitlement model/API/UI tests, quota enforcement tests, migration smoke, and paid-beta gate record |
| Final production launch audit | PR-12 | required | required | required | required | required | required | required | partial | repository final validation package exists; local repository checks pass when recorded below; owner-approved VPS/staging evidence and launch approval remain required |
| Final repository security corrections before staging | PR-12A | required | required | optional | optional | required | required | staging MFA/Redis smoke | pass | mandatory production admin MFA tests, Redis rate-limiter tests, readiness/config checks, full validation suite |

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
| Atomic job claim and concurrent worker distribution | pass | PR-13A `backend/tests/workers/test_background_jobs.py` - 11 focused tests passed |
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

## PR-07 Validation

| Check | Status | Evidence |
|---|---|---|
| Upload validation rejects unsupported, malformed, oversized, malicious, and unsafe-name files | pass | `backend/tests/rag/test_secure_document_ingestion.py` |
| DOCX extraction and PDF OCR gating | pass | `backend/tests/rag/test_secure_document_ingestion.py`; `backend/app/rag/extraction.py` |
| Private file storage path stays under configured root | pass | `backend/app/rag/document_storage.py`; storage-backed worker/API tests |
| File-backed worker avoids raw document bytes in job payload | pass | `backend/tests/rag/test_secure_document_ingestion.py` |
| Tenant-scoped upload, refresh, delete API controls | pass | `backend/tests/rag/test_secure_document_ingestion.py` |
| Backend focused PR-07 tests | pass | `backend/.venv/bin/python -m pytest backend/tests/rag/test_secure_document_ingestion.py backend/tests/rag/test_chunking_and_extraction.py backend/tests/rag/test_ingestion_and_retrieval.py backend/tests/workers/test_background_jobs.py backend/tests/business/test_business_portal_api.py` - 25 passed |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 81 passed |
| Backend compile | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations` |
| Backend lint | pass | `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | SQLite upgrade head and downgrade to `20260528_0009` |
| Compose static config | pass | `docker compose config`; `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Dependency and static security scans | pass | `pip-audit`; `bandit`; secret pattern scan; `npm audit --audit-level=high` passed high threshold with moderate Next.js/PostCSS advisory noted |
| OCR runtime | partial | Scanned PDFs fail closed with `ocr_status=required`; production OCR engine remains gated and not claimed in PR-07 |
| Controlled customer-document upload smoke | not_run | Repository phase does not upload real customer documents; run before real pilot usage |

## PR-08 Validation

| Check | Status | Evidence |
|---|---|---|
| SQL pgvector retrieval path with tenant/status filters | pass | `backend/app/rag/retrieval.py`; `backend/migrations/versions/20260529_0011_pr08_pgvector_retrieval_indexes.py` |
| Retrieval citations and source provenance | pass | `backend/tests/rag/test_ingestion_and_retrieval.py`; chat API citation response tests |
| No-answer fallback and threshold behavior | pass | `backend/tests/rag/test_ingestion_and_retrieval.py`; `backend/tests/rag/test_rag_safety_eval.py` |
| Prompt-injection handling for retrieved content and visitor prompts | pass | `backend/app/rag/safety.py`; `backend/tests/rag/test_rag_safety_eval.py` |
| Wrong-tenant retrieval protection | pass | `backend/tests/rag/test_rag_safety_eval.py`; existing chat tenant isolation tests |
| Usage metering seam for latency/token/citation metadata | pass | `backend/tests/rag/test_rag_safety_eval.py`; `backend/app/chat/service.py` |
| Widget citation display | pass | `widget/chat-widget.js`; backend response fixture coverage |
| Backend focused PR-08 tests | pass | `backend/.venv/bin/python -m pytest backend/tests/rag/test_ingestion_and_retrieval.py backend/tests/rag/test_rag_safety_eval.py backend/tests/chat/test_chat_api.py` - 15 passed |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 87 passed |
| Backend compile | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations` |
| Backend lint | pass | `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | SQLite upgrade head and downgrade to `20260529_0010` |
| Compose static config | pass | `docker compose config`; `docker compose --env-file .env.production.example -f docker-compose.prod.yml config`; production data-service port check |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Dependency and static security scans | pass | `pip-audit`; `bandit`; secret pattern scan; `npm audit --audit-level=high` passed high threshold with moderate Next.js/PostCSS advisory noted |
| Production-equivalent PostgreSQL/pgvector smoke | not_run | Repository phase does not run live/staging PostgreSQL; run before Gate C using `scripts/validate_pgvector_migrations.sh` and controlled tenant RAG smoke |

## PR-09 Validation

| Check | Status | Evidence |
|---|---|---|
| Business profile onboarding API and safe website URL validation | pass | `backend/tests/business/test_business_portal_api.py`; `backend/app/api/business_portal.py` |
| Source-grounded agent sandbox with tenant citations and no conversation persistence | pass | `backend/tests/business/test_business_portal_api.py`; `backend/app/api/business_portal.py` |
| Widget branding/title API and embed snippet update | pass | `backend/tests/business/test_business_portal_api.py`; `frontend/app/portal/widget/page.tsx` |
| Setup checklist and business profile UX | pass | `frontend/app/portal/onboarding/page.tsx`; `frontend/tests/static-check.mjs` |
| Knowledge setup job visibility | pass | `frontend/app/portal/documents/page.tsx`; `frontend/tests/static-check.mjs` |
| Agent test UX with source display | pass | `frontend/app/portal/agent/page.tsx`; `frontend/tests/static-check.mjs` |
| Leads/conversations loading and error states | pass | `frontend/app/portal/leads/page.tsx`; `frontend/app/portal/conversations/page.tsx` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Backend focused PR-09 tests | pass | `backend/.venv/bin/python -m pytest backend/tests/business/test_business_portal_api.py` - 12 passed |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 89 passed |
| Backend lint | pass | `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Authenticated browser smoke | pass | Local FastAPI + Next.js with temp SQLite tenant confirmed login, setup checklist, agent sandbox sources, and widget branding save |
| Live customer onboarding smoke | not_run | Repository phase does not onboard a real customer; run during Gate C release validation |

## PR-10 Validation

| Check | Status | Evidence |
|---|---|---|
| Tenant quota snapshots and usage metering | pass | `backend/app/usage/quotas.py`; `backend/tests/usage/test_quota_service.py` |
| Chat and agent token/cost capture | pass | `backend/app/chat/service.py`; `backend/app/api/business_portal.py`; focused quota/chat tests |
| Graceful quota enforcement | pass | HTTP 429 quota tests for widget chat start and quota event recording |
| Readiness endpoint and correlation baseline | pass | `backend/app/api/health.py`; `backend/tests/test_health.py` |
| Admin and portal quota/cost visibility | pass | `backend/app/analytics/service.py`; `frontend/app/admin/usage/page.tsx`; `frontend/app/portal/analytics/page.tsx` |
| Operations monitoring and incident runbook | pass | `docs/operations-monitoring.md` |
| Backend focused PR-10 tests | pass | `backend/.venv/bin/python -m pytest backend/tests/usage/test_quota_service.py backend/tests/chat/test_chat_api.py backend/tests/test_health.py` - 12 passed |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 93 passed |
| Backend lint | pass | `backend/.venv/bin/ruff check backend/app backend/tests` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Live logging/alert destination smoke | not_run | Repository phase does not configure hosted alerting; required before Gate C pilot |
| Controlled quota-limit/VPS `/ready` smoke | not_run | Repository phase does not deploy to VPS; required before Gate C pilot |

## PR-11 Validation

| Check | Status | Evidence |
|---|---|---|
| Manual paid-beta plan catalog and tenant subscription model | pass | `backend/app/billing/service.py`; `backend/app/models/billing.py`; `backend/migrations/versions/20260529_0012_pr11_billing_entitlements.py` |
| Admin subscription assignment and audit events | pass | `backend/app/api/admin.py`; `backend/tests/admin/test_admin_api.py` |
| Business portal billing/compliance visibility | pass | `backend/app/api/business_portal.py`; `frontend/app/portal/billing/page.tsx`; `backend/tests/business/test_business_portal_api.py` |
| Server-side entitlement and quota enforcement | pass | `backend/app/usage/quotas.py`; `backend/tests/usage/test_quota_service.py`; paused subscription document block test |
| Privacy/export/delete/offboarding alignment | pass | `backend/app/admin/service.py`; `docs/paid-beta-readiness.md`; subscription export is included in tenant privacy export |
| Backend focused PR-11 tests | pass | `backend/.venv/bin/python -m pytest backend/tests/usage/test_quota_service.py backend/tests/admin/test_admin_api.py backend/tests/business/test_business_portal_api.py` - 26 passed |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 97 passed |
| Backend compile/lint | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations`; `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Migration upgrade/downgrade | pass | SQLite upgrade head and downgrade to `20260529_0011` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Dependency and static security scans | pass | `pip-audit` found no known Python vulnerabilities; Bandit passed; `npm audit --audit-level=high` passed high threshold with moderate transitive PostCSS advisory noted |
| Paid-beta live operations review | partial | Repository controls are verified; owner approval, pricing/tax/refund confirmation, remote CI, VPS/staging smoke, and support readiness remain Gate D conditions |

## PR-12 Validation

| Check | Status | Evidence |
|---|---|---|
| Final validation report and launch-gate pack | pass | `docs/production-launch/final-production-validation-report.md`; `docs/production-launch/final-go-no-go-statement.md`; `docs/production-launch/release-evidence-checklist.md` |
| VPS/staging validation and rollback/restore runbooks | pass | `docs/production-launch/vps-staging-validation-runbook.md`; `docs/production-launch/rollback-and-restore-runbook.md` |
| Backend full test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 97 passed |
| Backend compile/lint | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations`; `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Migration upgrade/downgrade smoke | pass | SQLite upgrade head and downgrade to `20260529_0011` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Compose static config | pass | `docker compose config`; `docker compose --env-file .env.production.example -f docker-compose.prod.yml config` |
| Production data-service port check | pass | Production Compose JSON check confirmed `postgres` and `redis` have no published host ports |
| Backup/restore/pgvector script syntax | pass | `sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh` |
| Dependency and static security scans | pass | `pip-audit` found no known Python vulnerabilities; Bandit passed; secret pattern scan had no matches; `npm audit --audit-level=high` passed with moderate transitive PostCSS advisory noted |
| Production-control status and visuals | pass | `python3 -m json.tool production-control/status/production-status.json`; SVG parse check; `git diff --check` |
| Live VPS/staging validation, restore drill, load/abuse, and owner approval | not_run | Documented in `docs/production-launch/release-evidence-checklist.md`; not executed without explicit owner approval |

## PR-12A Validation

| Check | Status | Evidence |
|---|---|---|
| Production super-admin without MFA is blocked | pass | `backend/tests/admin/test_admin_api.py` focused PR-12A tests |
| Production super-admin with missing/invalid MFA is blocked and valid MFA succeeds | pass | `backend/tests/admin/test_admin_api.py` focused PR-12A tests |
| Local/test admin MFA behaviour is explicitly non-production | pass | `backend/tests/admin/test_admin_api.py` local-dev MFA test |
| Redis-backed limiter selection, rejection headers, shared count, and fail-closed Redis outage | pass | `backend/tests/security/test_rate_limit_backend.py` |
| Readiness/config visibility for admin MFA and rate-limit backend | pass | `backend/app/api/health.py`, `backend/app/core/config.py`, focused/full tests |
| Full backend test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 106 passed |
| Backend compile/lint | pass | `backend/.venv/bin/python -m compileall backend/app backend/tests backend/migrations`; `backend/.venv/bin/python -m ruff check backend/app backend/tests` |
| Alembic migration smoke | pass | SQLite upgrade head and downgrade to `20260529_0011` using `/private/tmp/ai_magnet_pr12a_alembic.db` |
| Frontend lint/typecheck/test/build | pass | `npm run lint`; `npm run typecheck`; `npm test`; `npm run build` |
| Compose/security/status checks | pass | Dev/prod Compose config, production data-service port check, script syntax, Bandit, pip-audit, secret pattern scan, npm audit high-threshold, status JSON parse, SVG parse, and `git diff --check` |
| Live VPS/staging MFA and Redis rate-limit smoke | not_run | Required before launch-gate change; not executed without explicit owner approval |

## PR-13 Validation

| Check | Status | Evidence |
|---|---|---|
| Default branch baseline established | pass | `master` updated to `d390f4dfa7853bb06cd6fd6558a820bdf696f122`; PR-12 and PR-12A merge commits visible locally |
| GitHub PR/CI metadata | not_verified | `gh` is unavailable in this environment; remote PR/CI status must be verified externally |
| Full backend test suite | pass | `backend/.venv/bin/python -m pytest backend/tests` - 106 passed |
| Focused production super-admin MFA tests | pass | 4 focused tests in `backend/tests/admin/test_admin_api.py` passed |
| Focused Redis-backed rate-limit tests | pass | `backend/tests/security/test_rate_limit_backend.py` - 5 passed |
| Focused tenant integrity test | pass | `backend/tests/security/test_pr03_tenant_integrity.py` - 1 passed |
| Focused ingestion, worker, RAG, chat tests | pass | 38 focused tests passed |
| Backend compile/lint | pass | `compileall` and Ruff passed |
| Alembic upgrade/downgrade/upgrade smoke | pass | SQLite smoke using `/private/tmp/ai_magnet_pr13_alembic_20260530.db` passed |
| Frontend lint/typecheck/static test/build | pass | `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build` passed |
| Compose and production data-service port validation | pass | Dev/prod Compose rendered; production JSON check confirmed no PostgreSQL/Redis published ports |
| Backup/restore/pgvector script syntax | pass | `sh -n scripts/backup_postgres.sh scripts/restore_postgres.sh scripts/validate_pgvector_migrations.sh` passed |
| Security scans | pass_with_warning | Bandit passed; pip-audit found no Python vulnerabilities; secret pattern scan had no matches; npm audit passed high threshold with moderate PostCSS advisory noted |
| Production-control artifact syntax | pass | Status JSON parsed; SVG parsed; phase/status consistency checked |
| Worker multi-process atomic claim proof | closed_pr13a | PR-13 finding AUD-HIGH-001; closed by PR-13A repository implementation and tests |
| Persisted rate-limit abuse analytics | closed_pr13a | PR-13 finding AUD-HIGH-002; closed by PR-13A repository implementation and tests |
| Reproducible browser/e2e evidence | closed_pr13a | PR-13 finding AUD-HIGH-003; closed by PR-13A mocked Playwright browser tests |
| External VPS/staging launch evidence | not_run | Required in PR-14 with owner approval |

## PR-13A Validation

| Check | Status | Evidence |
|---|---|---|
| Baseline/default branch verification | pass | `master` pulled to `32b74ee87a41c1a7d924763af85fb4abae562d07`; PR-13 merge commit visible; PR-12/PR-12A history retained |
| Worker atomic claim implementation | pass | `backend/app/jobs/service.py` uses atomic `UPDATE ... RETURNING`; PostgreSQL candidate query uses `FOR UPDATE SKIP LOCKED` |
| Worker concurrency/retry/recovery tests | pass | `backend/.venv/bin/python -m pytest backend/tests/workers/test_background_jobs.py -q` - 11 passed |
| PostgreSQL job claim SQL compile | pass | SQLAlchemy PostgreSQL dialect compile confirms `UPDATE ... SELECT ... FOR UPDATE SKIP LOCKED ... RETURNING`; live PostgreSQL execution remains PR-14 evidence |
| PostgreSQL-specific multi-worker live proof | external_pending | SQL shape is implemented, but local test DB is SQLite; PR-14 must run staging PostgreSQL multi-worker smoke |
| Rate-limit exceed event persistence | pass | `backend/app/core/rate_limit.py`, `backend/app/usage/service.py`; denied requests persist safe tenant/global events before returning 429 |
| Rate-limit analytics and privacy tests | pass | Focused rate-limit/admin/business/chat/analytics/security tests - 44 passed |
| Browser E2E framework | pass | Playwright committed in `frontend/playwright.config.ts` and `frontend/e2e/*` |
| Browser E2E execution | pass | `npm run test:e2e` - 5 mocked Chromium tests passed |
| Live backend-integrated browser proof | external_pending | Mocked API browser coverage is repository evidence only; PR-14 must run target-environment smoke |
| CI browser wiring | pass_pending_remote | `.github/workflows/ci.yml` installs Playwright Chromium and runs `npm run test:e2e`; remote CI result pending after push |
| Full backend regression | pass | `backend/.venv/bin/python -m pytest backend/tests -q` - 116 passed |
| Backend lint/compile | pass | Ruff passed; compileall passed |
| Alembic smoke | pass | SQLite upgrade/downgrade/upgrade using `/private/tmp/ai_magnet_pr13a_alembic.sqlite` passed |
| Frontend lint/typecheck/static/build | pass | `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` passed |
| Compose and data-service port checks | pass | Dev/prod Compose rendered; production JSON check confirmed PostgreSQL/Redis publish no host ports |
| Security scans | pass_with_warning | Bandit passed; pip-audit found no Python vulnerabilities; secret pattern scan no matches; npm audit high threshold passed with moderate PostCSS advisory noted |
| Production-control visual/status consistency | pass | `python3 -m json.tool production-control/status/production-status.json`; SVG parse check; dashboard/status grep review; `git diff --check` passed after final memory updates |
