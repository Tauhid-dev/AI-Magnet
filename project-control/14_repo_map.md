# Repository Map

## Current repository shape

The repository currently contains planning/control documentation, visual roadmap assets, the Phase 1 backend foundation, the Phase 2 tenant/database foundation, and the Phase 3 RAG ingestion/retrieval foundation.

| Path | Current status | Purpose |
|---|---|---|
| `Readme.md` | Exists | Minimal repository README. Future notes should append or edit carefully, not overwrite blindly. |
| `project-control/` | Exists | Planning, phase control, safety rules, memory, and context recovery docs. |
| `project-assets/roadmap/` | Exists | Deterministic visual roadmap status, generator, latest PNG, and historical snapshots. |
| `backend/` | Exists | FastAPI backend foundation, tenant/database models, RAG services, AI provider abstractions, migrations, health endpoint, config, requirements, Dockerfile, and tests. |
| `frontend/` | Not created | Planned Next.js business and/or admin portal. |
| `widget/` | Not created | Planned embeddable website chat widget if kept separate from frontend. |
| `infra/` | Not created | Planned Nginx, deployment, and infrastructure files. |
| `.github/workflows/` | Not created | Planned CI workflows. |
| `docs/` | Not created | Planned setup, deployment, security, and future module docs. |

## Important entrypoint files

- `project-control/11_master_context_index.md`: Read first in every future session.
- `project-control/13_quick_resume.md`: Read second for ultra-small current state.
- `project-control/12_phase_status_matrix.md`: Compact phase status.
- `project-control/18_task_execution_queue.md`: Ready/blocked task queue.
- `project-control/19_context_recovery_checklist.md`: Reset recovery steps.
- `project-control/02_phase_roadmap.md`: Full phase definitions.
- `project-control/03_task_dependency_graph.md`: Detailed task dependency IDs.
- `project-assets/roadmap/roadmap_status.json`: Visual roadmap status source.
- `project-assets/roadmap/generate_roadmap.py`: Deterministic roadmap image generator.

## Planning and governance files

- `project-control/00_product_vision.md`: Product intent and success indicators.
- `project-control/01_architecture_plan.md`: High-level architecture and component plan.
- `project-control/04_agent_execution_model.md`: Parent/sub-agent execution approach.
- `project-control/05_build_rules.md`: Strict implementation and phase rules.
- `project-control/06_security_privacy_rules.md`: Tenant isolation and privacy rules.
- `project-control/07_mvp_scope.md`: MVP boundaries.
- `project-control/08_future_scope.md`: Explicit non-MVP and premium modules.
- `project-control/09_phase_execution_log.md`: Phase completion log template.
- `project-control/10_decisions_log.md`: Decision log template.

## Key infrastructure files

Current infrastructure foundation:

- `.env.example`
- `docker-compose.yml`
- `backend/Dockerfile`
- `backend/alembic.ini`
- `backend/migrations/`
  - `backend/migrations/versions/20260522_0001_initial_tenant_schema.py`
  - `backend/migrations/versions/20260522_0002_document_chunks_vector.py`

Planned future files:

- `infra/nginx/`
- `.github/workflows/`
- `docs/deployment.md`
- `docs/security.md`

## Visual roadmap files

- `project-assets/roadmap/README.md`: How to use the roadmap system.
- `project-assets/roadmap/roadmap_status.json`: Phase/task status source.
- `project-assets/roadmap/generate_roadmap.py`: Python/Pillow image generator.
- `project-assets/roadmap/latest_roadmap.png`: Current roadmap image.
- `project-assets/roadmap/snapshots/`: Historical roadmap images.

## Backend structure

Created across Phases 1 through 3:

- `backend/app/main.py`: FastAPI app factory and application instance.
- `backend/app/core/config.py`: Environment-backed settings.
- `backend/app/core/logging.py`: Logging setup.
- `backend/app/api/router.py`: Top-level API router.
- `backend/app/api/health.py`: `/health` route.
- `backend/app/schemas/health.py`: Health response schema.
- `backend/app/db/config.py`: Database URL placeholder helper.
- `backend/app/db/base.py`: SQLAlchemy base and common mixins.
- `backend/app/db/session.py`: SQLAlchemy engine/session helpers.
- `backend/app/db/repository.py`: Tenant-scoped repository helper.
- `backend/app/db/seed.py`: Explicit local seed helper.
- `backend/app/db/vector.py`: Portable vector type that compiles to pgvector on PostgreSQL and text on SQLite tests.
- `backend/app/models/`: Tenant, business, document, conversation, message, lead, usage, and audit ORM models.
- `backend/app/models/knowledge.py`: Knowledge document and document chunk ORM models.
- `backend/app/providers/ai/`: AI provider protocols, deterministic local provider, OpenAI-compatible provider, and factories.
- `backend/app/ai/`: Compatibility exports for AI provider abstractions.
- `backend/app/rag/`: Text extraction, chunking, ingestion, retrieval, and scoring helpers.
- `backend/app/workers/`: Worker-style RAG ingestion entrypoint.
- `backend/app/tenants/`: Tenant/business service helpers.
- `backend/app/leads/`: Placeholder for later lead workflow.
- `backend/app/conversations/`: Placeholder for Phase 4 conversation APIs.
- `backend/tests/`: Backend health/config, tenant, and RAG tests.
- `backend/tests/test_tenant_models.py`: Phase 2 tenant CRUD and isolation tests.
- `backend/tests/rag/`: Phase 3 provider, chunking, ingestion, and retrieval isolation tests.
- `backend/requirements.txt`: Runtime dependencies.
- `backend/requirements-dev.txt`: Dev/test/lint dependencies.
- `backend/Dockerfile`: Backend image definition.

## Frontend structure

Not created yet.

Planned future areas:

- `frontend/` or `apps/business-portal/`
- `frontend/app/`
- `frontend/components/`
- `frontend/lib/api/`
- `frontend/lib/auth/`
- Admin routes or separate admin portal depending on future decision.

## Widget structure

Not created yet.

Planned future areas:

- `widget/` or `frontend/widget/`
- Widget bundle source.
- Test embed page.
- Widget API client.

## Database and migration location

Created:

- `backend/app/db/`
- `backend/app/models/`
- `backend/migrations/`
- `backend/migrations/versions/20260522_0001_initial_tenant_schema.py`
- `backend/migrations/versions/20260522_0002_document_chunks_vector.py`

## Deployment files

Created across Phases 1 through 3:

- `docker-compose.yml`

Planned future areas:

- `infra/nginx/`
- `docs/deployment.md`

## Test structure

Created in Phase 1:

- `backend/tests/`
- `backend/tests/test_tenant_models.py`
- `backend/tests/rag/`

Planned future areas:

- Frontend tests if introduced.
- Admin authorization tests.
- Notification privacy tests.
