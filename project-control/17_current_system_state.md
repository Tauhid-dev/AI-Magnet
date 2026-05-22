# Current System State

## Last updated

2026-05-23

## Current implemented modules

Phase 10 premium/future module planning is implemented and ready for review. Phase 10 added planning docs only and did not implement any premium module runtime behavior.

Implemented repository assets:

- `project-control/` planning and execution-control documentation.
- Context-recovery and memory-management documentation.
- `project-assets/roadmap/` deterministic visual roadmap assets.
- `project-assets/roadmap/latest_roadmap.png` current visual roadmap image.
- `project-assets/roadmap/snapshots/` historical roadmap image snapshots.
- `backend/` FastAPI foundation with app factory, config, health endpoint, placeholders, requirements, Dockerfile, and tests.
- `backend/migrations/` Alembic migration environment and initial tenant schema migration.
- SQLAlchemy ORM models for global admin users, tenants, businesses, business users, knowledge documents, conversations, messages, leads, usage logs, and audit logs.
- Document chunk model with required `tenant_id`, document ownership, chunk metadata, and embedding storage.
- pgvector-compatible migration that creates `document_chunks` and enables the `vector` extension on PostgreSQL.
- Tenant-scoped repository helper and basic tenant/business service helper.
- AI provider protocols for embeddings and chat completions.
- OpenAI-compatible AI provider using environment-backed API settings.
- Deterministic local AI provider for tests and offline development.
- RAG text extraction, chunking, ingestion, retrieval, and scoring helpers.
- Worker-style RAG ingestion entrypoint.
- RAG tests covering provider mocking, ingestion, unsupported content failure handling, and tenant-first retrieval.
- Widget configuration model with hashed public widget key lookup and revocation support.
- Widget initialization API that validates public keys without exposing tenant IDs.
- Chat conversation API for starting tenant-scoped conversations and posting visitor messages.
- Environment-backed CORS configuration for browser-embedded widget requests.
- Chat service that stores visitor/assistant messages, uses tenant-scoped RAG context, calls the AI provider abstraction, and logs usage events.
- Deterministic lead capture for name, phone, job type, suburb, urgency, and notes.
- Lightweight static embeddable widget and local test embed page under `widget/`.
- Chat/widget tests covering active/revoked widget keys, cross-tenant conversation denial, tenant-only RAG context, usage logging, and lead capture.
- Business portal HMAC bearer-session service with active tenant and business user verification.
- Tenant-scoped business portal API routes for session, documents, leads, conversations, widget setup, and analytics.
- Portal document upload endpoint that ingests plain text/Markdown content for the verified tenant.
- Next.js, TypeScript, and TailwindCSS business portal under `frontend/`.
- Business portal pages for login, dashboard, documents, leads, conversations, widget setup, and analytics.
- Frontend typed API client and browser session helper.
- Frontend static validation test and package lockfile.
- Backend business portal tests covering login/session, cross-tenant denial, document upload, widget key creation, and analytics.
- Global `AdminUser` model and Alembic migration for super admin access.
- Super admin HMAC bearer-session service with active admin and role verification.
- Super admin API routes for tenant list/detail, tenant creation, tenant status management, usage overview, system health, support context, and audit log viewing.
- Tenant-scoped audit service for admin access to tenant data and tenant changes.
- Next.js super admin portal under `frontend/app/admin/`.
- Admin portal pages for login, overview, tenants, tenant detail/support context, usage, health, and audit logs.
- Frontend admin API client and browser session helper.
- Backend admin tests covering admin login/session, business-token rejection, tenant management, limited support context, usage, health, and audit logging.
- Deterministic lead lifecycle workflow that marks leads `needs_info`, `qualified`, `notified`, `contacted`, `closed`, or `disqualified` using backend rules.
- Lead qualification and notification state fields on `leads`.
- Tenant-scoped `business_notification_settings` and `notification_deliveries` ORM models.
- Email provider abstraction with local console and SMTP providers.
- DB-backed notification queue/service with delivery attempts, retry scheduling, sent state, and failure state.
- Chat lead capture integration that queues and sends newly qualified lead notifications.
- Business portal lead status update endpoint and leads UI showing qualification and notification state.
- Backend lead workflow and notification delivery tests.
- Usage event taxonomy and tenant-scoped usage logging service.
- Chat, RAG ingestion, widget key, lead status, and notification workflows recording usage events.
- Tenant analytics query service for documents, conversations, messages, leads, notification deliveries, and usage events.
- Super admin platform analytics query service with aggregate counts, status breakdowns, and per-tenant usage summaries.
- Business portal analytics API and dashboard with usage counts, lead/document status breakdowns, and recent usage events.
- Super admin usage API and dashboard with platform aggregate usage and tenant summaries.
- Backend analytics tests covering tenant isolation and aggregate analytics without raw lead PII.
- Production runtime guardrails for placeholder session secrets, wildcard CORS, and enabled API docs.
- API security headers for content-type sniffing, framing, referrer policy, and browser permissions.
- Long-lived worker process entrypoint for Docker Compose deployment wiring.
- Security-focused backend tests for runtime guardrails, response headers, cross-portal token rejection, and tenant-scoped analytics.
- GitHub Actions CI workflow for backend, frontend, migration, and Compose validation.
- Docker Compose backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx services with healthchecks.
- Nginx reverse proxy config for `/api`, `/health`, and frontend routes.
- Deployment, security, and release-readiness docs under `docs/`.
- Future-module planning docs under `docs/future-modules/` for Voice AI, SMS/WhatsApp messaging, Stripe billing, n8n/CRM automation, local model/Ollama support, and multi-region architecture.
- `.env.example` local configuration template.
- `docker-compose.yml` local/dev backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx foundation.
- `.gitignore` for local env files, Python caches, logs, macOS metadata, and generated frontend artifacts.

## Active infrastructure

Configured but not running in this session:

- Docker Compose foundation with backend, worker, frontend, PostgreSQL/pgvector, Redis, and Nginx. Config validation passes, but full startup was not validated because the Docker daemon is unavailable on this machine.
- Backend service.
- Worker service wiring.
- Frontend service.
- PostgreSQL/pgvector service.
- Redis service.
- Nginx reverse proxy service.
- Alembic migration tooling.
- RAG ingestion worker entrypoint.
- Public chat/widget API routes.
- Business portal API routes.
- Super admin API routes.
- Lead workflow, notification, usage, and analytics services.

Not created yet:

- Production TLS certificate automation.
- Scheduled backup automation.
- Real queue-processing worker implementation.

## Current APIs

Implemented API:

- `GET /health`
- `POST /widget/init`
- `POST /chat/conversations`
- `POST /chat/conversations/{conversation_id}/messages`
- `POST /business-portal/auth/login`
- `GET /business-portal/session`
- `GET /business-portal/documents`
- `POST /business-portal/documents`
- `GET /business-portal/leads`
- `GET /business-portal/leads/{lead_id}`
- `PATCH /business-portal/leads/{lead_id}/status`
- `GET /business-portal/conversations`
- `GET /business-portal/conversations/{conversation_id}`
- `GET /business-portal/widget`
- `POST /business-portal/widget/keys`
- `GET /business-portal/analytics` with tenant-scoped usage and status breakdowns
- `POST /admin/auth/login`
- `GET /admin/session`
- `GET /admin/tenants`
- `POST /admin/tenants`
- `GET /admin/tenants/{tenant_id}`
- `PATCH /admin/tenants/{tenant_id}/status`
- `GET /admin/tenants/{tenant_id}/support-context`
- `GET /admin/usage` with aggregate usage, status breakdowns, and tenant summaries
- `GET /admin/health`
- `GET /admin/audit-logs`

Planned future API groups:

- `/health`
- `/auth`
- `/tenants`
- `/business-portal`
- `/documents`
- `/chat`
- `/leads`
- `/analytics`
- `/usage`
- `/widget`

## Current database state

Initial database schema exists as SQLAlchemy models and Alembic migrations.

Current schema includes tenant-owned tables with required `tenant_id` where tenant isolation applies. The Phase 3 migration adds `document_chunks` with a pgvector-compatible embedding column and enables the PostgreSQL `vector` extension when running on PostgreSQL.

The Phase 4 migration adds `widget_configs` with required `tenant_id`, hashed widget key lookup, key prefix, status, and optional allowed origins.

The Phase 6 migration adds global `admin_users` for platform operators. This table is intentionally not tenant-scoped because super admins are platform-level users, not tenant business users.

The Phase 7 migration adds lead qualification/notification columns to `leads` plus tenant-scoped `business_notification_settings` and `notification_deliveries`.

Phase 8 does not add a new migration. It uses the existing tenant-scoped `usage_logs` table plus existing tenant-owned models for analytics queries.

## Migrations applied

- `20260522_0001`: Initial tenant schema.
- `20260522_0002`: Document chunk vector schema.
- `20260522_0003`: Widget configuration schema.
- `20260522_0004`: Global admin users.
- `20260523_0005`: Lead lifecycle notification schema.

## Active services

None running from this phase. Phase 10 did not add services. Compose configuration validated during Phase 9.

## Deployment status

Local/dev deployment foundation exists through Docker Compose, `backend/Dockerfile`, and `infra/nginx/default.conf`.

Planned deployment target:

- OCI VPS or equivalent single-host Linux server.

## Known technical debt

- Ruff is selected in dev requirements and configured in CI; local Ruff validation passed during Phase 10.
- Full Docker Compose startup could not be validated in this session because the Docker daemon is unavailable.
- PostgreSQL migrations were not run against a live PostgreSQL container in this session; Alembic was validated against SQLite in memory.
- Retrieval currently scores tenant-filtered chunks in Python for MVP simplicity; optimized database vector search can be introduced later.
- Business portal authentication is an MVP email/session contract without passwords, MFA, or external identity provider integration.
- Super admin authentication is an MVP email/session contract without passwords, MFA, or external identity provider integration.
- Rate limiting is not implemented.
- TLS certificate automation is not implemented.
- Scheduled backup automation is documented but not implemented.
- Tenant-scoped audit logging covers tenant-targeted admin actions; global non-tenant admin events may need a separate audit strategy later.
- Notification delivery is DB-backed and processed synchronously in the MVP chat path; the worker service is wired but does not process a queue yet.
- Analytics are computed directly from transactional tables for MVP simplicity; rollups, materialized views, or cache-backed summaries can be introduced if usage volume requires them.
- Local `EMAIL_PROVIDER=console` does not contact SMTP and must be replaced with SMTP settings in production.
- `npm audit --audit-level=high` passed, but npm reported 2 moderate transitive vulnerabilities in the current Next/PostCSS dependency chain.
- The widget is a static MVP asset, not a full frontend build pipeline.
- Worker queue framework choice not made.

## Incomplete modules

- Premium/future modules are documented only. Voice AI, SMS, WhatsApp, Stripe billing, n8n automation, CRM integrations, local model/Ollama support, and multi-region infrastructure are not implemented.

## Update rules

- Update this file whenever implementation state changes.
- Keep it factual and short.
- Do not include full logs or diffs.
- Reflect only what exists in the repository, not what is planned.
