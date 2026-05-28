# AI-Magnet Repository Guidance

## AI-MAGNET PRODUCTION PHASE EXECUTION PROTOCOL

This repository has two distinct planning histories:

- `project-control/` and `project-assets/roadmap/` record the original MVP Phase 0-10 build history.
- `production-control/` is the production-remediation source of truth from 2026-05-28 onward.

When the user issues a short command such as `Implement production phase PR-01`, `Run PR-04`, `Continue PR-08`, or `Production phase 6`, Codex must interpret it as execution of the matching `production-control/phases/PR-XX_*.md` phase, not the original MVP Phase 0-10 history.

Before production phase work, follow the user's standing git workflow unless explicitly overridden: switch to `master`, pull remote, create or use a dedicated production feature branch, commit validated changes, and push the branch. Do not merge to `master`.

### Start-Of-Phase Rules

1. Read `production-control/04_CURRENT_STATUS.md`, `production-control/02_MASTER_PRODUCTION_ROADMAP.md`, the target `production-control/phases/PR-XX_*.md`, `production-control/07_RISK_REGISTER.md`, `production-control/08_VALIDATION_MATRIX.md`, `production-control/05_DECISIONS_LOG.md`, `production-control/06_EXECUTION_LOG.md`, `production-control/status/production-status.json`, and repository guidance files.
2. Confirm dependencies and gates. If a preceding required security/data gate is incomplete, do not quietly skip it; mark the requested phase blocked or implement only safe independent subtasks with clear documentation.
3. Inspect current code before changing it. Existing work may have been added since the previous run.
4. Create or switch to a dedicated feature branch named similar to `production/pr-XX-short-description`, unless already executing on the correct phase branch.
5. Do not begin a different PR phase unless it is a strictly required dependency and is explicitly documented as such in the current execution log.

### Implementation Rules

6. Implement the selected phase fully enough to satisfy its acceptance checklist; do not make cosmetic status updates without implementation evidence.
7. Preserve existing working features; prefer incremental production hardening over rewrites.
8. Add or update tests for each behaviour, security, or data change.
9. For database/schema work, use reversible migrations and document rollback/data impact.
10. Do not place secrets in source control. Update `.env.example` with non-secret configuration only.
11. Never expose PostgreSQL or Redis publicly in production configurations.
12. Never mark authentication, tenant isolation, data safety, or launch gates complete without relevant tests/validation evidence.
13. Do not deploy, migrate a live production database, change DNS, open firewall ports, or execute VPS destructive actions unless the user explicitly instructs that deployment step.

### End-Of-Phase Rules

14. Run the most appropriate validation available for the selected work: tests, lint, typecheck, build, migration checks, security tests, compose configuration validation, and/or documented manual verification.
15. Update the target phase file checklist with evidence; update `production-control/status/production-status.json`, `production-control/04_CURRENT_STATUS.md`, `production-control/06_EXECUTION_LOG.md`, `production-control/07_RISK_REGISTER.md`, `production-control/08_VALIDATION_MATRIX.md`, and `production-control/05_DECISIONS_LOG.md` where decisions changed.
16. Regenerate/update the Mermaid and visible SVG/PNG/dashboard status artifacts after every phase run, including partial or blocked runs.
17. Provide a concise completion report: implemented, files changed, validations run/results, remaining blockers, updated go/no-go, next permitted phase, branch, and recommended commit message.
18. Commit changes only after validation is recorded; never falsely report a commit or pushed branch.

### Status Rules

- `not_started`: no meaningful implementation evidence for this production remediation phase.
- `in_progress`: implementation has begun but gate is not met.
- `blocked`: work cannot safely proceed because a prerequisite or unresolved risk blocks completion.
- `complete`: implementation tasks are finished but final required verification is not yet complete.
- `verified`: implementation and required validation evidence satisfy the phase completion criteria.

A production phase must not be `verified` simply because an earlier MVP implementation exists.
