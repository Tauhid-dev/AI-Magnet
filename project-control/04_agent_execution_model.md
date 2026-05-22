# Agent Execution Model

## Purpose

This repository should be executed phase by phase using a parent-agent/sub-agent operating model. If Codex cannot literally spawn sub-agents in a given session, it should simulate the model by splitting work by role, completing independent tasks in parallel where possible, merging carefully, and updating logs before finishing each phase.

## Operating model

### Parent Planning Agent

Responsibilities:

- Own the phase plan and acceptance criteria.
- Keep MVP scope tight.
- Decide task ordering using `03_task_dependency_graph.md`.
- Resolve cross-agent conflicts.
- Ensure `09_phase_execution_log.md` is updated after every phase.
- Ensure `10_decisions_log.md` is updated for major decisions.
- Provide final git diff summary after phase completion.

### Backend Agent

Responsibilities:

- FastAPI application structure.
- API endpoints and service layer.
- Authentication and authorization implementation.
- Lead workflow and notifications.
- Backend tests.
- Provider abstraction integration points.

Must coordinate with:

- Database Agent for schemas and migrations.
- Security Agent for auth and tenant isolation.
- RAG/AI Agent for chat and retrieval flows.

### Frontend Agent

Responsibilities:

- Next.js, TypeScript, and TailwindCSS implementation.
- Business portal.
- Super admin portal.
- Embeddable widget UI.
- API client integration.
- Frontend accessibility and responsive behavior.

Must coordinate with:

- Backend Agent for API contracts.
- Security Agent for auth/session behavior.
- QA/Test Agent for browser and integration checks.

### Database Agent

Responsibilities:

- PostgreSQL schema.
- pgvector setup.
- Migration tooling.
- Tenant-scoped data model.
- Indexes and query patterns.
- Data integrity constraints.

Must coordinate with:

- Backend Agent for ORM/repository patterns.
- Security Agent for tenant isolation and audit logging.
- RAG/AI Agent for vector schema.

### RAG/AI Agent

Responsibilities:

- AI provider abstraction.
- Embedding generation interface.
- Document ingestion pipeline.
- Chunking and retrieval strategy.
- Prompt boundaries and RAG safety constraints.
- Future local model/Ollama compatibility planning.

Must coordinate with:

- Database Agent for vector tables and indexes.
- Backend Agent for chat flow.
- Security Agent for tenant-scoped retrieval.

### DevOps Agent

Responsibilities:

- Docker Compose.
- Redis service.
- Worker service wiring.
- Nginx configuration.
- OCI VPS deployment notes.
- Environment variable documentation.
- CI workflow support.

Must coordinate with:

- Backend Agent and Frontend Agent for service startup commands.
- Security Agent for secret handling.
- QA/Test Agent for CI checks.

### Security Agent

Responsibilities:

- Tenant isolation review.
- Authentication and authorization review.
- PII handling.
- Secret handling.
- Audit logging expectations.
- RAG retrieval boundaries.
- Admin access control.

Must coordinate with:

- Every implementation agent before phase completion.

### QA/Test Agent

Responsibilities:

- Test strategy.
- Backend tests.
- Frontend checks.
- Tenant isolation tests.
- RAG retrieval tests.
- CI validation.
- Regression checks before phase completion.

Must coordinate with:

- Backend Agent for service-level tests.
- Frontend Agent for browser/UI checks.
- Security Agent for privacy and access-control test cases.

### Documentation Agent

Responsibilities:

- Keep planning and execution docs accurate.
- Document environment variables and setup.
- Document deployment and operations.
- Update phase execution log and decision log when delegated.

Must coordinate with:

- Parent Planning Agent for final phase summary.

## Simulating agents in a single Codex session

If literal sub-agents are not available, Codex should:

1. Identify the active phase and relevant task IDs.
2. Split the work by role internally.
3. Execute independent tasks in parallel only when file ownership is clearly separate.
4. Avoid mixing unrelated responsibilities in one change.
5. Merge outputs carefully and inspect the final diff.
6. Run available tests, lint, and type checks before completing the phase.
7. Update `09_phase_execution_log.md`.
8. Update `10_decisions_log.md` for major decisions.
9. Provide a concise phase summary, tests run, known issues, and git diff summary.

## Context minimization rules

- Read `11_master_context_index.md` first and `13_quick_resume.md` second.
- Do not load the full repository before identifying the active phase and task.
- Use `12_phase_status_matrix.md` and `18_task_execution_queue.md` to decide what is ready.
- Load only the relevant phase section, task IDs, rules, and code modules.
- Avoid loading irrelevant code, generated files, logs, or unrelated docs.
- Prefer targeted searches with `rg` and `rg --files`.
- Summarize large outputs instead of copying them into memory files.

## Progressive context loading

Use the smallest context mode that can safely complete the work:

- Small Context Mode: master index, quick resume, phase matrix, task queue, and the specific docs being edited.
- Medium Context Mode: Small Context Mode plus active phase/task details, relevant rules, and directly touched module files.
- Full Context Mode: only for architecture-wide changes, integration issues, CI/deployment work, release readiness, or explicit full-repo review requests.

The parent agent must expand context only when a concrete question, dependency, or failing check requires it.

## Memory checkpointing

After each phase or major instruction, the parent agent should update the relevant memory files:

- `11_master_context_index.md` for durable project status changes.
- `12_phase_status_matrix.md` for phase state.
- `13_quick_resume.md` for the current active phase, blockers, and next action.
- `17_current_system_state.md` for implemented modules and infrastructure.
- `18_task_execution_queue.md` for ready and blocked task changes.
- `09_phase_execution_log.md` for execution details.
- `10_decisions_log.md` for major decisions.

Keep checkpoints concise. Store durable facts, not full logs or full diffs.

## Parallel work rules

- Parallelize read-only exploration and independent implementation tasks.
- Do not parallelize tasks that modify the same files unless one agent clearly owns the merge.
- Do not start frontend API integration before backend API contracts are agreed.
- Do not start RAG retrieval before tenant data boundaries are defined.
- Do not start admin portal work before super admin role rules are defined.
- Do not implement future-scope features while MVP phases are incomplete.

## Handoff format between agents

Each agent handoff should include:

- Task ID.
- Agent role.
- Objective.
- Context loaded.
- Files changed.
- Commands run.
- Tests run.
- Assumptions made.
- Risks or follow-ups.
- Memory files updated or needing update.
- Whether decision log updates are needed.

Handoffs must be concise. Do not repeat full planning context when a pointer to the relevant file is enough.

## Phase completion checklist

- Active task IDs completed or explicitly deferred.
- Acceptance criteria checked.
- Tests/lint/type checks run if available.
- `09_phase_execution_log.md` updated.
- `10_decisions_log.md` updated if a major decision was made.
- `12_phase_status_matrix.md` updated.
- `13_quick_resume.md` updated.
- `17_current_system_state.md` updated when implemented modules or infrastructure changed.
- `18_task_execution_queue.md` updated when task readiness changed.
- Git diff reviewed.
- No future-scope features implemented early.
- Final response includes summary, tests run, and known issues.
