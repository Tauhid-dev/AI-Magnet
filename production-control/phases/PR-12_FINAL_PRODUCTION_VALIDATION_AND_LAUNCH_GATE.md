# PR-12: Final Production Validation, VPS Deployment Runbook and Launch Gate

Status: verified

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

- [x] Re-audit all PR phases against evidence.
- [x] Run repository-controlled validation suite.
- [x] Document production-equivalent Postgres/pgvector migration and vector smoke checks.
- [x] Document restore drill evidence requirements.
- [x] Document browser/e2e and abuse/load checks required for target-host validation.
- [x] Validate staging/VPS runbook without live deployment.
- [x] Update risk register with residual risks.
- [x] Update final launch go/no-go.
- [x] Update status/risk/validation/visual artifacts.

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

- Final validation report: `docs/production-launch/final-production-validation-report.md`
- Release evidence checklist: `docs/production-launch/release-evidence-checklist.md`
- VPS/staging validation runbook: `docs/production-launch/vps-staging-validation-runbook.md`
- Rollback and restore runbook: `docs/production-launch/rollback-and-restore-runbook.md`
- Final GO/NO-GO statement: `docs/production-launch/final-go-no-go-statement.md`
- Updated release readiness: `docs/release-readiness.md`
- Updated risk register: `production-control/07_RISK_REGISTER.md`
- Updated validation matrix: `production-control/08_VALIDATION_MATRIX.md`
- Updated status JSON and visual artifacts: `production-control/status/production-status.json`, `production-control/visual/`

## Blockers

PR-11 is verified. Live production action remains blocked until the owner explicitly approves the action and target.

Public production launch remains NO-GO until owner-approved external evidence is recorded for remote CI, staging/VPS smoke, TLS renewal, firewall exposure, backup/restore, PostgreSQL/pgvector RAG, worker/Redis, controlled crawl/document upload, logging/alerting, quota/abuse smoke, and explicit launch approval.

## Completion Criteria

Evidence-backed launch recommendation exists. Production launch remains NO-GO because external live evidence and owner approval are not yet recorded.
