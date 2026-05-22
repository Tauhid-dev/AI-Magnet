# Architecture Plan

## Architecture summary

The product should be built as a Docker-based multi-tenant SaaS platform with:

- Backend API: FastAPI, Python.
- Frontend applications: Next.js, TypeScript, TailwindCSS.
- Database: PostgreSQL with pgvector enabled.
- Cache and queue: Redis.
- Background processing: Python worker using Celery, RQ, or a simple async worker for MVP.
- Reverse proxy: Nginx.
- Deployment target: OCI VPS using Docker Compose.
- AI provider layer: OpenAI-compatible provider first, future local model or Ollama support.
- Email provider layer: SMTP abstraction.

## High-level components

### Backend API

Responsibilities:

- Tenant and business management.
- Authentication and authorization.
- Chat conversation API.
- RAG query orchestration.
- Lead capture and qualification.
- Email notification dispatch requests.
- Usage logging.
- Admin APIs.
- Health checks and operational diagnostics.

Expected future folder:

- `backend/`

### Background worker

Responsibilities:

- Document parsing and ingestion.
- Embedding generation.
- Vector indexing.
- Async notification delivery.
- Scheduled maintenance tasks.
- Future automation jobs.

Expected future folder:

- `backend/worker/` or `worker/`

### Business portal

Responsibilities:

- Business profile management.
- Knowledge base document upload and status.
- Conversation and lead review.
- Basic analytics.
- Widget embed configuration.

Expected future folder:

- `frontend/` or `apps/business-portal/`

### Super admin portal

Responsibilities:

- Tenant and subscription administration.
- Usage and system health overview.
- Support visibility.
- Admin-only configuration.

Expected future folder:

- `frontend/` or `apps/admin-portal/`

### Embeddable chat widget

Responsibilities:

- Lightweight script for customer websites.
- Tenant-aware initialization using a public tenant/widget key.
- Conversation UI.
- Lead capture prompts.
- Safe API calls to the backend.

Expected future folder:

- `widget/` or `apps/widget/`

### PostgreSQL and pgvector

Responsibilities:

- Source of truth for tenants, users, documents, conversations, leads, audit logs, and usage logs.
- Vector storage for tenant-scoped document chunks.
- Enforce tenant-aware data access at the application layer and, where practical, through constraints or row-level policies.

### Redis

Responsibilities:

- Queue backend.
- Short-lived cache.
- Rate limiting state.
- Temporary job status tracking.

## Multi-tenancy model

All tenant-owned domain data must include `tenant_id` where tenant isolation applies. This includes, at minimum:

- Business profiles.
- Users associated with a tenant.
- Knowledge documents.
- Document chunks and embeddings.
- Chat conversations.
- Chat messages.
- Leads.
- Lead qualification records.
- Usage logs.
- Audit logs where activity is tenant-specific.

Super admin data may be global, but any view into tenant data must be permission-checked and audit-logged.

## Core data flows

### Tenant onboarding

1. Super admin creates tenant/business.
2. Business portal access is configured.
3. Widget configuration or public widget key is generated.
4. Business uploads knowledge documents.
5. Worker ingests documents into tenant-scoped chunks and embeddings.
6. Business installs widget on its website.

### RAG document ingestion

1. Business uploads document in portal.
2. Backend stores metadata and file reference.
3. Worker extracts text.
4. Worker chunks text.
5. Worker creates embeddings using AI provider abstraction.
6. Worker stores chunks and vectors with `tenant_id`.
7. Document status is updated.

### Chat and lead capture

1. Website visitor opens widget.
2. Widget starts or resumes tenant-scoped conversation.
3. Backend validates widget key and tenant.
4. User message is stored.
5. Backend retrieves only current tenant knowledge chunks.
6. AI provider generates an answer using safe prompt constraints.
7. Deterministic lead capture rules request key fields when needed.
8. Qualified lead is stored and notification job is queued.
9. Business receives email notification.
10. Usage and analytics events are logged.

## Provider abstraction plan

AI provider interfaces should separate product logic from vendor-specific APIs.

Initial provider:

- OpenAI-compatible chat completion and embeddings API.

Future providers:

- Local model server.
- Ollama.
- Other hosted LLM providers.

Provider abstractions should cover:

- Chat completions.
- Embeddings.
- Model configuration.
- Retry and timeout behavior.
- Token and cost usage metadata where available.

## Email abstraction plan

The MVP should use SMTP through a provider abstraction so the implementation can later support services such as SES, SendGrid, Mailgun, Postmark, or local SMTP.

Email provider should support:

- Lead notification email.
- Basic templating.
- Delivery result logging.
- Retryable failures through the worker.

## API surfaces

Likely API groups:

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

Exact routes should be decided during backend implementation and recorded in `10_decisions_log.md`.

## Deployment topology

MVP local/dev:

- Docker Compose starts backend, frontend, PostgreSQL with pgvector, Redis, worker, and Nginx where useful.
- Environment variables are loaded from local `.env` files that are excluded from git.

MVP VPS:

- OCI VPS runs Docker Compose.
- Nginx terminates public traffic and routes to frontend/backend services.
- PostgreSQL and Redis run as containers or managed services depending on operational needs.
- Backups must be planned before production data is stored.

## Observability and operations

Minimum operational visibility:

- Health endpoint for API.
- Worker health or heartbeat.
- Structured logs.
- Usage logs per tenant.
- Admin view of tenant ingestion status.
- Error logging for failed document ingestion and notification delivery.

Future:

- Metrics dashboard.
- Alerting.
- Centralized log aggregation.
- Uptime checks.

## Repository direction

The repo should start with planning files only. Future implementation may use a monorepo shape such as:

- `backend/`
- `frontend/`
- `widget/`
- `infra/`
- `docs/`
- `project-control/`

This should not be created until the implementation phase that needs it.
