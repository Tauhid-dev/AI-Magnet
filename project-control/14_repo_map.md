# Repository Map

## Current repository shape

The repository currently contains planning/control documentation only. Application folders are not created yet.

| Path | Current status | Purpose |
|---|---|---|
| `Readme.md` | Exists | Minimal repository README. Future notes should append or edit carefully, not overwrite blindly. |
| `project-control/` | Exists | Planning, phase control, safety rules, memory, and context recovery docs. |
| `backend/` | Not created | Planned FastAPI backend. |
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

None exist yet.

Planned future files:

- `docker-compose.yml`
- `infra/nginx/`
- `.github/workflows/`
- `.env.example`
- `docs/deployment.md`
- `docs/security.md`

## Backend structure

Not created yet.

Planned future areas:

- `backend/app/`
- `backend/app/config*`
- `backend/app/db/`
- `backend/app/models/`
- `backend/app/auth/`
- `backend/app/chat/`
- `backend/app/rag/`
- `backend/app/leads/`
- `backend/app/notifications/`
- `backend/app/providers/ai/`
- `backend/app/providers/email/`
- `backend/app/admin/`
- `backend/tests/`

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

Not created yet.

Planned future areas:

- `backend/app/db/`
- `backend/app/models/`
- `backend/migrations/`

## Deployment files

Not created yet.

Planned future areas:

- `docker-compose.yml`
- `infra/nginx/`
- `docs/deployment.md`

## Test structure

Not created yet.

Planned future areas:

- `backend/tests/`
- Frontend tests if introduced.
- Tenant isolation tests.
- RAG retrieval tests.
- Admin authorization tests.
- Notification privacy tests.
