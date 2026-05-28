# PR-00: Visible Roadmap, Persistent Memory and Verified Baseline

Status: verified

## Purpose

Create the production-control memory structure, diagrams/dashboard, Codex resume protocol, and evidence-backed starting status.

## Why It Is Needed

The existing MVP Phase 0-10 system tracks build history. Production remediation needs a separate resumable system that maps audit blockers to launch gates and prevents later Codex runs from treating MVP foundations as production readiness.

## Preconditions

- Repository audit pack is available under `docs/audit/2026-05-23-end-to-end/`.
- Current repository source can be inspected without deployment.
- Work is performed on a dedicated branch.

## In-Scope Work

- Inspect existing repo guidance, project-control docs, audit docs, security/deployment docs, and current source evidence.
- Create `production-control/` memory files.
- Create PR-00 through PR-12 phase files.
- Create machine-readable status JSON.
- Create Mermaid, SVG, and static HTML visual status dashboard.
- Add root `AGENTS.md` production phase execution protocol.
- Record initial go/no-go and audit gap mapping.

## Out-Of-Scope Work

- No PR-01 or later feature remediation.
- No production deployment.
- No live database migration.
- No VPS action.

## Source Areas Likely Affected

- `production-control/`
- `AGENTS.md`

## Detailed Tasks

- [x] Inspect repository root, branch, and status.
- [x] Read existing project-control, audit, security, deployment, roadmap, backend, frontend, widget, infra, and CI evidence.
- [x] Create production charter, baseline, roadmap, dependency graph, current status, decisions log, execution log, risk register, validation matrix, release gates, and deferred scope.
- [x] Create one detailed file per PR phase.
- [x] Create status JSON.
- [x] Create visual Mermaid, SVG, HTML dashboard, and visual README.
- [x] Add Codex resume protocol to `AGENTS.md`.
- [x] Validate JSON and diff hygiene before commit.

## Tests And Validation Required

- `python3 -m json.tool production-control/status/production-status.json`
- `git diff --check`
- Static review that dashboard/SVG files exist and are readable.
- Confirm product runtime code was not modified.

## Security Considerations

PR-00 must document risks but must not mark security controls complete unless implementation evidence exists.

## Migration And Rollback Notes

No database migration. Rollback is deletion of `production-control/` and `AGENTS.md` changes from the PR branch.

## Evidence

- `production-control/`
- `AGENTS.md`
- Existing audit: `docs/audit/2026-05-23-end-to-end/`

## Blockers

None for PR-00.

## Completion Criteria

- Future Codex can execute `Implement production phase PR-01` using persisted repo context only.
- PR-00 status is reflected in JSON, dashboard, and roadmap.
