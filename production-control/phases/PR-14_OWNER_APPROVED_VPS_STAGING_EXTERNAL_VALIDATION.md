# PR-14 - Owner-Approved VPS/Staging External Validation

Status: not_started
Production launch status: NO-GO until evidence and explicit owner approval are recorded.

## Purpose

Validate the repository-complete PR-13A package in an owner-approved VPS/staging environment using synthetic data only.

## Why It Is Needed

PR-13A closes the remaining repository-level High findings from PR-13, but repository tests cannot prove live TLS, firewall, backup/restore, PostgreSQL/pgvector behavior, Redis worker behavior, production readiness, alerting, quota behavior, or owner launch approval.

## Preconditions

- PR-13A is merged or explicitly selected as the base.
- Owner approves the staging/VPS target, data policy, allowed commands, and rollback expectations.
- No real customer data is used unless the owner separately approves a real pilot gate.

## In-Scope Work

- Record remote CI evidence for the launch-candidate branch.
- Render and smoke-test the production Compose topology on the approved target.
- Validate TLS issuance/renewal path, HTTPS redirect, HSTS, and secure headers.
- Prove PostgreSQL and Redis are not publicly exposed.
- Run `/health` and `/ready` checks against production-equivalent dependencies.
- Run production super-admin MFA smoke using synthetic/admin-approved credentials.
- Run Redis-backed application rate-limit smoke, including denial persistence into abuse analytics.
- Run PostgreSQL multi-worker background job claiming smoke.
- Run worker/Redis queue health and sample job smoke.
- Run PostgreSQL/pgvector migration and tenant-scoped RAG smoke.
- Run controlled website/sitemap and document ingestion smoke with synthetic or owner-approved test sources.
- Run live backend-integrated browser smoke for onboarding, agent test with citations, widget setup, and admin monitoring.
- Verify encrypted backup creation and restore drill.
- Verify log/alert destination, quota-limit behavior, and incident-response contact path.
- Capture evidence under `docs/production-launch/` or a dated evidence folder.

## Out-Of-Scope Work

- Public production launch.
- DNS cutover.
- Live customer onboarding.
- Payment activation.
- Real customer data processing without a separate explicit owner approval.
- Voice AI, SMS/WhatsApp, marketplace, mobile app, advanced CRM, multi-region, n8n runtime, or local Ollama runtime.

## Source Areas Likely Affected

- `docs/production-launch/`
- `production-control/`
- `docker-compose.prod.yml`
- `infra/nginx/`
- staging evidence logs/screenshots sanitized for secrets

## Detailed Tasks

- [ ] Confirm owner approval for target environment and synthetic-data policy.
- [ ] Pull and identify the exact launch-candidate branch/commit.
- [ ] Record remote CI result.
- [ ] Render production Compose config and confirm no public PostgreSQL/Redis host ports.
- [ ] Run target-host health/readiness smoke.
- [ ] Run target-host production super-admin MFA smoke.
- [ ] Run target-host Redis-backed rate-limit and abuse analytics smoke.
- [ ] Run PostgreSQL multi-worker job claiming smoke.
- [ ] Run worker/Redis sample job smoke.
- [ ] Run PostgreSQL/pgvector migration and RAG retrieval smoke.
- [ ] Run controlled website/document ingestion smoke.
- [ ] Run backend-integrated browser smoke for supported customer/admin/widget flows.
- [ ] Run backup creation and restore drill.
- [ ] Verify logging, alerting, quota-limit, and incident-response evidence.
- [ ] Update production-control status, dashboard, risk register, validation matrix, release gates, and launch docs.

## Tests And Validation Required

- Remote CI pass on the target branch.
- Target-host Docker Compose production config render.
- Target-host smoke tests listed above with sanitized evidence.
- `git diff --check` after any evidence/status updates.

## Security Considerations

Use synthetic data by default. Do not commit secrets, raw credentials, private keys, live tokens, raw customer data, or sensitive screenshots. Redact hostnames or IPs when the owner requests it.

## Migration And Rollback Notes

No destructive production migration is allowed without separate explicit owner approval. Any staging migration smoke must document exact upgrade/downgrade or rollback behavior and data impact.

## Evidence

Pending. Add dated evidence files when PR-14 is executed.

## Blockers

Owner-approved VPS/staging access and explicit permission are required before execution.

## Completion Criteria

PR-14 is complete only when owner-approved external evidence shows the target environment passes the defined staging/VPS checks. Public production launch remains NO-GO unless the owner separately approves launch after reviewing the evidence.
