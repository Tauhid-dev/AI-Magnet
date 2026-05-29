# Release Gates

Last updated: 2026-05-29

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

Current status: REPOSITORY READY WITH CONDITIONS.

PR-01 through PR-06 are verified in repository-controlled code and tests. Before operating a private internet demo, the owner still needs remote CI evidence plus VPS smoke validation for TLS, firewall exposure, worker health, Redis reachability, backups, restore, PostgreSQL/pgvector migration checks, and any owner-approved controlled real-site crawl smoke.

Requires verified:

- PR-01: production authentication and session security.
- PR-02: rate limiting, abuse protection, widget origin controls.
- PR-03: tenant isolation/privacy/database integrity.
- PR-04: production infrastructure, TLS, secrets, backups, CI security.
- PR-05: real queue/worker reliability.
- PR-06: secure website/sitemap ingestion, if the demo includes live website ingestion.

## Gate C: Real Customer Pilot

Current status: REPOSITORY READY WITH CONDITIONS.

Requires verified:

- PR-01 through PR-10.
- Real customer data handling, secure document ingestion, RAG safety, operational monitoring, quotas, incident response, and controlled crawl evidence.
- Owner approval for the specific customer pilot terms and data handling.

Remaining conditions before a real customer pilot may begin:

- Remote CI evidence for the current PR-10 branch.
- VPS/staging `/ready` smoke against production-equivalent PostgreSQL/pgvector.
- Logging/alert destination configured and verified.
- Controlled quota-limit smoke test.
- Backup/restore drill evidence.
- Worker/Redis health smoke.
- Controlled real-site crawl and document-upload smoke.
- Owner approval for the exact customer, data set, and pilot terms.

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
