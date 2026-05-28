# PR-02: Public API Abuse Protection, Widget Origin Controls and API Security

Status: not_started

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

- [ ] Inspect public endpoints and current CORS/session behavior.
- [ ] Decide rate-limit implementation and record decision.
- [ ] Add rate-limit config with production-safe defaults.
- [ ] Add endpoint-specific rate policies.
- [ ] Add widget origin management API and portal UI.
- [ ] Add key revoke/rotate/disable tests.
- [ ] Add positive/negative origin tests.
- [ ] Add abuse log events without leaking PII.
- [ ] Review and update security headers, CSRF, CSP, and CORS.
- [ ] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Unit/integration tests for rate-limit policies.
- Origin enforcement tests.
- Widget key lifecycle tests.
- Frontend lint/typecheck/test/build.
- Compose/Nginx config validation if proxy limits are used.

## Security Considerations

Rate-limit bypass, forwarded IP trust, CORS wildcard, CSRF, and widget key leakage must be considered.

## Migration And Rollback Notes

Schema migration may be required for widget key lifecycle metadata. Provide downgrade/rollback.

## Evidence

To be filled during PR-02.

## Blockers

Depends on PR-01 for final cookie/CSRF alignment.

## Completion Criteria

Public endpoints have enforced and tested abuse controls. A tenant widget cannot be used from an unauthorized origin in production configuration.
