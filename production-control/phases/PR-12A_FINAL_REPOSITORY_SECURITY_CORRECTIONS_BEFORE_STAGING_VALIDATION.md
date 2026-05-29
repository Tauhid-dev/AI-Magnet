# PR-12A: Final Repository Security Corrections Before Staging Validation

Status: verified

## Purpose

Correct repository-level security gaps found by independent review after PR-12 and before owner-approved staging/VPS validation.

## Why It Is Needed

PR-12 created the final launch-gate package, but independent review found two repository-controlled issues that should not be deferred to staging:

- Production super-admin MFA was conditional on `admin.mfa_required`, allowing a production `super_admin` with MFA disabled to log in.
- Application-level rate limits were per-process in memory, which does not coordinate across backend instances and resets on restart.

## Preconditions

- PR-12 branch exists and is pushed.
- No live deployment, DNS/TLS, payment, or customer onboarding permission is assumed.

## In-Scope Work

- Enforce mandatory configured TOTP MFA for active production `super_admin` accounts.
- Preserve explicit local/test non-production MFA ergonomics.
- Add Redis-backed application-level rate limiting for production-sensitive scopes.
- Keep in-memory rate limiting only for explicitly configured local/test/development mode.
- Fail closed when Redis rate limiting is selected but unavailable.
- Add readiness visibility for rate-limit backend and production super-admin MFA state.
- Update docs, production-control memory/status/risk/validation/visual artifacts.

## Out-Of-Scope Work

- Live VPS/staging deployment.
- DNS, TLS issuance, firewall changes, payment activation, or real customer onboarding.
- Public production GO.
- Admin MFA enrollment/rotation UI.

## Source Areas Affected

- `backend/app/admin/auth.py`
- `backend/app/core/rate_limit.py`
- `backend/app/core/config.py`
- `backend/app/api/health.py`
- `backend/tests/admin/`
- `backend/tests/security/`
- `docker-compose*.yml`
- `.env*.example`
- docs and production-control files

## Detailed Tasks

- [x] Inspect admin auth, admin models, API routes, tests, config, and local seed logic.
- [x] Enforce production super-admin MFA even when `admin.mfa_required` is false.
- [x] Reject production super-admin login/session validation when MFA is disabled or no valid MFA secret is configured.
- [x] Keep local/test behaviour explicit and non-production only.
- [x] Inspect current rate limiter, Redis dependency, Nginx config, API usage, settings, and tests.
- [x] Add Redis-backed app limiter with production config enforcement.
- [x] Keep in-memory limiter only when explicitly configured for local/dev/test.
- [x] Fail closed with HTTP 503 when Redis limiter is required but unavailable.
- [x] Add readiness visibility for rate limiting and admin MFA state.
- [x] Update stale auth docs and production-control memory.
- [x] Run focused and full validation checks.

## Tests And Validation Required

- Focused production admin MFA tests.
- Focused Redis rate-limiter selection, rejection, headers, and failure-mode tests.
- Full backend tests.
- Backend lint and compile.
- Alembic migration smoke.
- Frontend lint, typecheck, tests, and build.
- Dev/prod Compose config rendering.
- Security scans used in PR-12.
- JSON/SVG/dashboard consistency checks.
- `git diff --check`.

## Evidence

- Mandatory production admin MFA: `backend/app/admin/auth.py`, `backend/tests/admin/test_admin_api.py`
- Redis rate limiting: `backend/app/core/rate_limit.py`, `backend/tests/security/test_rate_limit_backend.py`
- Readiness visibility: `backend/app/api/health.py`, `backend/app/schemas/health.py`
- Production config: `.env.production.example`, `docker-compose.prod.yml`, `backend/app/core/config.py`
- Documentation: `docs/security.md`, `docs/production-launch/`, `frontend/README.md`, `Readme.md`
- Validation record: `production-control/06_EXECUTION_LOG.md`, `production-control/08_VALIDATION_MATRIX.md`

## Blockers

No repository-controlled PR-12A blocker remains after validation.

External release evidence remains blocked until owner-approved staging/VPS validation, remote CI, restore drill, controlled smoke tests, and explicit owner approval are recorded.

## Completion Criteria

The independent-review repository gaps are corrected and validated. Public production launch remains NO-GO.
