# Release Gates

Last updated: 2026-05-30

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

Current status: CONDITIONAL.

PR-01 through PR-06 are implemented in repository-controlled code and tests, PR-13A closed the PR-13 repository High findings, and PR #31 remote CI passed at `51687cec8695e397c41bb0daa377370be4da214f`. Before operating a private internet demo, the owner still needs post-merge launch-candidate CI plus VPS smoke validation for TLS, firewall exposure, worker health, Redis reachability, backups, restore, PostgreSQL/pgvector migration checks, and any owner-approved controlled real-site crawl smoke.

Requires verified:

- PR-01: production authentication and session security.
- PR-02: rate limiting, abuse protection, widget origin controls.
- PR-03: tenant isolation/privacy/database integrity.
- PR-04: production infrastructure, TLS, secrets, backups, CI security.
- PR-05: real queue/worker reliability.
- PR-06: secure website/sitemap ingestion, if the demo includes live website ingestion.

## Gate C: Real Customer Pilot

Current status: NO-GO pending PR-14B external evidence and owner approval.

Requires verified:

- PR-01 through PR-10.
- Real customer data handling, secure document ingestion, RAG safety, operational monitoring, quotas, incident response, and controlled crawl evidence.
- Owner approval for the specific customer pilot terms and data handling.

Remaining conditions before a real customer pilot may begin:

- Remote CI evidence for the latest production remediation branch and PR-14A framework branch.
- VPS/staging `/ready` smoke against production-equivalent PostgreSQL/pgvector.
- Production-equivalent PostgreSQL multi-worker job claim smoke.
- Live Redis-backed rate-limit denial and abuse analytics smoke.
- Live backend-integrated browser smoke for primary onboarding/widget workflows.
- Logging/alert destination configured and verified.
- Controlled quota-limit smoke test.
- Backup/restore drill evidence.
- Worker/Redis health smoke.
- Controlled real-site crawl and document-upload smoke.
- Owner approval for the exact customer, data set, and pilot terms.

## Gate D: Paid Beta

Current status: NO-GO pending PR-14B external evidence and owner commercial approval.

Requires verified:

- PR-01 through PR-11.
- Billing or manual paid-beta entitlement controls.
- Cost limits and customer-facing privacy/support process.
- Paid-beta go/no-go review in `06_EXECUTION_LOG.md`.

Remaining conditions before paid beta may begin:

- Owner approval for pricing, GST/tax handling, refund terms, and support process.
- Remote CI evidence for the final remediation branch.
- VPS/staging smoke evidence for auth, quotas, manual entitlement changes, backup/restore, worker/Redis, PostgreSQL/pgvector RAG, and readiness checks.
- Confirmation that manual invoicing is acceptable for the first paid beta; Stripe remains deferred.

## Gate E: Public Production Launch

Current status: NO-GO.

PR-12A repository security corrections are verified, PR-13 audit is complete, PR-13A closed the repository High findings from PR-13, and PR-14A prepares the GitHub Actions staging evidence framework. Public launch remains blocked by PR-14B external evidence and owner approval.

Requires:

- Remote CI evidence for the final launch candidate.
- Owner-approved staging/VPS validation using `docs/production-launch/vps-staging-validation-runbook.md`.
- Production super-admin MFA smoke on the target environment.
- Redis-backed application rate-limit smoke on the target environment.
- TLS certificate issuance and renewal evidence.
- External firewall proof that PostgreSQL and Redis are not public.
- Encrypted backup schedule plus tested restore procedure evidence.
- Production-equivalent PostgreSQL/pgvector migration and RAG smoke.
- Worker/Redis queue smoke.
- Controlled website crawl and document upload smoke.
- Log/alert destination verification.
- Quota-limit and abuse-control smoke.
- Explicit owner approval.
- No unresolved critical production blocker.
