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

- Repository contains planning/control documentation, deterministic roadmap visual assets, Phase 1 through Phase 9 MVP foundations, and Phase 10 premium/future-module planning docs.
- Backend application, database, tenant, AI provider, RAG, chat, widget-key, conversation, business portal, super admin, lead lifecycle, notification, usage logging, analytics, CI, and deployment-hardening foundations have been implemented.
- Production authentication hardening, rate limiting, TLS automation, scheduled backups, and a real queue worker remain future production-readiness work.
- `project-control/` contains the planning, execution, security, and memory architecture files.
- `project-assets/roadmap/` contains the visual roadmap status JSON, generator script, latest image, and snapshots.
- `backend/` contains the FastAPI app foundation, tenant/database models, RAG services, AI providers, email providers, chat/widget services, business portal services/routes, super admin services/routes, lead workflow and notification services, usage and analytics services, security guardrails, worker wiring, audit helpers, config, health endpoint, requirements, Dockerfile, and tests.
- `backend/migrations/` contains Alembic migration setup, tenant schema, document chunk/vector, widget config, admin user, and lead notification migrations.
- `frontend/` contains the Next.js business portal and super admin portal foundations.
- `widget/` contains the lightweight embeddable chat widget and local test page.
- `docker-compose.yml` defines local/dev backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx services.
- `.github/workflows/ci.yml` contains backend, frontend, and Compose validation jobs.
- `infra/nginx/default.conf` contains MVP reverse proxy routing for `/api`, `/health`, and frontend routes.
- `docs/` contains deployment, security, release-readiness, and future-module planning notes.
- Current branch may vary; future sessions must start from latest `master`, pull remote, then branch.

## Current active phase

Phase 10: Premium/future modules.

Current status: READY_FOR_REVIEW.

Next action after review: merge the Phase 10 planning branch. No further product phase should start without a new instruction.

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
- Phase 6 super admin portal foundation created:
  - Global `AdminUser` model and migration separate from tenant business users.
  - MVP super admin login/session flow backed by separate admin HMAC bearer tokens.
  - Protected `/admin` backend APIs for tenant list/detail, tenant creation, tenant status management, usage overview, health, support context, and audit logs.
  - Tenant-scoped audit logging for tenant creation, tenant detail access, support context access, and tenant status changes.
  - Next.js `/admin` portal screens for login, overview, tenants, tenant detail/support context, usage, health, and audit logs.
  - Backend admin tests covering session invalidation, business-token rejection, tenant management, support context PII limiting, health, usage, and audit records.
- Phase 7 notifications and lead workflow created:
  - Deterministic lead qualification workflow using required captured fields.
  - Tenant-scoped lead lifecycle transitions for business portal users.
  - Lead qualification and notification state on lead records.
  - Tenant-scoped business notification settings and delivery log models.
  - DB-backed notification delivery queue with attempts, retry, sent, and failed states.
  - Provider-neutral email abstraction with local console and SMTP providers.
  - Chat lead capture integration that queues/sends newly qualified leads.
  - Business portal lead API and UI updates for qualification, notification, and status updates.
  - Backend tests for lead workflow, notification delivery, and portal status updates.
- Phase 8 analytics and usage tracking created:
  - Formal usage event taxonomy and tenant-scoped usage logging service.
  - Chat, RAG ingestion, widget key, lead status, and notification flows record usage events.
  - Tenant analytics service aggregates documents, conversations, messages, leads, notifications, and usage events by `tenant_id`.
  - Super admin usage overview aggregates platform-level counts without exposing lead PII.
  - Business portal analytics dashboard shows richer metrics, status breakdowns, and recent usage.
  - Super admin usage dashboard shows aggregate usage, status breakdowns, and per-tenant summaries.
  - Backend analytics tests prove tenant analytics do not count another tenant's records.
- Phase 9 security, testing, CI, and deployment created:
  - GitHub Actions CI for backend tests/lint/migrations, frontend lint/type/test/build, and Docker Compose config validation.
  - Docker Compose includes backend, worker, frontend, PostgreSQL/pgvector, Redis, Nginx, and service healthchecks.
  - Nginx reverse proxy routes `/api/*` to the backend and other browser routes to the frontend.
  - Production runtime guardrails reject placeholder secrets, wildcard CORS, and enabled API docs.
  - API responses include conservative security headers.
  - Security tests cover production config, headers, cross-portal token rejection, and tenant-scoped analytics.
  - Deployment, security, and release-readiness documentation exists under `docs/`.
- Phase 10 premium/future module planning created:
  - Voice AI scope, consent, reliability, cost, and architecture planning in `docs/future-modules/voice-ai.md`.
  - SMS and WhatsApp add-on consent, opt-out, provider, and delivery planning in `docs/future-modules/messaging.md`.
  - Stripe billing, subscription, webhook, entitlement, and failure-handling planning in `docs/future-modules/billing.md`.
  - n8n automation, CRM integrations, local model/Ollama support, and multi-region planning in `docs/future-modules/automation-and-local-models.md`.
  - No premium/future product code has been implemented.

## Pending phases

- No numbered project phases remain after Phase 10 review/merge.

## Critical architecture summary

- Multi-tenant SaaS platform with tenant-owned records isolated by `tenant_id`.
- RAG retrieval filters document chunks by active `tenant_id` before scoring or returning results.
- AI provider calls go through embedding and chat-completion provider protocols.
- Public widget keys resolve to a single active tenant on the server and are not private API secrets.
- Browser widget origins are controlled by environment-backed CORS configuration.
- Business portal routes verify the bearer session server-side and filter all data by the verified tenant.
- Super admin routes verify a global admin session server-side and do not accept business portal tokens.
- Tenant-specific admin data access and tenant changes are audit-logged with the target `tenant_id`.
- Lead capture, qualification, and lifecycle transitions use deterministic business logic.
- Email notifications use a provider abstraction with SMTP support and local no-network console delivery.
- Notification delivery state is tenant-scoped and persisted in the database.
- Usage events are recorded through a typed service and remain tenant-scoped for tenant analytics.
- Platform analytics expose aggregate counts and tenant summaries without raw customer lead PII.
- Production mode validates high-risk runtime settings before the FastAPI app starts.
- Nginx should expose the public app and proxy backend API calls through `/api` for hosted deployment.
- CI should run backend, frontend, migration, and Compose checks on branches and pull requests.
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
- Premium/future modules remain planning-only. Implementation of Voice AI, SMS, WhatsApp, Stripe, n8n, CRM integrations, local models, or multi-region infrastructure requires a separate explicit instruction.

## Latest execution state

- Phase 9 was merged to `master` before Phase 10 work began.
- Phase 10 future-module research/scoping docs exist under `docs/future-modules/`.
- Phase 10 intentionally adds no application code, no provider credentials, no feature flags, and no premium module runtime behavior.
- Validation should focus on docs, roadmap generation, and regression checks for the existing MVP.

## Next recommended actions

1. Review and merge the Phase 10 premium/future modules planning branch.
2. Start any future instruction from latest `master`.
3. Read `11_master_context_index.md` and `13_quick_resume.md`.
4. Do not implement premium/future modules unless the user explicitly requests a specific module.
5. When a premium module is requested, begin with the matching `docs/future-modules/` plan and update the decision log.

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
- `project-control/02_phase_roadmap.md` active frontend phase as relevant.
- `project-control/03_task_dependency_graph.md` active frontend task IDs.
- `frontend/`, `widget/`, or future `apps/` files relevant to the active task.

### DevOps work

- `project-control/01_architecture_plan.md`
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- `docker-compose.yml`, `infra/nginx/`, `.github/workflows/`, and `docs/` files relevant to the task.

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
