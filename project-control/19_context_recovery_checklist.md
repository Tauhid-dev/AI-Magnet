# Context Recovery Checklist

Use this checklist after context reset, new Codex session, or any long interruption.

## Step 1: Read primary memory files

Read:

- `project-control/11_master_context_index.md`
- `project-control/13_quick_resume.md`

Do not load the whole repository first.

## Step 2: Determine active phase

Read:

- `project-control/12_phase_status_matrix.md`
- `project-control/18_task_execution_queue.md`

Identify:

- Active phase.
- Ready task IDs.
- Blocked task IDs.
- Next recommended action.

## Step 3: Load only relevant architecture/task files

Read only what matches the task:

- `project-control/01_architecture_plan.md` for architecture-sensitive tasks.
- Relevant section of `project-control/02_phase_roadmap.md`.
- Relevant task IDs in `project-control/03_task_dependency_graph.md`.
- `project-control/05_build_rules.md`.
- `project-control/06_security_privacy_rules.md` for tenant, auth, AI, RAG, admin, PII, or secret-related work.

## Step 4: Load only relevant code folders

Only after implementation folders exist, load the exact folder needed:

- Backend task: relevant files under `backend/`.
- Frontend task: relevant files under `frontend/`, `apps/`, or `widget/`.
- Database task: models, migrations, and database helpers.
- DevOps task: Docker, infra, CI, and deployment files.
- QA task: relevant tests and touched modules.

Use `rg` or `rg --files` for targeted discovery.

## Step 5: Resume execution

Before making changes:

- Confirm git status.
- Switch to latest `master`.
- Pull remote.
- Create a feature branch.
- Confirm scope and active task.

During work:

- Keep changes scoped.
- Avoid future-scope features.
- Run available checks.

## Step 6: Update logs and memory files after changes

Update as relevant:

- `09_phase_execution_log.md`
- `10_decisions_log.md`
- `11_master_context_index.md`
- `12_phase_status_matrix.md`
- `13_quick_resume.md`
- `17_current_system_state.md`
- `18_task_execution_queue.md`

Record:

- What changed.
- Which modules were touched.
- Tests/checks run.
- Known issues.
- Next action.

## Step 7: Final response

Include:

- Summary of changes.
- Files changed.
- Tests/checks run.
- Known issues or blockers.
- Git diff summary.
- Whether the next phase/task is ready.

Do not continue to the next instruction automatically.
