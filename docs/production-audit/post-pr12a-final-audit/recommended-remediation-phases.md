# Recommended Remediation Phases

Date: 2026-05-30

## PR-13A - Security And Operations Correctness Remediation

Scope:

- Make background job acquisition atomic/concurrency-safe for multiple worker processes.
- Add concurrent worker race tests proving a due job is claimed once.
- Persist application rate-limit exceed events into usage/abuse analytics where tenant/widget/account context exists.
- Ensure persisted abuse events avoid PII and do not create a write-amplification risk under attack.
- Update PR-05, PR-02, PR-10 status and validation evidence.

Dependencies:

- Current PR-13 audit findings.

Acceptance criteria:

- Full backend suite passes.
- New concurrent worker tests pass.
- New rate-limit usage-event tests pass.
- Admin analytics can observe rate-limit exceed events from tenant/widget-scoped limiter failures.
- Public production remains NO-GO until external evidence is recorded.

Blocks:

- Real customer pilot.
- Paid beta.
- Public production launch.

## PR-13B - Product Flow Browser/E2E Evidence Remediation

Scope:

- Add reproducible browser/e2e coverage for login, onboarding, knowledge source setup, agent sandbox with citations, widget key/domain setup and embed snippet generation.
- Include failure/empty/loading state checks for the primary business portal flows.
- Decide whether to add Playwright or a lighter repository-approved browser test approach.
- Update PR-09 phase evidence and validation matrix.

Dependencies:

- PR-13 audit findings.
- PR-13A if shared setup/security helpers are touched.

Acceptance criteria:

- Browser/e2e tests are committed and runnable in CI or documented with a reliable manual target-host procedure.
- Previous PR-09 checklist wording is corrected or backed by executed evidence.

Blocks:

- Real customer pilot if business self-service onboarding is in scope.
- Paid beta.

## PR-13C - Documentation And Status Cleanup

Scope:

- Sweep production-control, launch docs and README files for stale commit placeholders, phase counts, and PR-13 findings.
- Ensure PR-00 through PR-12A history is preserved and PR-13/PR-13A findings are visible.
- Keep historical audit baseline under `docs/audit/2026-05-23-end-to-end/` unchanged except for explicit cross-reference if needed.

Dependencies:

- PR-13 findings.

Acceptance criteria:

- Status JSON, Mermaid, SVG/dashboard, current status, risk register, validation matrix and release gates agree.
- No document claims public production GO.
- No document claims OCR or browser/Playwright crawling as implemented.

Blocks:

- Not a code blocker by itself, but should be completed before external release review.

## PR-14 - Owner-Approved External Staging/VPS Validation

Scope:

- Run staging/VPS deployment smoke with owner approval.
- Record remote CI status.
- Prove TLS issuance/renewal, firewall/private PostgreSQL/Redis exposure, backup schedule, restore drill, live `/ready`, live Redis limiter, worker/Redis job, PostgreSQL/pgvector RAG, controlled crawl, controlled document upload, log/alert destination and quota/abuse smoke.
- Attach evidence files under `docs/production-launch/` or a new evidence folder.

Dependencies:

- PR-13A complete.
- PR-13B complete or owner explicitly scopes out self-service customer flow from the staging gate.
- Owner explicitly authorizes staging/VPS actions.

Acceptance criteria:

- External evidence files are present.
- Public production remains NO-GO unless owner separately approves launch after evidence review.

Blocks:

- Real customer pilot.
- Paid beta.
- Public production launch.

