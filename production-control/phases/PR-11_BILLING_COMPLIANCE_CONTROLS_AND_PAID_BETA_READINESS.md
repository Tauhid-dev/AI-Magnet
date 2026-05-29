# PR-11: Billing, Compliance Controls and Paid Beta Readiness

Status: verified

## Purpose

Prepare controlled paid onboarding only after security, data, RAG, and operations gates pass.

## Why It Is Needed

Billing/entitlements are currently planning-only. Paid beta must not start without enforceable commercial controls, quota alignment, privacy workflows, support readiness, and go/no-go evidence.

## Preconditions

- PR-10 is verified.
- Gate C real-customer pilot requirements are satisfied or intentionally blocked.

## In-Scope Work

- Entitlements/plans and plan enforcement.
- Billing integration or documented manual paid-beta entitlement process, chosen deliberately.
- Subscription/payment webhook safety if payment integration is included.
- Trial, limit, upgrade, downgrade, cancellation behavior appropriate to initial launch.
- Privacy policy/data retention/export/deletion operational alignment and customer-facing disclosures needed for beta scope.
- Support/admin workflow and customer issue handling.
- Paid-beta go/no-go review against release gates.

## Out-Of-Scope Work

- Marketplace.
- Multi-region enterprise billing.
- Advanced CRM.

## Source Areas Likely Affected

- `backend/app/models/`
- `backend/migrations/`
- `backend/app/api/admin.py`
- `backend/app/business/`
- `frontend/app/admin/`
- `frontend/app/portal/`
- `docs/future-modules/billing.md`
- `docs/`
- `backend/tests/`
- `frontend/tests/`

## Detailed Tasks

- [x] Decide billing/manual entitlement approach and record decision.
- [x] Add plan/entitlement model and enforcement.
- [x] Add billing integration or manual paid-beta workflow.
- [x] Add webhook/idempotency tests if provider billing is included. Not applicable: PR-11 deliberately uses manual paid-beta entitlements and no payment provider.
- [x] Align privacy/export/delete/support docs.
- [x] Add admin/customer visibility where needed.
- [x] Perform paid-beta go/no-go review.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Entitlement enforcement tests.
- Billing/manual workflow tests.
- Webhook tests if applicable.
- Frontend lint/typecheck/test/build.
- Paid-beta gate checklist.

## Security Considerations

Payment data must not be stored unless necessary. Webhooks require signature validation and idempotency.

## Migration And Rollback Notes

Plan/subscription state requires reversible migrations and clear failed payment state transitions.

## Evidence

- Decision: `DEC-PR-20260529-020` records manual paid-beta entitlement before Stripe/payment-provider automation.
- Data model and migration: `backend/app/models/billing.py`, `backend/app/billing/service.py`, `backend/migrations/versions/20260529_0012_pr11_billing_entitlements.py`.
- Enforcement: `backend/app/usage/quotas.py` applies tenant subscription limits and blocks billable work for `past_due`, `paused`, and `canceled` subscriptions.
- APIs: `backend/app/api/admin.py` exposes plan catalog and tenant subscription controls; `backend/app/api/business_portal.py` exposes business billing status.
- Frontend: `frontend/app/admin/billing/page.tsx`, `frontend/app/portal/billing/page.tsx`, `frontend/components/AdminShell.tsx`, `frontend/components/PortalShell.tsx`.
- Docs: `docs/paid-beta-readiness.md`, `docs/future-modules/billing.md`.
- Tests: `backend/tests/admin/test_admin_api.py`, `backend/tests/business/test_business_portal_api.py`, `backend/tests/usage/test_quota_service.py`, `frontend/tests/static-check.mjs`.
- Validation: focused PR-11 backend tests passed with 26 tests, full backend suite passed with 97 tests, ruff passed, compileall passed, SQLite Alembic upgrade/downgrade passed, frontend lint/typecheck/static test/build passed, Bandit passed, pip-audit found no known Python vulnerabilities, npm audit passed high threshold with moderate transitive PostCSS advisories still noted.

## Blockers

- No repository-controlled PR-11 blocker remains.
- Live paid-beta operation still requires owner approval, pricing/tax/refund confirmation, remote CI evidence, VPS/staging smoke, backup/restore evidence, and support readiness confirmation.

## Completion Criteria

Paid-beta repository controls are enforceable through manual entitlements and server-side quota checks. Gate D remains repository-ready with conditions, not unconditional GO, until owner approval and live release evidence are complete.
