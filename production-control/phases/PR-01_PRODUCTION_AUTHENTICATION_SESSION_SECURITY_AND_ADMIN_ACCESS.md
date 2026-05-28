# PR-01: Production Authentication, Session Security and Admin Access

Status: verified

## Purpose

Remove the critical authentication blocker for business portal and super-admin access.

## Why It Is Needed

Current business and admin login flows issue signed sessions from known emails without proof of mailbox ownership, password, MFA, or external identity verification. This blocks all internet-facing and customer-data gates.

## Preconditions

- PR-00 is verified.
- Current auth models/routes/frontend login flows are inspected before implementation.
- Branch should be named similar to `production/pr-01-auth-session-security`.

## In-Scope Work

- Choose and record production auth approach: secure password auth with reset/verification, verified passwordless magic-link, or identity provider.
- Implement production business authentication.
- Implement strong admin authentication and MFA/admin protection appropriate to stack.
- Decide and implement secure browser session/token strategy, preferably HttpOnly/Secure/SameSite cookies where architecture permits.
- Add logout, session expiry, session revocation, and audit events.
- Add brute-force controls/hooks that integrate with PR-02 rate limiting.
- Add role/permission and admin/support access boundaries.
- Add unit, integration, security, and frontend login/error-state tests.

## Out-Of-Scope Work

- Full billing or plan entitlements.
- Widget origin enforcement except as it affects session security.
- Live deployment.

## Source Areas Likely Affected

- `backend/app/business/auth.py`
- `backend/app/admin/auth.py`
- `backend/app/api/business_portal.py`
- `backend/app/api/admin.py`
- `backend/app/models/tenant.py`
- `backend/app/models/admin.py`
- `backend/migrations/`
- `frontend/app/login/page.tsx`
- `frontend/app/admin/login/page.tsx`
- `frontend/lib/auth/`
- `backend/tests/`
- `frontend/tests/`
- `.env.example`

## Detailed Tasks

- [x] Inspect current business/admin auth and frontend token storage.
- [x] Record auth/session decision in `05_DECISIONS_LOG.md`.
- [x] Add schema/model changes for chosen auth method.
- [x] Implement verified business login and logout.
- [x] Implement verified admin login, admin protection, and MFA requirement/design.
- [x] Replace or harden bearer/localStorage session handling.
- [x] Add session revocation and expiration tests.
- [x] Add failed login, inactive user, inactive tenant, cross-portal token, and admin role tests.
- [x] Update frontend login, logout, and error states.
- [x] Update `.env.example` with non-secret configuration.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Backend auth and API tests.
- Frontend lint/typecheck/test/build.
- Security tests for no email-only production path, session cookies/tokens, logout/revocation, inactive users, admin boundaries.
- Migration upgrade/downgrade checks if schema changes.

## Security Considerations

- Do not store plaintext passwords or secrets.
- Passwords require strong hashing if password auth is chosen.
- Cookies must be Secure/SameSite/HttpOnly in production if used.
- CSRF/CSP implications must be documented for PR-02.

## Migration And Rollback Notes

Use reversible migrations. Document impact on existing demo users and seed data.

## Evidence

- `backend/app/core/passwords.py`
- `backend/app/core/totp.py`
- `backend/migrations/versions/20260528_0006_pr01_auth_security.py`
- `backend/tests/business/test_business_portal_api.py`
- `backend/tests/admin/test_admin_api.py`
- `backend/tests/security/test_security_boundaries.py`
- `frontend/lib/auth/session.ts`
- `frontend/lib/auth/admin-session.ts`
- `frontend/app/login/page.tsx`
- `frontend/app/admin/login/page.tsx`
- Validation commands recorded in `production-control/06_EXECUTION_LOG.md`.

## Blockers

None for PR-01 exit gate.

Residual PR-02 blocker: CSRF/CSP/security-header review and public endpoint abuse controls are still required for internet exposure.

## Completion Criteria

- No production user/admin can authenticate by email-only session issuance.
- Auth flows and failure/abuse cases are tested.
- Residual risks are documented.
