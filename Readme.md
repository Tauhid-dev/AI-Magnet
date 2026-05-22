This is first commit ai-magne

Codex dummy update for branch workflow verification.

# AI Tradie Receptionist Platform

Multi-tenant SaaS platform for Australian tradies and local businesses. The current foundation includes a FastAPI backend, tenant-isolated database models, tenant-scoped RAG, chat/widget APIs, a Next.js business portal, a protected super admin portal foundation, and tenant-safe usage analytics.

## Backend local setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
python -m pytest backend/tests
uvicorn app.main:app --app-dir backend --reload
```

The API health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

## Docker Compose

Create a local `.env` from `.env.example`, then run:

```bash
docker compose up --build
```

This starts the backend, frontend, PostgreSQL with pgvector, and Redis as development dependencies. Notification workflow, CI, and production deployment automation are still future phases.

## Database migrations

Phase 2 adds SQLAlchemy ORM models and Alembic migrations for tenant-isolated data. Run migrations from the repository root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

The migration command reads `DATABASE_URL` from the environment. Tenant-owned tables include a required `tenant_id` column, and tenant-scoped repository helpers require an explicit tenant context.

## RAG ingestion and retrieval

Phase 3 adds tenant-scoped RAG foundations:

- document chunks with pgvector-compatible embedding storage
- text extraction for plain text/Markdown
- deterministic local embedding provider for tests
- OpenAI-compatible embedding/chat provider abstraction
- tenant-first retrieval service

The PostgreSQL migration enables the `vector` extension when running against PostgreSQL. Local automated tests use SQLite with a portable vector column representation.

## Chat widget and conversation API

Phase 4 adds the public chat path:

- active public widget keys resolve to exactly one tenant
- `/widget/init` validates a widget key without returning tenant IDs
- `/chat/conversations` starts tenant-scoped conversations
- `/chat/conversations/{conversation_id}/messages` stores visitor and assistant messages
- assistant replies use tenant-filtered RAG context and the AI provider abstraction
- deterministic lead capture tracks name, phone, job type, suburb, urgency, and notes

The lightweight embeddable widget lives in `widget/chat-widget.js`, with a local test page at `widget/test-embed.html`.

For local widget smoke tests without an external AI key, set `AI_PROVIDER=local-deterministic`. Set `CORS_ALLOWED_ORIGINS` to the allowed website origins before production deployment.

## Business portal

Phase 5 adds a tenant business portal in `frontend/` using Next.js, TypeScript, and TailwindCSS.

```bash
cd frontend
npm install
npm run dev
```

The portal talks to the backend through `NEXT_PUBLIC_API_BASE_URL`. It includes sign-in, dashboard metrics, knowledge document upload/status, leads, conversations, widget setup, and basic analytics screens.

The Phase 5 sign-in flow is an MVP tenant-aware email/session contract for local validation. Production auth hardening belongs to a later security/auth phase.

## Super admin portal

Phase 6 adds super admin routes in the same `frontend/` app at `/admin` and backend APIs under `/admin`.

Current admin scope:

- super admin login/session contract
- tenant list/detail
- tenant creation and status management
- usage overview
- system health view
- limited tenant support context
- tenant-scoped admin audit logs

Super admins are stored separately from tenant business users in `admin_users`. The current sign-in flow is an MVP email/session contract for local validation and must be hardened before production.

## Lead notifications

Phase 7 adds deterministic lead qualification and tenant-scoped email notification delivery.
Leads move from `new` or `needs_info` to `qualified` only after required contact and job fields are captured.
Qualified leads are queued in `notification_deliveries` and sent through the configured email provider.

Local development uses `EMAIL_PROVIDER=console`, which records a successful delivery without contacting an external SMTP server.
Set `EMAIL_PROVIDER=smtp` plus the `SMTP_*` variables in `.env` to send real lead notifications.
The business portal leads table shows qualification and notification state, and lets business users mark leads as contacted, closed, or disqualified.

## Analytics and usage tracking

Phase 8 adds a tenant-scoped usage event taxonomy and logging service backed by the existing `usage_logs` table.
Chat, RAG ingestion, widget key, lead status, and notification workflows record safe usage events for analytics and future metering.

The business portal analytics page shows tenant-only usage totals, lead/document status breakdowns, notification counts, and recent usage events.
The super admin usage page shows platform aggregate counts, usage breakdowns, and per-tenant summaries without exposing raw lead PII.
