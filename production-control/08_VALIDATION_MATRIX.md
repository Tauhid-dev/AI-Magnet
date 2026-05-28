# Validation Matrix

Last updated: 2026-05-28

Status values: `pass`, `fail`, `not_run`, `partial`, `blocked`.

| Requirement | Phase | Unit | Integration/API | Migration/DB | Frontend/E2E | Security | CI/static | VPS/staging/manual | Current status | Evidence model |
|---|---|---|---|---|---|---|---|---|---|---|
| Verified business/admin auth | PR-01 | required | required | required if schema changes | required | required | required | manual smoke | pass | backend tests, frontend build, migration upgrade/downgrade |
| Secure cookie/token/CSRF/CSP session strategy | PR-01/PR-02 | required | required | optional | required | required | required | manual browser | partial | cookie/token storage tests pass; CSRF/CSP review remains PR-02 |
| Rate limiting and abuse controls | PR-02 | required | required | optional | optional | required | required | manual curl/abuse checks | not_run | tests and config evidence |
| Widget origin/key controls | PR-02 | required | required | optional | required | required | required | manual embed test | not_run | positive/negative origin tests |
| Tenant DB integrity | PR-03 | required | required | required | optional | required | required | staging migration | not_run | migration and cross-tenant attack tests |
| Privacy export/delete/offboarding | PR-03 | required | required | required | required if UI | required | required | manual lifecycle test | not_run | deletion/export fixtures |
| Global admin audit events | PR-03 | required | required | required if schema changes | required if UI | required | required | manual audit review | not_run | audit trail tests |
| Production private DB/Redis topology | PR-04 | optional | optional | optional | optional | required | required | required | not_run | compose config, port scan, runbook |
| TLS/HSTS/renewal path | PR-04 | optional | optional | optional | optional | required | required | required | not_run | Nginx config, certbot/renewal docs, header check |
| Secret validation | PR-04 | required | required | optional | optional | required | required | manual env smoke | not_run | production startup failure tests |
| Scheduled encrypted backups and restore | PR-04 | optional | optional | required | optional | required | required | required | not_run | backup artifact and restore drill |
| Live PostgreSQL plus pgvector validation | PR-04 | optional | optional | required | optional | optional | required | required | not_run | migration and vector query smoke |
| Dependency/secret/SAST CI scans | PR-04 | optional | optional | optional | optional | required | required | optional | not_run | CI job logs |
| Structured logs/correlation IDs/PII-safe logging | PR-04/PR-10 | required | required | optional | optional | required | required | manual log review | not_run | tests and sample logs |
| Real queue worker and job visibility | PR-05 | required | required | required if schema changes | required if UI | required | required | manual worker smoke | not_run | job enqueue/process/retry tests |
| Website/sitemap ingestion SSRF safety | PR-06 | required | required | required | required | required | required | staging safe crawl | not_run | malicious URL tests and crawl status |
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
