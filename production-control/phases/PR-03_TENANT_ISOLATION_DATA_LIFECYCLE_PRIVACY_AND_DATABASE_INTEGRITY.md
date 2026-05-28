# PR-03: Tenant Isolation, Data Lifecycle, Privacy and Database Integrity

Status: not_started

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

- [ ] Inspect all tenant-owned relationships and migrations.
- [ ] Design same-tenant integrity constraints.
- [ ] Add reversible migrations.
- [ ] Add database and API cross-tenant tests.
- [ ] Add export/delete/offboarding service and route plan/implementation for beta scope.
- [ ] Add global or nullable-tenant audit strategy.
- [ ] Add PII-safe logging and retention documentation updates.
- [ ] Update status/risk/validation/visual artifacts.

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

To be filled during PR-03.

## Blockers

Requires auth and public API controls to avoid building lifecycle APIs on insecure sessions.

## Completion Criteria

Cross-tenant relationships are prevented/tested at appropriate layers and privacy lifecycle requirements are implemented or explicitly scoped for beta.
