# Decisions Log

Use this file to record major product, architecture, tooling, security, and deployment decisions.

## DEC-20260522-006: Phase 6 super admin role boundary and audit model

### Decision ID

DEC-20260522-006

### Date

2026-05-22

### Context

Phase 6 requires a master admin portal for platform operators. Super admin access must be distinct from tenant business users, must not rely on tenant membership, and must audit access to tenant data.

### Decision

Add a global `admin_users` table for platform operators and use a separate `/admin` HMAC bearer-session contract backed by `ADMIN_PORTAL_SESSION_SECRET`. Only active `AdminUser` records with the `super_admin` role can authenticate to admin APIs. Keep admin browser session storage separate from business portal storage. Add `/admin` backend routes for tenant management, usage, system health, support context, and audit logs. Reuse existing tenant-scoped `audit_logs` for tenant-specific admin actions such as tenant creation, tenant detail access, support context access, and status changes.

### Alternatives considered

- Treating tenant `BusinessUser` records with a special role as platform admins.
- Reusing business portal tokens for admin APIs.
- Creating a separate admin frontend app immediately.
- Adding a new global audit table before the tenant-scoped audit needs are clearer.

### Reason

Global admin users create a clear authorization boundary and prevent tenant membership from becoming platform access. Separate tokens and browser storage reduce accidental token reuse between portals. Reusing tenant-scoped audit logs is enough for Phase 6 because the required audit events target tenant records.

### Impact

Future production auth must replace the email-only MVP login contract with password, magic-link, or external identity provider verification. Future support/admin actions that are not tenant-specific may need a global audit table or nullable tenant audit strategy before being logged.

## DEC-20260522-005: Phase 5 business portal structure and MVP session contract

### Decision ID

DEC-20260522-005

### Date

2026-05-22

### Context

Phase 5 requires a business portal that can be validated before the super admin portal exists. The portal needs tenant-aware sessions, document upload/listing, lead and conversation views, widget setup, and basic analytics while preserving tenant isolation and keeping future admin work separate.

### Decision

Create one `frontend/` Next.js, TypeScript, and TailwindCSS app for the business portal first, with reusable shell/API/auth patterns that Phase 6 may extend or split later if needed. Add backend `/business-portal` API routes protected by an MVP HMAC bearer-session token. Business portal login resolves an active `BusinessUser` by tenant slug and email, then every protected route reloads the user and tenant context from the token and filters all data by that tenant. Store the bearer token in browser localStorage for the MVP portal session.

### Alternatives considered

- Creating separate `apps/business-portal/` and `apps/admin-portal/` packages immediately.
- Building a mock-only frontend without backend portal routes.
- Delaying business session handling until a full auth provider exists.
- Implementing password or external identity provider flows during Phase 5.

### Reason

A single `frontend/` app keeps the MVP simple and matches the current repo size. Backend-owned session verification keeps tenant filtering server-side instead of trusting browser-provided tenant IDs. The email/session MVP contract is enough to exercise portal UX and tenant isolation tests, while production-grade auth can be hardened in a later security/auth phase.

### Impact

Future Phase 6 work must decide whether to add protected admin routes in the same app or split an admin app. Before production launch, the business auth flow must add password, magic-link, or external IdP verification, tighter token rotation/revocation, and audit logging for sensitive portal actions.

## DEC-20260522-004: Phase 4 public widget key and chat API contract

### Decision ID

DEC-20260522-004

### Date

2026-05-22

### Context

Phase 4 requires a browser-embeddable widget that can initialize without exposing private tenant data, start conversations, send visitor messages, use tenant-scoped RAG context, and capture lead fields predictably. The widget runs on customer websites, so it can only hold public identifiers.

### Decision

Use a public widget key that resolves server-side to exactly one active `WidgetConfig` and tenant. Store only a SHA-256 hash of the widget key plus a short non-secret prefix for support. Add `/widget/init`, `/chat/conversations`, and `/chat/conversations/{conversation_id}/messages` endpoints. Chat messages are stored with the resolved `tenant_id`; cross-tenant widget keys cannot access another tenant's conversation. AI responses use the existing provider abstraction and tenant-filtered RAG retrieval. Lead capture uses deterministic extraction and optional structured fields instead of relying only on LLM output. Add environment-backed CORS configuration so browser-embedded widgets can call the API from approved origins.

### Alternatives considered

- Exposing tenant IDs directly to the widget.
- Treating the widget key as a private API secret.
- Delaying widget key revocation support until a later phase.
- Letting the LLM infer and mutate lead records directly.

### Reason

Public widget keys are appropriate for browser code, but tenant resolution and authorization must remain server-side. Hashing stored keys reduces accidental raw-key exposure. Deterministic lead capture keeps Phase 4 predictable and testable while leaving richer CRM workflows for later phases.

### Impact

Future business portal work should create, display once, rotate, and revoke widget keys through tenant-authorized screens. Future widget/API work must keep tenant resolution server-side and must not expose private tenant IDs, private API keys, or unrelated RAG context to the browser.

## DEC-20260522-003: Phase 3 RAG vector schema and AI provider abstraction

### Decision ID

DEC-20260522-003

### Date

2026-05-22

### Context

Phase 3 requires pgvector-compatible document chunk storage, tenant-scoped ingestion and retrieval, and an AI provider abstraction that can use an OpenAI-compatible API without hardcoding credentials. Automated validation also needs to run without a live PostgreSQL or external AI service.

### Decision

Add a `document_chunks` model and Alembic migration with required `tenant_id`, `document_id`, chunk metadata, and a pgvector-compatible embedding column. Use a small SQLAlchemy `VectorType` wrapper that compiles to `vector(1536)` on PostgreSQL and JSON text on SQLite tests. Add AI provider protocols for embeddings and chat completions, an OpenAI-compatible implementation using `httpx`, and a deterministic local provider for tests/offline development. Keep retrieval tenant-first by filtering chunks by `tenant_id` before scoring in Python.

### Alternatives considered

- Requiring the `pgvector` Python package for all local tests.
- Calling OpenAI APIs directly from RAG services.
- Running retrieval similarity only in SQL from the start.
- Delaying chat provider abstraction until Phase 4.

### Reason

The wrapper keeps migrations pgvector-ready while allowing fast local tests. Provider protocols keep secrets and vendor details out of RAG logic. Tenant-first Python scoring is simple, deterministic, and testable for the MVP foundation, while PostgreSQL vector indexing can be used for optimized retrieval in later phases.

### Impact

Future RAG and chat code must use the provider abstraction instead of direct external API calls. Production embeddings should use vectors matching the configured 1536-dimensional column unless a future migration changes the dimension. Retrieval services must continue filtering by tenant before scoring or returning chunks.

## DEC-20260522-002: Phase 2 database ORM and migration strategy

### Decision ID

DEC-20260522-002

### Date

2026-05-22

### Context

Phase 2 requires PostgreSQL integration, migration tooling, tenant/business schema, initial tenant-owned models, database session lifecycle, and tests proving tenant isolation. The Phase 1 backend already uses FastAPI, environment-backed settings, and Docker Compose with PostgreSQL/pgvector.

### Decision

Use SQLAlchemy 2.x ORM with synchronous sessions for the MVP backend database layer, Alembic for migrations, and `psycopg` as the PostgreSQL driver. Keep database sessions explicit and testable, with tenant-scoped repository helpers requiring a tenant context. Use SQLite only for local automated tests that validate model structure, repository filtering, and migration execution without requiring a running PostgreSQL service.

### Alternatives considered

- SQLAlchemy async sessions with `asyncpg`.
- SQLModel for model/schema consolidation.
- Deferring Alembic migrations until later.
- Using raw SQL repositories.

### Reason

Synchronous SQLAlchemy keeps the MVP backend simpler, works naturally with Alembic, and is enough for current FastAPI service needs. Alembic is needed now so schema changes are repeatable from the beginning. SQLite-based tests give fast tenant isolation validation while Docker Compose remains the PostgreSQL development path.

### Impact

Future phases should continue adding tenant-owned tables through SQLAlchemy models and Alembic migrations. If async database access becomes necessary, it should be recorded as a new decision before changing the session strategy.

## DEC-20260522-001: Phase 1 backend tooling and structure

### Decision ID

DEC-20260522-001

### Date

2026-05-22

### Context

Phase 1 requires a core backend foundation with FastAPI, environment configuration, a health endpoint, test setup, Dockerfile, and Docker Compose foundation. The project already prefers FastAPI, Python, PostgreSQL, Redis, Docker Compose, and provider abstractions.

### Decision

Use a `backend/` package with FastAPI app factory pattern, pip `requirements.txt` and `requirements-dev.txt`, pytest plus httpx for backend tests, and Ruff as the selected lint/format tool for future checks. Use environment variables through a small standard-library settings module for Phase 1. Add Docker Compose with backend, PostgreSQL/pgvector, and Redis services as a local/dev foundation.

### Alternatives considered

- Poetry or uv-based Python project management.
- Pydantic Settings through `pydantic-settings`.
- Deferring Docker Compose until Phase 9.

### Reason

The requirements-file approach matches the requested Phase 1 structure and keeps the initial backend simple. The standard-library settings module avoids introducing extra configuration dependencies before the database and auth layers exist. Docker Compose now gives later phases a stable local service foundation without implementing Phase 2 tenant schema.

### Impact

Future phases can add ORM/migration tooling, tenant models, RAG services, and worker processes inside the established backend structure. If the project later chooses Poetry, uv, or a richer settings library, that decision should be recorded separately before changing the package workflow.

## Decision Template

### Decision ID

DEC-YYYYMMDD-001

### Date

YYYY-MM-DD

### Context

TBD

### Decision

TBD

### Alternatives considered

- TBD

### Reason

TBD

### Impact

TBD
