# PR-02: Public API Abuse Protection, Widget Origin Controls and API Security

Status: verified

## Purpose

Protect public-facing chatbot, login, ingestion, and admin surfaces from abuse and unapproved embedding.

## Why It Is Needed

Current endpoints have no rate limiting. Widget origins can be unrestricted when `allowed_origins` is unset. This exposes the platform to brute force, spam, tenant abuse, and uncontrolled AI provider cost.

## Preconditions

- PR-01 is verified or explicitly documented as blocked with safe independent subtasks.
- Chosen session/cookie strategy is understood.

## In-Scope Work

- Implement rate limiting for login, widget init, chat/message, ingestion, lead, and high-risk admin operations.
- Define per-IP, per-account, per-tenant, per-widget-key policies as appropriate.
- Add application-level and/or Nginx-level limiting.
- Enforce widget allowed-domain/origin controls in production.
- Add widget key create, rotate, revoke, and disable workflow plus portal controls/API.
- Review CORS, CSRF, CSP, security headers, and cookie behavior.
- Add payload bounds, safe error responses, and abuse logging.

## Out-Of-Scope Work

- Website crawling implementation.
- Billing quotas beyond abuse/rate-limit primitives.
- Live deployment.

## Source Areas Likely Affected

- `backend/app/main.py`
- `backend/app/api/widget.py`
- `backend/app/api/chat.py`
- `backend/app/api/business_portal.py`
- `backend/app/api/admin.py`
- `backend/app/widget/service.py`
- `backend/app/core/security.py`
- `infra/nginx/`
- `frontend/app/portal/widget/page.tsx`
- `frontend/lib/api/`
- `backend/tests/`
- `frontend/tests/`

## Detailed Tasks

- [x] Inspect public endpoints and current CORS/session behavior.
- [x] Decide rate-limit implementation and record decision.
- [x] Add rate-limit config with production-safe defaults.
- [x] Add endpoint-specific rate policies.
- [x] Add widget origin management API and portal UI.
- [x] Add key revoke/rotate/disable workflow.
- [x] Add positive/negative origin tests.
- [x] Add abuse logging via PII-safe rate-limit scope logs and tenant usage events.
- [x] Review and update security headers, CSRF, CSP, and CORS.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Unit/integration tests for rate-limit policies.
- Origin enforcement tests.
- Widget key lifecycle tests.
- Frontend lint/typecheck/test/build.
- Compose/Nginx config validation if proxy limits are used.

## Security Considerations

Rate-limit bypass, forwarded IP trust, CORS wildcard, CSRF, and widget key leakage must be considered.

## Migration And Rollback Notes

No schema migration was required. Widget lifecycle state uses the existing `status`, `allowed_origins`, `key_prefix`, and hashed-key fields. Rollback is code-only: revert PR-02 changes and reset `WIDGET_REQUIRE_ALLOWED_ORIGINS` / rate-limit environment settings as needed for local development.

## Evidence

- Branch: `production/pr-02-api-abuse-widget-security`.
- App-level rate limit helper: `backend/app/core/rate_limit.py`.
- Production rate-limit and widget-origin config: `backend/app/core/config.py`, `.env.example`.
- Cookie CSRF confirmation: `backend/app/api/session_cookies.py`, `frontend/lib/api/client.ts`.
- Public endpoint policies: `backend/app/api/widget.py`, `backend/app/api/chat.py`.
- Portal/admin write policies: `backend/app/api/business_portal.py`, `backend/app/api/admin.py`.
- Widget origin and lifecycle service: `backend/app/widget/service.py`.
- Portal widget controls: `frontend/app/portal/widget/page.tsx`, `frontend/lib/api/client.ts`.
- Tests: `backend/tests/business/test_business_portal_api.py`, `backend/tests/chat/test_chat_api.py`, `backend/tests/security/test_security_boundaries.py`.
- Validation:
  - `python3 -m pytest backend/tests` - pass, 54 tests.
  - `python3 -m ruff check backend/app backend/tests` - pass.
  - `npm run lint` - pass.
  - `npm run typecheck` - pass.
  - `npm test` - pass.
  - `npm run build` - pass.

## Blockers

No PR-02 blockers remain. Distributed/proxy-backed rate limiting and production network hardening are intentionally left to PR-04/PR-05.

## Completion Criteria

Public endpoints have enforced and tested abuse controls. A tenant widget cannot be used from an unauthorized origin in production configuration.
