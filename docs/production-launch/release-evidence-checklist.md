# Release Evidence Checklist

PR-13 update, 2026-05-30: before using this checklist for a real customer pilot, paid beta, or public launch, first resolve or explicitly scope the PR-13 findings recorded in `docs/production-audit/post-pr12a-final-audit/implementation-gap-register.md`.

Date: 2026-05-29  
Phase: PR-12 with PR-12A correction package

This checklist is the evidence ledger to use before changing any launch gate status. Checkboxes should be completed with dates, branch/commit, operator, and links to logs or screenshots where practical.

## Gate A: Controlled Internal Demo

Status: GO WITH CONDITIONS.

- [x] PR-00 through PR-04 production-control evidence exists.
- [x] Synthetic/sample-data-only warning is recorded.
- [x] No real customer onboarding is approved.
- [x] Public production and paid beta remain blocked without later gates.

## Gate B: Secure Private Internet Demo

Status: REPOSITORY READY WITH CONDITIONS.

Repository prerequisites:

- [x] PR-01 authentication/session/admin security verified.
- [x] PR-02 rate limiting, widget origin, CORS/CSRF/security-header controls verified.
- [x] PR-03 tenant integrity/privacy/audit model verified.
- [x] PR-04 production topology/TLS/backups/secrets/CI scans verified statically.
- [x] PR-05 worker queue and job visibility verified.

External evidence still required:

- [ ] Remote CI passes on the final target branch.
- [ ] Owner approves private demo scope and data policy.
- [ ] VPS firewall exposes only approved public ports.
- [ ] HTTPS certificate issuance and renewal path is tested.
- [ ] `/health` and `/ready` pass on the target host.
- [ ] Production super-admin MFA smoke confirms login is rejected without configured/valid MFA and accepted with valid TOTP.
- [ ] Redis-backed application rate-limit smoke confirms shared limits, retry headers, and fail-closed Redis outage behaviour.
- [ ] Worker heartbeat and Redis connectivity are verified.
- [ ] Encrypted backup and restore drill are completed.
- [ ] PostgreSQL/pgvector migration smoke passes.

## Gate C: Real Customer Pilot

Status: REPOSITORY READY WITH CONDITIONS.

Repository prerequisites:

- [x] PR-01 through PR-10 are verified in repository-controlled checks.
- [x] Secure website/sitemap ingestion exists.
- [x] Secure document upload and PDF/DOCX extraction exists.
- [x] SQL pgvector retrieval, citations, no-answer fallback, and RAG safety evals exist.
- [x] Onboarding, knowledge setup, agent sandbox, and widget installation UX exists.
- [x] Monitoring, metering, quotas, and cost controls exist.

External evidence still required:

- [ ] Owner approves the specific pilot tenant, terms, data set, and support owner.
- [ ] Controlled real-site crawl smoke passes for an approved domain.
- [ ] Controlled document upload smoke passes with owner-approved test files.
- [ ] Production-equivalent RAG smoke returns tenant-only cited answers.
- [ ] Log/alert destination receives request, job, error, and quota signals.
- [ ] Quota-limit smoke blocks at least one controlled operation gracefully.
- [ ] Incident-response contact path is documented and tested.

## Gate D: Paid Beta

Status: REPOSITORY READY WITH CONDITIONS.

Repository prerequisites:

- [x] PR-01 through PR-11 are verified in repository-controlled checks.
- [x] Manual paid-beta plans and tenant subscription records exist.
- [x] Server-side entitlement and quota enforcement exists.
- [x] Business portal billing/compliance visibility exists.
- [x] Privacy export includes subscription state.

Commercial and external evidence still required:

- [ ] Owner approves plan prices, GST/tax handling, invoice process, refund terms, and support SLA.
- [ ] Owner confirms manual invoicing is acceptable for first paid beta.
- [ ] Remote CI passes on the paid-beta target branch.
- [ ] VPS/staging smoke covers auth, production super-admin MFA, Redis-backed app rate limiting, entitlements, quotas, backup/restore, worker/Redis, pgvector RAG, and `/ready`.
- [ ] Support escalation, incident process, and customer-facing disclosures are ready.

## Gate E: Public Production Launch

Status: NO-GO.

Required before changing to GO:

- [ ] PR-12A final correction branch is merged after review.
- [ ] All repository-controlled PR-12A validation commands pass.
- [ ] Remote CI passes on the production launch candidate.
- [ ] Staging/VPS validation run passes.
- [ ] Production super-admin MFA smoke passes on the target environment.
- [ ] Redis-backed application rate-limit smoke passes on the target environment.
- [ ] Restore drill evidence is recorded and accepted.
- [ ] No unresolved critical production blocker remains.
- [ ] Owner explicitly approves public production launch.
- [ ] DNS, TLS, payment activation, and customer onboarding actions are separately authorized.
