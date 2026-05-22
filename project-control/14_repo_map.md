# Repository Map

## Current repository shape

The repository currently contains planning/control documentation, visual roadmap assets, the Phase 1 backend foundation, the Phase 2 tenant/database foundation, the Phase 3 RAG ingestion/retrieval foundation, the Phase 4 chat/widget foundation, the Phase 5 business portal foundation, and the Phase 6 super admin portal foundation.

| Path | Current status | Purpose |
|---|---|---|
| `Readme.md` | Exists | Minimal repository README. Future notes should append or edit carefully, not overwrite blindly. |
| `project-control/` | Exists | Planning, phase control, safety rules, memory, and context recovery docs. |
| `project-assets/roadmap/` | Exists | Deterministic visual roadmap status, generator, latest PNG, and historical snapshots. |
| `backend/` | Exists | FastAPI backend foundation, tenant/database/admin models, RAG services, AI provider abstractions, chat/widget services, business portal routes/services, super admin routes/services, audit helpers, migrations, health endpoint, config, requirements, Dockerfile, and tests. |
| `frontend/` | Exists | Next.js, TypeScript, and TailwindCSS business portal and super admin portal foundation. |
| `widget/` | Exists | Lightweight static embeddable website chat widget and local test page. |
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
- `.gitignore`
- `docker-compose.yml`
- `backend/Dockerfile`
- `backend/alembic.ini`
- `backend/migrations/`
  - `backend/migrations/versions/20260522_0001_initial_tenant_schema.py`
  - `backend/migrations/versions/20260522_0002_document_chunks_vector.py`
  - `backend/migrations/versions/20260522_0003_widget_configs.py`

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

Created across Phases 1 through 6:

- `backend/app/main.py`: FastAPI app factory and application instance.
- `backend/app/core/config.py`: Environment-backed settings.
- `backend/app/core/logging.py`: Logging setup.
- `backend/app/api/router.py`: Top-level API router.
- `backend/app/api/health.py`: `/health` route.
- `backend/app/api/widget.py`: Public widget initialization route.
- `backend/app/api/chat.py`: Public conversation start and message routes.
- `backend/app/api/business_portal.py`: Tenant-aware business portal session, document, lead, conversation, widget, and analytics routes.
- `backend/app/api/admin.py`: Super admin session, tenant management, support context, usage, health, and audit routes.
- `backend/app/schemas/health.py`: Health response schema.
- `backend/app/schemas/widget.py`: Widget request/response schemas.
- `backend/app/schemas/chat.py`: Conversation, message, and lead capture schemas.
- `backend/app/schemas/business_portal.py`: Business portal request/response schemas.
- `backend/app/schemas/admin.py`: Super admin request/response schemas.
- `backend/app/db/config.py`: Database URL placeholder helper.
- `backend/app/db/base.py`: SQLAlchemy base and common mixins.
- `backend/app/db/session.py`: SQLAlchemy engine/session helpers.
- `backend/app/db/repository.py`: Tenant-scoped repository helper.
- `backend/app/db/seed.py`: Explicit local seed helper, including local super admin seed support.
- `backend/app/db/vector.py`: Portable vector type that compiles to pgvector on PostgreSQL and text on SQLite tests.
- `backend/app/models/`: Admin, tenant, business, document, conversation, message, lead, usage, and audit ORM models.
- `backend/app/models/admin.py`: Global platform admin user model.
- `backend/app/models/knowledge.py`: Knowledge document and document chunk ORM models.
- `backend/app/models/widget.py`: Tenant-scoped public widget configuration model.
- `backend/app/providers/ai/`: AI provider protocols, deterministic local provider, OpenAI-compatible provider, and factories.
- `backend/app/ai/`: Compatibility exports for AI provider abstractions.
- `backend/app/rag/`: Text extraction, chunking, ingestion, retrieval, and scoring helpers.
- `backend/app/chat/`: Conversation orchestration, RAG answer generation, usage logging, and deterministic lead capture.
- `backend/app/widget/`: Public widget key hashing, resolution, creation, and revocation helpers.
- `backend/app/business/`: Business portal auth/session and tenant-scoped query services.
- `backend/app/admin/`: Super admin auth/session and data services.
- `backend/app/audit/`: Tenant-scoped audit logging helpers.
- `backend/app/workers/`: Worker-style RAG ingestion entrypoint.
- `backend/app/tenants/`: Tenant/business service helpers.
- `backend/app/leads/`: Placeholder for later lead workflow.
- `backend/app/conversations/`: Reserved package for future conversation-specific helpers.
- `backend/tests/`: Backend health/config, tenant, and RAG tests.
- `backend/tests/test_tenant_models.py`: Phase 2 tenant CRUD and isolation tests.
- `backend/tests/rag/`: Phase 3 provider, chunking, ingestion, and retrieval isolation tests.
- `backend/tests/chat/`: Phase 4 widget initialization, conversation, lead capture, and cross-tenant denial tests.
- `backend/tests/business/`: Phase 5 business portal login/session, cross-tenant denial, document, widget, and analytics tests.
- `backend/tests/admin/`: Phase 6 admin session, business-token rejection, tenant management, support, usage, health, and audit tests.
- `backend/requirements.txt`: Runtime dependencies.
- `backend/requirements-dev.txt`: Dev/test/lint dependencies.
- `backend/Dockerfile`: Backend image definition.

## Frontend structure

Created in Phase 5:

- `frontend/app/`: Next.js App Router routes for login, business portal, and admin portal sections.
- `frontend/app/login/page.tsx`: Business portal login screen.
- `frontend/app/portal/layout.tsx`: Protected portal layout.
- `frontend/app/portal/page.tsx`: Dashboard summary.
- `frontend/app/portal/documents/page.tsx`: Knowledge base document list and text upload.
- `frontend/app/portal/leads/page.tsx`: Lead list and selected lead detail.
- `frontend/app/portal/conversations/page.tsx`: Conversation list and message history.
- `frontend/app/portal/widget/page.tsx`: Widget status, key creation, and embed snippet.
- `frontend/app/portal/analytics/page.tsx`: Basic tenant analytics.
- `frontend/components/`: Portal shell, status pill, and metric card components.
- `frontend/lib/api/`: Typed business portal API client and response types.
- `frontend/lib/auth/`: Browser session storage helper.
- `frontend/tests/static-check.mjs`: Frontend static project-shape validation.
- `frontend/package.json`: Next.js scripts and dependencies.

Created in Phase 6:

- `frontend/app/admin/login/page.tsx`: Super admin login screen.
- `frontend/app/admin/page.tsx`: Super admin overview.
- `frontend/app/admin/tenants/page.tsx`: Tenant list and tenant creation.
- `frontend/app/admin/tenants/[tenantId]/page.tsx`: Tenant detail, status management, and support context.
- `frontend/app/admin/usage/page.tsx`: Platform usage overview.
- `frontend/app/admin/health/page.tsx`: System health view.
- `frontend/app/admin/audit/page.tsx`: Recent tenant-scoped admin audit logs.
- `frontend/components/AdminShell.tsx`: Protected admin shell and navigation.
- `frontend/lib/auth/admin-session.ts`: Browser admin session storage helper.

## Widget structure

Created in Phase 4:

- `widget/chat-widget.js`: Lightweight embeddable browser widget.
- `widget/test-embed.html`: Local embed test page.
- `widget/README.md`: Basic embed usage notes.

Planned future areas:

- Bundled/minified widget build if needed.
- Widget theming/configuration from the business portal.
- Browser automation checks once a dev server or widget build pipeline exists.

## Database and migration location

Created:

- `backend/app/db/`
- `backend/app/models/`
- `backend/migrations/`
- `backend/migrations/versions/20260522_0001_initial_tenant_schema.py`
- `backend/migrations/versions/20260522_0002_document_chunks_vector.py`
- `backend/migrations/versions/20260522_0003_widget_configs.py`
- `backend/migrations/versions/20260522_0004_admin_users.py`

## Deployment files

Created across Phases 1 through 6:

- `docker-compose.yml`
  - Backend service.
  - Frontend service.
  - PostgreSQL/pgvector service.
  - Redis service.

Planned future areas:

- `infra/nginx/`
- `docs/deployment.md`

## Test structure

Created across Phases 1 through 5:

- `backend/tests/`
- `backend/tests/test_tenant_models.py`
- `backend/tests/rag/`
- `backend/tests/chat/`
- `backend/tests/business/`
- `backend/tests/admin/`
- `frontend/tests/`

Planned future areas:

- Notification privacy tests.
