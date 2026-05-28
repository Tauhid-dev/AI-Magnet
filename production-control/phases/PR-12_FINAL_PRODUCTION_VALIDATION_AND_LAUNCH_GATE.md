# PR-12: Final Production Validation, VPS Deployment Runbook and Launch Gate

Status: not_started

## Purpose

Re-audit the product and validate production launch readiness. Execute live deployment only upon separate explicit permission.

## Why It Is Needed

Production launch must be evidence-backed, not inferred from phase completion. The final phase verifies all release gates, residual risks, tests, infrastructure, backups, rollback, and owner approval.

## Preconditions

- PR-11 is verified.
- All critical/high risks are closed or explicitly accepted by owner with evidence.
- No live deployment permission is assumed.

## In-Scope Work

- End-to-end audit against PR-00 baseline and every release gate.
- Complete test suite, CI, migrations against production-equivalent PostgreSQL/pgvector, security checks, browser tests, load/abuse checks, and restore drill evidence as scoped.
- Staging/VPS deployment runbook validation and rollback procedure.
- Final visible diagrams, status dashboard, audit report, residual risk register, and go/no-go statement.
- Separate explicit user permission gate before real customer onboarding, live DNS/TLS changes, payment activation, or production deployment.

## Out-Of-Scope Work

- Live production deployment unless explicitly instructed.
- New feature development beyond launch blockers discovered by final audit.

## Source Areas Likely Affected

- `production-control/`
- `docs/`
- `.github/workflows/`
- `docker-compose*.yml`
- `infra/`
- tests across backend/frontend/widget

## Detailed Tasks

- [ ] Re-audit all PR phases against evidence.
- [ ] Run complete validation suite.
- [ ] Validate production-equivalent Postgres/pgvector migration and vector smoke checks.
- [ ] Validate restore drill evidence.
- [ ] Validate browser/e2e and abuse/load checks.
- [ ] Validate staging/VPS runbook without live deployment unless permitted.
- [ ] Update risk register with residual risks.
- [ ] Update final launch go/no-go.
- [ ] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Complete backend/frontend/widget/CI suite.
- Security scans.
- Migration checks on production-equivalent Postgres/pgvector.
- E2E browser tests.
- Backup restore drill.
- Load/abuse checks appropriate to beta/launch.
- Manual release checklist and owner approval.

## Security Considerations

Do not mark Production Launch GO with open critical risks or missing owner approval.

## Migration And Rollback Notes

Deployment runbook must include rollback procedure, migration rollback policy, and data restore boundaries.

## Evidence

To be filled during PR-12.

## Blockers

Requires PR-11 verified and explicit owner approval for any live production action.

## Completion Criteria

Evidence-backed launch recommendation exists. Mark production GO only when every required release gate passes; otherwise retain NO-GO with precise remaining work.
