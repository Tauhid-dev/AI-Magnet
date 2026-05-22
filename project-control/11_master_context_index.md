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

- Repository contains planning/control documentation, deterministic roadmap visual assets, a Phase 1 backend foundation, a Phase 2 tenant/database foundation, a Phase 3 RAG ingestion/retrieval foundation, a Phase 4 chat/widget foundation, and a Phase 5 business portal foundation.
- Backend application, database, tenant, AI provider, RAG, chat, widget-key, conversation, and business portal foundations have been implemented.
- No super admin portal, email notification workflow, CI pipeline, or production deployment automation exists yet.
- `project-control/` contains the planning, execution, security, and memory architecture files.
- `project-assets/roadmap/` contains the visual roadmap status JSON, generator script, latest image, and snapshots.
- `backend/` contains the FastAPI app foundation, tenant/database models, RAG services, AI providers, chat/widget services, business portal services/routes, config, health endpoint, requirements, Dockerfile, and tests.
- `backend/migrations/` contains Alembic migration setup, the initial tenant schema migration, the document chunk/vector migration, and the widget config migration.
- `frontend/` contains the Next.js business portal foundation.
- `widget/` contains the lightweight embeddable chat widget and local test page.
- `docker-compose.yml` defines local/dev backend, frontend, PostgreSQL/pgvector, and Redis services.
- Current branch may vary; future sessions must start from latest `master`, pull remote, then branch.

## Current active phase

Phase 5: Business portal.

Current status: READY_FOR_REVIEW.

Next implementation phase after review and explicit instruction: Phase 6: Super admin portal.

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
- Phase 0 visual roadmap system created:
  - Roadmap status JSON.
  - Python/Pillow roadmap generator.
  - Latest roadmap image.
  - Historical snapshot folder.
- Phase 1 backend foundation created:
  - FastAPI app factory.
  - Environment-backed settings.
  - `/health` endpoint.
  - Database and Redis config placeholders.
  - Backend test setup.
  - Dockerfile and Docker Compose foundation.
  - README startup notes.
- Phase 2 tenant/database foundation created:
  - SQLAlchemy 2.x synchronous ORM strategy.
  - Alembic migration setup.
  - Tenant, business, business user, knowledge document, conversation, message, lead, usage log, and audit log models.
  - Tenant-scoped repository helpers.
  - Basic tenant/business service helpers.
  - Local seed helper.
  - Tenant isolation tests.
- Phase 3 RAG ingestion/retrieval foundation created:
  - pgvector-compatible `document_chunks` schema and migration.
  - Portable vector type for PostgreSQL and SQLite validation.
  - AI provider protocols for embeddings and chat completions.
  - OpenAI-compatible provider implementation and deterministic local provider.
  - Plain text/Markdown extraction and chunking helpers.
  - Tenant-scoped ingestion service and worker-style entrypoint.
  - Tenant-first retrieval and RAG isolation tests.
- Phase 4 chat/widget foundation created:
  - Public widget key model and server-side resolver.
  - Widget initialization endpoint.
  - Conversation start and message endpoints.
  - Tenant-filtered RAG-backed AI answer generation.
  - Deterministic lead capture from messages and structured widget fields.
  - Message usage logging.
  - Lightweight static embeddable widget and local test page.
  - Chat/widget tenant isolation tests.
- Phase 5 business portal foundation created:
  - Next.js, TypeScript, and TailwindCSS business portal app under `frontend/`.
  - MVP business portal login/session flow backed by tenant-aware HMAC bearer tokens.
  - Protected portal routes for dashboard, documents, leads, conversations, widget setup, and analytics.
  - Backend `/business-portal` API routes for session, document listing/upload, lead/conversation views, widget key creation, and tenant analytics.
  - Frontend API client, local browser session helper, portal shell, and static validation test.
  - Backend tests covering login/session, cross-tenant denial, document upload, widget key creation, and analytics.

## Pending phases

- Phase 6: Super admin portal.
- Phase 7: Notifications and lead workflow.
- Phase 8: Analytics and usage tracking.
- Phase 9: Security, testing, CI, and deployment.
- Phase 10: Premium/future modules.

## Critical architecture summary

- Multi-tenant SaaS platform with tenant-owned records isolated by `tenant_id`.
- RAG retrieval filters document chunks by active `tenant_id` before scoring or returning results.
- AI provider calls go through embedding and chat-completion provider protocols.
- Public widget keys resolve to a single active tenant on the server and are not private API secrets.
- Browser widget origins are controlled by environment-backed CORS configuration.
- Business portal routes verify the bearer session server-side and filter all data by the verified tenant.
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
- Phase 6 must not start until the user explicitly instructs it.
- Super admin role and authorization model is not defined yet.

## Latest execution state

- Phase 5 business portal foundation exists and validates locally.
- Backend tests passed with `python3 -m pytest backend/tests` - 24 tests.
- Frontend checks passed with `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build`.
- `npm audit --audit-level=high` passed the high-severity gate; npm reported 2 moderate transitive vulnerabilities in the current Next/PostCSS dependency chain.
- Alembic migrations run against SQLite with `env DATABASE_URL=sqlite:///:memory: python3 -m alembic -c backend/alembic.ini upgrade head`.
- Docker Compose config validates with `docker compose config`.
- Business portal route registration validates through app introspection.
- Ruff is selected in dev requirements but was not installed in the current interpreter during validation.
- Next meaningful task, after review and explicit instruction, is Phase 6 task P6-T1: Define super admin role model.

## Next recommended actions

1. Review and merge the Phase 5 business portal foundation branch.
2. Start the next instruction from latest `master`.
3. Read `11_master_context_index.md` and `13_quick_resume.md`.
4. Do not start Phase 6 unless explicitly instructed.
5. When instructed, begin Phase 6 with super admin role model and protected admin portal foundation.
6. Record Phase 6 admin role/routing/audit decisions in `10_decisions_log.md`.
7. Update memory files and roadmap artifacts after each future phase execution.

## Files to read next depending on task type

### Starting any session

- `project-control/11_master_context_index.md`
- `project-control/13_quick_resume.md`
- `project-control/12_phase_status_matrix.md`
- `project-control/18_task_execution_queue.md`
- `project-assets/roadmap/roadmap_status.json` when visual phase status is relevant.

### Backend work

- `project-control/01_architecture_plan.md`
- `project-control/02_phase_roadmap.md` for active phase only.
- `project-control/03_task_dependency_graph.md` for active task IDs only.
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- Relevant `backend/` files for the active task.

### Database work

- `project-control/01_architecture_plan.md`
- `project-control/03_task_dependency_graph.md` Phase 2 and Phase 3 tasks.
- `project-control/06_security_privacy_rules.md`
- `backend/app/db/`, `backend/app/models/`, and `backend/migrations/` files relevant to the task.

### RAG/AI work

- `project-control/01_architecture_plan.md`
- `project-control/03_task_dependency_graph.md` Phase 3 and Phase 4 tasks.
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- `backend/app/rag/`, `backend/app/providers/ai/`, `backend/app/models/knowledge.py`, and relevant tests.

### Frontend work

- `project-control/01_architecture_plan.md`
- `project-control/02_phase_roadmap.md` Phase 5 or Phase 6 as relevant.
- `project-control/03_task_dependency_graph.md` active frontend task IDs.
- `frontend/`, `widget/`, or future `apps/` files relevant to the active task.

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
