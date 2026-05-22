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

This starts the backend plus PostgreSQL with pgvector and Redis as development dependencies. Phase 1 does not create tenant tables, migrations, RAG, frontend, or production deployment automation.

## Database migrations

Phase 2 adds SQLAlchemy ORM models and Alembic migrations for tenant-isolated data. Run migrations from the repository root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

The migration command reads `DATABASE_URL` from the environment. Tenant-owned tables include a required `tenant_id` column, and tenant-scoped repository helpers require an explicit tenant context.
