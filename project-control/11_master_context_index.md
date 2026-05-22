# Master Context Index

## Read this first

This is the primary entrypoint for future Codex sessions. Read this file first, then read `13_quick_resume.md`. Do not load the whole repository unless the active task requires broad architecture changes.

## Project overview

AI Tradie Receptionist Platform is a multi-tenant SaaS product for Australian local businesses and tradies. Each business tenant gets a portal, an embeddable website chat widget, tenant-isolated knowledge base data, RAG-backed AI answers, lead capture, lead qualification, and email notifications. A super admin portal manages tenants, usage, support, subscriptions later, and system health.

Technology preference:

- Backend: FastAPI, Python.
- Frontend: Next.js, TypeScript, TailwindCSS.
- Database: PostgreSQL with pgvector.
- Cache/queue: Redis.
- Worker: Python worker using Celery, RQ, or a simple async worker.
- Deployment: Docker Compose, Nginx, OCI VPS.
- AI: provider abstraction using OpenAI-compatible API first, with future local model/Ollama support.
- Email: SMTP provider abstraction.

## Current project status

- Repository contains planning and control documentation only.
- No application code has been implemented.
- No backend, frontend, database, worker, infrastructure, or test scaffold exists yet.
- `project-control/` contains the planning, execution, security, and memory architecture files.
- Current branch may vary; future sessions must start from latest `master`, pull remote, then branch.

## Current active phase

Phase 0: Project control and repo setup.

Current status: READY_FOR_REVIEW after the context-recovery and memory-management layer is merged.

Next implementation phase after review: Phase 1: Core backend foundation.

## Completed phases

- Phase 0 baseline planning documents created:
  - Product vision.
  - Architecture plan.
  - Phase roadmap.
  - Task dependency graph.
  - Agent execution model.
  - Build rules.
  - Security/privacy rules.
  - MVP and future scope.
  - Execution and decision log templates.
- Phase 0 memory architecture extension created:
  - Master context index.
  - Phase status matrix.
  - Quick resume file.
  - Repository map.
  - Context loading rules.
  - Agent memory protocol.
  - Current system state snapshot.
  - Task execution queue.
  - Context recovery checklist.

## Pending phases

- Phase 1: Core backend foundation.
- Phase 2: Tenant and database model.
- Phase 3: RAG ingestion and retrieval.
- Phase 4: Chat widget and conversation API.
- Phase 5: Business portal.
- Phase 6: Super admin portal.
- Phase 7: Notifications and lead workflow.
- Phase 8: Analytics and usage tracking.
- Phase 9: Security, testing, CI, and deployment.
- Phase 10: Premium/future modules.

## Critical architecture summary

- Multi-tenant SaaS platform with tenant-owned records isolated by `tenant_id`.
- RAG retrieval must only return knowledge chunks for the active tenant.
- AI provider calls must go through a provider abstraction.
- Lead capture and qualification should use deterministic business logic where possible.
- Email notifications should use an SMTP provider abstraction.
- Super admin functionality must be role-protected and audit-logged.
- Local/dev deployment should use Docker Compose.

## Important build rules

- Do not implement future-scope features early.
- Do not hardcode API keys or secrets.
- Use environment variables for deployment-specific configuration.
- Every tenant-owned table must include `tenant_id`.
- Every phase must update:
  - `09_phase_execution_log.md`
  - `12_phase_status_matrix.md`
  - `13_quick_resume.md`
  - `17_current_system_state.md`
  - `18_task_execution_queue.md` when queue status changes.
- Every major decision must update `10_decisions_log.md`.
- Before completing a phase, run available tests/lint/type checks.
- After completing a phase, provide a git diff summary.

## Current blockers

- No technical blockers are known.
- Application implementation must wait until the user explicitly starts Phase 1.
- Backend tooling decisions have not been made yet.

## Latest execution state

- Phase 0 planning docs exist.
- Context-recovery memory docs exist.
- No app code exists.
- Next meaningful task is Phase 1 task P1-T1: Select backend tooling.

## Next recommended actions

1. Review and merge the context-recovery branch.
2. Start the next instruction from latest `master`.
3. Read `11_master_context_index.md` and `13_quick_resume.md`.
4. Begin Phase 1 with P1-T1: select backend tooling.
5. Record the tooling decision in `10_decisions_log.md`.
6. Update memory files after the phase or major instruction.

## Files to read next depending on task type

### Starting any session

- `project-control/11_master_context_index.md`
- `project-control/13_quick_resume.md`
- `project-control/12_phase_status_matrix.md`
- `project-control/18_task_execution_queue.md`

### Backend work

- `project-control/01_architecture_plan.md`
- `project-control/02_phase_roadmap.md` for active phase only.
- `project-control/03_task_dependency_graph.md` for active task IDs only.
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- Future `backend/` files only after backend exists.

### Database work

- `project-control/01_architecture_plan.md`
- `project-control/03_task_dependency_graph.md` Phase 2 and Phase 3 tasks.
- `project-control/06_security_privacy_rules.md`
- Future `backend/app/db/`, `backend/app/models/`, and migration files only after they exist.

### RAG/AI work

- `project-control/01_architecture_plan.md`
- `project-control/03_task_dependency_graph.md` Phase 3 and Phase 4 tasks.
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- Future `backend/app/rag/` and `backend/app/providers/ai/` files only after they exist.

### Frontend work

- `project-control/01_architecture_plan.md`
- `project-control/02_phase_roadmap.md` Phase 4, Phase 5, or Phase 6 as relevant.
- `project-control/03_task_dependency_graph.md` active frontend task IDs.
- Future `frontend/`, `widget/`, or `apps/` files only after they exist.

### DevOps work

- `project-control/01_architecture_plan.md`
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- Future `docker-compose.yml`, `infra/`, `.github/workflows/`, and deployment docs only after they exist.

### Security or QA work

- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- `project-control/03_task_dependency_graph.md` relevant test/security tasks.
- Future test folders and implementation files for the touched module only.

## Selective Context Loading Guide

Use the smallest context that can safely complete the task.

If working on backend:

- Read the master index, quick resume, current phase/task docs, build rules, security rules, and only relevant backend files.

If working on RAG:

- Read the master index, quick resume, architecture plan, RAG task IDs, build rules, security rules, and only RAG/provider/database files required by the task.

If working on frontend:

- Read the master index, quick resume, active frontend phase/task docs, API contract docs or backend route files, and only the relevant frontend folder.

If working on DevOps:

- Read the master index, quick resume, build rules, deployment-related architecture notes, and only infrastructure files.

If working on docs:

- Read the master index, quick resume, and the specific docs being edited. Avoid loading unrelated code.

Avoid loading the entire repo unless:

- The task changes architecture-wide contracts.
- A regression spans multiple modules.
- The active phase is integration, CI, deployment, or release readiness.
