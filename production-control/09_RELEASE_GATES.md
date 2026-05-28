# Release Gates

Last updated: 2026-05-28

## Gate A: Controlled Internal Demo

Current status: GO WITH CONDITIONS.

Allowed:

- Synthetic/sample data only.
- Local or controlled development environment.
- Internal evaluation of UX and technical direction.

Required:

- No real customer data.
- No public production claim.
- Clear warning that infrastructure, backups, queueing, ingestion, RAG quality, monitoring, quotas, and billing are not production-ready.

## Gate B: Secure Private Internet Demo

Current status: NO-GO.

PR-01, PR-02, and PR-03 are verified. PR-04 and PR-05 remain required before this gate can move.

Requires verified:

- PR-01: production authentication and session security.
- PR-02: rate limiting, abuse protection, widget origin controls.
- PR-03: tenant isolation/privacy/database integrity.
- PR-04: production infrastructure, TLS, secrets, backups, CI security.
- PR-05: real queue/worker reliability.

## Gate C: Real Customer Pilot

Current status: NO-GO.

Requires verified:

- PR-01 through PR-10.
- Real customer data handling, ingestion, RAG safety, operational monitoring, quotas, and incident response.
- Owner approval for the specific customer pilot terms and data handling.

## Gate D: Paid Beta

Current status: NO-GO.

Requires verified:

- PR-01 through PR-11.
- Billing or manual paid-beta entitlement controls.
- Cost limits and customer-facing privacy/support process.
- Paid-beta go/no-go review in `06_EXECUTION_LOG.md`.

## Gate E: Public Production Launch

Current status: NO-GO.

Requires:

- PR-12 final production validation and independent re-audit.
- All required test, migration, security, staging/VPS, backup/restore, and rollback evidence.
- Explicit owner approval.
- No unresolved critical production blocker.
