# Agent Memory Protocol

## Purpose

This protocol defines how the parent agent and simulated sub-agents preserve context across sessions without bloating the repository memory files.

## Parent agent responsibilities

- Read `11_master_context_index.md` and `13_quick_resume.md` first.
- Determine active phase and task IDs.
- Assign work by agent role.
- Choose Small, Medium, or Full Context Mode.
- Keep memory files synchronized after changes.
- Prevent future-scope implementation during MVP phases.
- Produce concise end-of-phase summaries.

## Sub-agent responsibilities

Each simulated sub-agent should:

- Load only files relevant to its role and task.
- Avoid repeating full context from planning docs.
- Work within clear file ownership boundaries.
- Report assumptions, changed files, tests, and risks.
- Tell the parent agent when memory files need updates.

## Context handoff rules

Every handoff should include:

- Task ID.
- Role.
- Objective.
- Context loaded.
- Files touched.
- Decisions needed or made.
- Tests/checks run.
- Known issues.
- Next recommended action.

Keep handoffs concise. Do not paste full file contents unless the next agent must edit them.

## Work summary format

Use this shape for sub-agent summaries:

```text
Role:
Task ID:
Goal:
Files changed:
Tests/checks:
Decision log needed:
Memory updates needed:
Risks:
Next:
```

## Context snapshots

After each phase or major instruction, update the relevant memory files:

- `11_master_context_index.md` for durable project status changes.
- `12_phase_status_matrix.md` for phase state.
- `13_quick_resume.md` for current active task and next action.
- `17_current_system_state.md` for implemented modules and infrastructure.
- `18_task_execution_queue.md` for ready/blocked task changes.
- `09_phase_execution_log.md` for execution details.
- `10_decisions_log.md` for major decisions.

## What to store in memory files

Store:

- Current phase and task state.
- Durable decisions.
- Known blockers.
- Implemented modules.
- Active services and deployment state.
- Test/check status.
- Next recommended action.

Do not store:

- Full command logs.
- Full diffs.
- Repeated copies of roadmap sections.
- Secrets.
- Temporary speculation.
- Large generated output.

## Execution log updates

The execution log should record:

- Phase.
- Date.
- Tasks completed.
- Files changed.
- Tests run.
- Known issues.
- Context snapshot summary.
- Active modules touched.
- Memory files updated.
- Next phase readiness.

## Decision log updates

Update `10_decisions_log.md` when choosing:

- Backend tooling.
- Frontend structure.
- ORM/migration tooling.
- Worker/queue approach.
- AI provider abstraction details.
- Email provider approach.
- Auth/session model.
- Deployment topology.
- Any security-sensitive behavior.

## Synchronization rules

- If phase status changes, update `12_phase_status_matrix.md` and `13_quick_resume.md`.
- If implemented modules change, update `17_current_system_state.md`.
- If next task changes, update `18_task_execution_queue.md`.
- If a blocker appears, update `11_master_context_index.md`, `12_phase_status_matrix.md`, `13_quick_resume.md`, and `18_task_execution_queue.md`.
- If a phase finishes, update all relevant memory files before final response.

## Token minimization rules

- Prefer summaries over copied text.
- Read only relevant files.
- Use targeted searches with `rg`.
- Do not scan generated folders unless needed.
- Keep memory docs concise and current.
