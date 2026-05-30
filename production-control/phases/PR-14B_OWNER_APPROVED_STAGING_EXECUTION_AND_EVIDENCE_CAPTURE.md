# PR-14B - Owner-Approved Staging Execution and Evidence Capture

Status: not_started  
Production launch status: NO-GO

## Purpose

Execute the PR-14A GitHub Actions staging deployment and external validation framework after the owner configures the GitHub `staging` Environment, supplies required secrets/variables, approves the workflow run, and confirms synthetic data only.

## Why It Is Needed

Repository validation cannot prove live VPS, TLS, firewall, backup/restore, PostgreSQL/pgvector, Redis worker, multi-worker job claiming, ingestion, RAG, quota, monitoring, or browser behaviour on the target environment. PR-14B is the owner-approved external evidence phase.

## Preconditions

- PR-14A is merged.
- GitHub Environment `staging` exists.
- Required Environment variables and secrets are configured.
- Required reviewer/manual approval is enabled.
- Owner confirms synthetic data only.

## In Scope

- Manually run `Staging deployment validation` from GitHub Actions.
- Approve the GitHub Environment deployment.
- Deploy the selected branch/commit to staging.
- Capture evidence artifacts.
- Validate live staging readiness and external gates with synthetic data.
- Update release evidence checklist and production-control status based on actual results.

## Out of Scope

- Public production launch.
- Real customer onboarding.
- Payment activation.
- Production DNS changes.
- Production environment secrets.

## Tasks

- [ ] Confirm GitHub `staging` Environment variables/secrets.
- [ ] Run `Staging deployment validation` with `confirm_synthetic_data_only=true`.
- [ ] Review uploaded staging evidence artifact.
- [ ] Capture TLS/renewal proof or document blocker.
- [ ] Capture firewall/private-port proof.
- [ ] Capture backup and safe restore-drill proof.
- [ ] Capture live PostgreSQL/pgvector migration/RAG smoke.
- [ ] Capture live Redis worker and multi-worker job claim smoke.
- [ ] Capture controlled website/document ingestion smoke.
- [ ] Capture live rate-limit analytics and quota/abuse smoke.
- [ ] Capture backend-integrated browser/customer/admin/widget smoke.
- [ ] Capture monitoring/logging/alerting evidence.
- [ ] Update production-control release gates and GO/NO-GO status.

## Tests / Validation Required

- GitHub Actions required jobs pass.
- Staging workflow evidence artifact is present and reviewed.
- Every release-gate checklist item is pass/fail/manual evidence required with proof.

## Security Considerations

- Use synthetic data only.
- Do not expose secrets in logs or artifacts.
- Keep PostgreSQL and Redis private.
- Do not disable SSH host-key verification.
- Public production remains NO-GO unless later explicit owner launch approval is recorded.

## Completion Criteria

PR-14B is complete when owner-approved staging evidence is captured, release gates are updated truthfully, and a launch recommendation is recorded. Public production can only change from NO-GO after all required evidence and explicit owner approval are present.
