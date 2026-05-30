# PR-14A - GitHub Actions Staging Deployment and External Validation Framework

Status: verified  
Branch: `production/pr-14a-github-actions-staging-validation`  
Baseline branch: `master`  
Baseline commit: `1b8a979fd60b44c31467026fd429bf8a9c6c1521`  
Production launch status: NO-GO

## Purpose

Create the repository framework for owner-approved staging deployment and external validation using GitHub Actions Environments, environment secrets, manual approval gates, synthetic data, deployment scripts, smoke checks, backup/restore drill helpers, and evidence capture.

## Why It Is Needed

PR-13A closed repository-level High findings, but the project still lacks live external evidence for the release gates: VPS/staging deployment, TLS, firewall/private-port proof, backup/restore, live PostgreSQL/pgvector, Redis worker, multi-worker job claim, ingestion, RAG, rate-limit analytics, browser smoke, monitoring, quota/abuse, and owner approval.

PR-14A does not run those live checks. It prepares the safe workflow and scripts so PR-14B can execute them later after the owner configures the GitHub `staging` Environment and manually approves the workflow run.

## Preconditions

- PR-13A is merged into `master`.
- Work starts from latest `master`.
- GitHub Environment secrets are not committed to the repository.
- No live VPS deployment occurs during PR-14A.

## In Scope

- Add `.github/workflows/staging-deploy-validation.yml`.
- Use `workflow_dispatch` and GitHub Environment `staging`.
- Require owner confirmation of synthetic data only.
- Validate required GitHub Environment variables/secrets before deployment.
- Use SSH private key and known-hosts values from environment secrets.
- Keep `StrictHostKeyChecking=yes`.
- Add staging bootstrap, deploy, validation, backup, restore-drill, and evidence scripts.
- Document required GitHub Environment variables/secrets and safe future auto-deploy options.
- Update production-control roadmap/status/dashboard/risk/validation/release-gate memory.

## Out of Scope

- Live VPS deployment.
- DNS changes.
- Certificate issuance or renewal.
- Production database migration against a live host.
- Payment activation.
- Real customer onboarding or real customer data.
- Public production GO.

## Source Areas Likely Affected

- `.github/workflows/staging-deploy-validation.yml`
- `scripts/staging/*.sh`
- `docs/deployment/github-environment-secrets.md`
- `docs/deployment/staging-auto-deploy-plan.md`
- `production-control/*`
- `production-control/visual/*`

## Tasks

- [x] Confirm PR-13A is merged into `master`.
- [x] Create `production/pr-14a-github-actions-staging-validation`.
- [x] Add manual GitHub Actions staging workflow.
- [x] Add VPS bootstrap helper.
- [x] Add staging deployment helper.
- [x] Add synthetic-data-only staging validation helper.
- [x] Add backup and safe restore-drill helpers.
- [x] Add redacted evidence capture helper.
- [x] Add GitHub Environment setup documentation.
- [x] Add disabled-by-default auto-deploy plan.
- [x] Run local PR-14A validation.
- [x] Update validation evidence after commands complete.

## Tests / Validation Required

- YAML syntax validation for `.github/workflows/staging-deploy-validation.yml`.
- `bash -n scripts/staging/*.sh`.
- `shellcheck scripts/staging/*.sh` if available.
- Status JSON parse.
- SVG parse.
- Git diff whitespace check.
- No live deployment.

## Security Considerations

- No VPS host, private key, API key, database password, SMTP password, MFA secret, or environment value is committed.
- The workflow uses GitHub Environment `staging` so secrets are only released after owner approval.
- SSH host identity is validated with `STAGING_SSH_KNOWN_HOSTS`.
- The evidence capture script redacts common secret/token/password patterns before saving service logs.
- Artifacts must not contain real customer data.

## Migration / Rollback Notes

No database migration is added in PR-14A.

Rollback is documentation/workflow-only: remove the workflow and staging scripts if the owner chooses a different deployment mechanism.

## Evidence

- `.github/workflows/staging-deploy-validation.yml`
- `scripts/staging/bootstrap-vps.sh`
- `scripts/staging/deploy-staging.sh`
- `scripts/staging/validate-staging.sh`
- `scripts/staging/backup-staging.sh`
- `scripts/staging/restore-staging-drill.sh`
- `scripts/staging/capture-staging-evidence.sh`
- `docs/deployment/github-environment-secrets.md`
- `docs/deployment/staging-auto-deploy-plan.md`

## Blockers

- PR-14B requires owner-created GitHub Environment variables/secrets and manual approval.
- Real staging evidence cannot be produced from the repository alone.

## Completion Criteria

PR-14A is marked verified because the workflow, scripts, docs, status memory, and local syntax/status validation passed. Public production remains NO-GO.
