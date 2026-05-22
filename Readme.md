This is first commit ai-magne

Codex dummy update for branch workflow verification.

# AI Tradie Receptionist Platform

Multi-tenant SaaS platform for Australian tradies and local businesses. Phase 1 adds the backend foundation only: a FastAPI application shell, environment-backed configuration, a health endpoint, basic tests, and Docker Compose support.

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
docker compose up --build backend
```

This starts the backend plus PostgreSQL with pgvector and Redis as development dependencies. Current backend phases include the tenant/database foundation and RAG foundation, but no frontend, chat widget, notification workflow, or production deployment automation yet.

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
