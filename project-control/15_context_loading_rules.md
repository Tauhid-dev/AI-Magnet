# Context Loading Rules

## Prime rule

Never load the whole repository first. Always start with the smallest useful context.

## Always read first

1. `project-control/11_master_context_index.md`
2. `project-control/13_quick_resume.md`

Then load only what the current task needs.

## Progressive loading sequence

1. Read master index and quick resume.
2. Determine active phase and task IDs.
3. Read `12_phase_status_matrix.md` and `18_task_execution_queue.md`.
4. Read only the relevant phase section in `02_phase_roadmap.md`.
5. Read only the relevant task IDs in `03_task_dependency_graph.md`.
6. Read rules files needed for the task, usually `05_build_rules.md` and `06_security_privacy_rules.md`.
7. Load specific code folders only after they exist and only when the active task touches them.

## Small Context Mode

Use for:

- Status checks.
- Planning-only updates.
- Minor documentation edits.
- Choosing the next task.
- Resuming after context reset.

Load:

- `11_master_context_index.md`
- `13_quick_resume.md`
- `12_phase_status_matrix.md`
- `18_task_execution_queue.md`
- The specific doc being edited.

Do not load:

- Full roadmap.
- Full task graph.
- Whole code folders.
- Unrelated docs.

## Medium Context Mode

Use for:

- Implementing one backend, frontend, database, RAG, DevOps, or QA task.
- Updating a module with known boundaries.
- Adding tests for a specific module.

Load:

- Small Context Mode files.
- Relevant phase section from `02_phase_roadmap.md`.
- Relevant task IDs from `03_task_dependency_graph.md`.
- `05_build_rules.md`.
- `06_security_privacy_rules.md` for sensitive or tenant-related work.
- Specific module files and direct dependencies.

Do not load:

- Unrelated application modules.
- Entire frontend when editing backend.
- Entire backend when editing frontend unless API contracts require it.

## Full Context Mode

Use only when:

- Architecture-wide changes are required.
- A regression crosses multiple modules.
- Integration, CI, deployment, or release readiness requires broad review.
- The user explicitly asks for a full repo review.

Load:

- All project-control files that affect the decision.
- Relevant implementation modules across affected areas.
- Test and infrastructure files for affected systems.

Even in Full Context Mode:

- Prefer `rg` and targeted file reads.
- Avoid dumping large generated outputs.
- Summarize large findings into memory files.

## Task-specific loading

### Backend task

Load:

- Master index.
- Quick resume.
- Active phase/task details.
- Build and security rules.
- Relevant backend files.
- Relevant tests.

### Database task

Load:

- Architecture plan.
- Tenant/security rules.
- Relevant models/migrations.
- Relevant repository/query files.
- Tenant isolation tests.

### RAG task

Load:

- Architecture plan.
- RAG task IDs.
- AI/RAG rules.
- Security/privacy rules.
- Provider, retrieval, ingestion, and vector schema files.

### Frontend task

Load:

- Active frontend phase/task docs.
- API contract or relevant backend route files.
- Relevant frontend routes/components.
- Auth/session rules if applicable.

### DevOps task

Load:

- Build rules.
- Deployment architecture notes.
- Docker, infra, CI, and env example files.
- Service startup commands from package files only as needed.

### Security or QA task

Load:

- Build rules.
- Security/privacy rules.
- Relevant implementation files.
- Relevant tests.
- Logs only when needed and only summarized.

## Output handling

- Summarize large command outputs.
- Do not paste full generated logs into memory files.
- Record only durable state, decisions, blockers, and next actions.
- Keep `13_quick_resume.md` short.
- Keep `11_master_context_index.md` concise.
