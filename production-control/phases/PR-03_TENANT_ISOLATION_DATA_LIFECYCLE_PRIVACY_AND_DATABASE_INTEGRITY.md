# PR-03: Tenant Isolation, Data Lifecycle, Privacy and Database Integrity

Status: verified

## Purpose

Make multi-customer data ownership enforceable beyond application conventions.

## Why It Is Needed

Current tables include `tenant_id`, and service tests cover several boundaries, but database constraints do not fully prevent cross-tenant parent/child relationships. Privacy lifecycle workflows for export, deletion, retention, and offboarding are missing.

## Preconditions

- PR-01 and PR-02 are verified or blocking exceptions are documented.
- Current models and migrations are inspected before changes.

## In-Scope Work

- Add composite foreign keys, constraints, or database protections for same-tenant relationships.
- Cover documents/chunks, conversations/messages, leads, usage, notifications, widget configs, and business users where relevant.
- Add tenant isolation attack tests across API, services, and migrations.
- Implement retention, deletion, export, and tenant offboarding model for beta scope.
- Strengthen PII/privacy boundaries and log redaction rules.
- Add global administrator audit-event handling where tenant-scoped audit is insufficient.
- Document migration and rollback/data impact.

## Out-Of-Scope Work

- Full legal/privacy policy drafting.
- Billing entitlements.
- Multi-region data residency.

## Source Areas Likely Affected

- `backend/app/models/`
- `backend/migrations/`
- `backend/app/audit/`
- `backend/app/business/`
- `backend/app/admin/`
- `backend/app/analytics/`
- `backend/tests/`
- `docs/security.md`

## Detailed Tasks

- [x] Inspect all tenant-owned relationships and migrations.
- [x] Design same-tenant integrity constraints.
- [x] Add reversible migrations.
- [x] Add database and API cross-tenant tests.
- [x] Add export/delete/offboarding service and route plan/implementation for beta scope.
- [x] Add global or nullable-tenant audit strategy.
- [x] Add PII-safe logging and retention documentation updates.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Migration upgrade/downgrade.
- Cross-tenant fixture tests.
- API privacy lifecycle tests.
- Audit event tests.
- Backend lint/tests.

## Security Considerations

Tenant isolation failures are production blockers. Do not mark verified until tests prove wrong-tenant access fails.

## Migration And Rollback Notes

Data cleanup may be needed before adding constraints. Document destructive risks and rollback.

## Evidence

- Same-tenant model constraints: `backend/app/models/tenant.py`, `backend/app/models/knowledge.py`, `backend/app/models/conversation.py`, `backend/app/models/lead.py`, `backend/app/models/notification.py`.
- Reversible migration: `backend/migrations/versions/20260528_0007_pr03_tenant_privacy_integrity.py`.
- Privacy lifecycle APIs/services: `backend/app/api/admin.py`, `backend/app/admin/service.py`, `backend/app/schemas/admin.py`.
- Global admin audit model and redaction: `backend/app/models/usage.py`, `backend/app/audit/service.py`, `backend/app/core/privacy.py`.
- Admin privacy lifecycle frontend controls/API types: `frontend/app/admin/tenants/[tenantId]/page.tsx`, `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`.
- Security documentation: `docs/security.md`.
- Tests: `backend/tests/security/test_pr03_tenant_integrity.py`, `backend/tests/admin/test_admin_api.py`.
- Validation:
  - `python3 -m pytest backend/tests/security/test_pr03_tenant_integrity.py backend/tests/admin/test_admin_api.py` - pass, 9 tests.
  - `python3 -m pytest backend/tests` - pass, 56 tests.
  - `python3 -m ruff check backend/app backend/tests` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr03_alembic_20260528_2.db python3 -m alembic -c backend/alembic.ini upgrade head` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr03_alembic_20260528_2.db python3 -m alembic -c backend/alembic.ini downgrade 20260528_0006` - pass.
  - `npm run lint` - pass.
  - `npm run typecheck` - pass.
  - `npm test` - pass.
  - `npm run build` - pass.
  - `python3 -m json.tool production-control/status/production-status.json` - pass.
  - `python3 -c "import xml.etree.ElementTree as ET; ET.parse('production-control/visual/production-roadmap-status.svg'); print('svg ok')"` - pass.
  - `git diff --check` - pass.

## Blockers

None for PR-03. PR-04 remains required before Gate B because production topology, TLS, private PostgreSQL/Redis, backups, secrets, and CI scans are still open.

## Completion Criteria

Cross-tenant relationships are prevented/tested at appropriate layers and privacy lifecycle requirements are implemented or explicitly scoped for beta.

Completion criteria met on 2026-05-28. Residual production launch risks are tracked in PR-04 and later phases.
