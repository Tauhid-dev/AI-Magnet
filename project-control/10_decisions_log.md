# Decisions Log

Use this file to record major product, architecture, tooling, security, and deployment decisions.

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
