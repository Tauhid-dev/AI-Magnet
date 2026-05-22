# Current System State

## Last updated

2026-05-22

## Current implemented modules

Phase 4 chat/widget foundation is implemented and ready for review.

Implemented repository assets:

- `project-control/` planning and execution-control documentation.
- Context-recovery and memory-management documentation.
- `project-assets/roadmap/` deterministic visual roadmap assets.
- `project-assets/roadmap/latest_roadmap.png` current visual roadmap image.
- `project-assets/roadmap/snapshots/` historical roadmap image snapshots.
- `backend/` FastAPI foundation with app factory, config, health endpoint, placeholders, requirements, Dockerfile, and tests.
- `backend/migrations/` Alembic migration environment and initial tenant schema migration.
- SQLAlchemy ORM models for tenants, businesses, business users, knowledge documents, conversations, messages, leads, usage logs, and audit logs.
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
- `.env.example` local configuration template.
- `docker-compose.yml` local/dev backend, PostgreSQL/pgvector, and Redis foundation.
- `.gitignore` for local env files, Python caches, logs, and macOS metadata.

## Active infrastructure

Configured but not running in this session:

- Docker Compose foundation.
- Backend service.
- PostgreSQL/pgvector service.
- Redis service.
- Alembic migration tooling.
- RAG ingestion worker entrypoint.
- Public chat/widget API routes.

Not created yet:

- Nginx configuration.
- Frontend service.
- Dedicated worker service.
- CI pipeline.

## Current APIs

Implemented API:

- `GET /health`
- `POST /widget/init`
- `POST /chat/conversations`
- `POST /chat/conversations/{conversation_id}/messages`

Planned future API groups:

- `/health`
- `/auth`
- `/tenants`
- `/business`
- `/admin`
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

## Migrations applied

- `20260522_0001`: Initial tenant schema.
- `20260522_0002`: Document chunk vector schema.
- `20260522_0003`: Widget configuration schema.

## Active services

None running. Compose configuration validates, but services were not started during Phase 4 validation.

## Deployment status

Local/dev deployment foundation exists through Docker Compose and `backend/Dockerfile`.

Planned deployment:

- Nginx reverse proxy.
- OCI VPS target.

## Known technical debt

- Ruff is selected in dev requirements but was not installed in the current interpreter during validation.
- PostgreSQL migrations were not run against a live PostgreSQL container in this session; Alembic was validated against SQLite in memory.
- Retrieval currently scores tenant-filtered chunks in Python for MVP simplicity; optimized database vector search can be introduced later.
- Widget key creation is available through service code but not yet exposed in a business portal.
- The widget is a static MVP asset, not a full frontend build pipeline.
- Frontend app structure decision not made.
- Auth/session model decision not made.
- Worker choice not made.

## Incomplete modules

- Document upload API endpoint.
- Business portal.
- Super admin portal.
- Lead workflow and notifications.
- Analytics and usage tracking.
- CI and deployment.

## Update rules

- Update this file whenever implementation state changes.
- Keep it factual and short.
- Do not include full logs or diffs.
- Reflect only what exists in the repository, not what is planned.
