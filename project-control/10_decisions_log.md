# Decisions Log

Use this file to record major product, architecture, tooling, security, and deployment decisions.

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
