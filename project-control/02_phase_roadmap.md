# Phase Roadmap

## Phase 0: Project control and repo setup

### Objective

Create the planning and execution-control structure before application code begins.

### Deliverables

- `project-control/` folder.
- Product vision, architecture plan, phase roadmap, dependency graph, agent model, build rules, security rules, MVP scope, future scope, execution log template, and decision log template.

### Tasks

- Create project-control Markdown files.
- Define phase boundaries and task dependencies.
- Define future agent roles and execution model.
- Define strict build and security rules.

### Dependencies

- Existing repository access.
- Clean git branch created from latest `master`.

### Expected files/folders

- `project-control/00_product_vision.md`
- `project-control/01_architecture_plan.md`
- `project-control/02_phase_roadmap.md`
- `project-control/03_task_dependency_graph.md`
- `project-control/04_agent_execution_model.md`
- `project-control/05_build_rules.md`
- `project-control/06_security_privacy_rules.md`
- `project-control/07_mvp_scope.md`
- `project-control/08_future_scope.md`
- `project-control/09_phase_execution_log.md`
- `project-control/10_decisions_log.md`

### Acceptance criteria

- All listed planning files exist.
- No application code or scaffolding has been created.
- Future Codex sessions can understand the intended architecture, scope, and execution rules.
- Git diff contains only planning/helper Markdown files.

### Suggested agent roles

- Parent Planning Agent.
- Documentation Agent.

### Parallel execution

- Can run in parallel: content drafting can be split by document.
- Merge caution: one agent should reconcile terminology and phase numbering.

## Phase 1: Core backend foundation

### Objective

Establish the FastAPI backend foundation without implementing full product workflows.

### Deliverables

- Backend project structure.
- Configuration loading from environment variables.
- Health endpoint.
- Basic logging.
- Initial test setup.
- Initial Docker service definition for backend if Docker work starts here.

### Tasks

- Create FastAPI app skeleton.
- Add config module and environment variable handling.
- Add health check endpoint.
- Add structured logging baseline.
- Add minimal test runner and first health test.

### Dependencies

- Phase 0 completed.
- Decision recorded for package manager and Python tooling.

### Expected files/folders

- `backend/`
- `backend/app/`
- `backend/tests/`
- `backend/pyproject.toml` or equivalent dependency files.
- Optional `docker-compose.yml` and `infra/` if introduced in this phase.

### Acceptance criteria

- Backend starts locally.
- Health endpoint returns a successful status.
- Config does not hardcode secrets.
- Tests for health endpoint pass.
- Execution log and decision log are updated.

### Suggested agent roles

- Backend Agent.
- DevOps Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: backend skeleton and test setup can be split.
- Should not run in parallel: config decisions and dependency manager selection should be finalized first.

## Phase 2: Tenant and database model

### Objective

Create the database foundation for tenant-isolated SaaS data.

### Deliverables

- PostgreSQL integration.
- Migration tooling.
- Tenant and business tables.
- User/account model where needed.
- Initial tenant-scoped models for documents, conversations, leads, usage, and audit logs.

### Tasks

- Choose and configure ORM/migration tooling.
- Create tenant/business schema.
- Create core tenant-owned tables.
- Add database session lifecycle.
- Add seed/dev data for local development where safe.
- Add tests for tenant isolation assumptions.

### Dependencies

- Phase 1 backend foundation.
- Decision on ORM and migration tool.

### Expected files/folders

- `backend/app/db/`
- `backend/app/models/`
- `backend/migrations/`
- `backend/tests/`
- Updated Docker Compose for PostgreSQL.

### Acceptance criteria

- Migrations run successfully.
- Tenant-owned tables include `tenant_id`.
- Basic tenant CRUD works through internal service or API.
- Tests confirm tenant-scoped queries do not return cross-tenant data.
- Execution log and decision log are updated.

### Suggested agent roles

- Database Agent.
- Backend Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: model drafting and test drafting after schema decisions.
- Should not run in parallel: migration tooling decision and tenant key strategy.

## Phase 3: RAG ingestion and retrieval

### Objective

Build tenant-scoped knowledge ingestion and retrieval using PostgreSQL plus pgvector.

### Deliverables

- Document upload metadata.
- Worker-based ingestion pipeline.
- Text extraction and chunking.
- Embedding provider abstraction.
- Vector storage with `tenant_id`.
- Retrieval service restricted to current tenant.

### Tasks

- Enable pgvector in local/dev database.
- Add document upload and ingestion status model.
- Build text extraction and chunking pipeline.
- Implement embedding provider interface.
- Store embeddings and metadata.
- Implement tenant-scoped retrieval API/service.
- Add tests for no cross-tenant retrieval.

### Dependencies

- Phase 2 database model.
- AI provider abstraction decision.
- Worker/queue baseline from Phase 1 or created here.

### Expected files/folders

- `backend/app/rag/`
- `backend/app/providers/ai/`
- `backend/app/workers/`
- `backend/app/models/document*`
- `backend/tests/rag/`

### Acceptance criteria

- A document can be ingested for a tenant.
- Chunks and embeddings are stored with `tenant_id`.
- Retrieval only returns chunks for the active tenant.
- Ingestion failures are visible and recoverable.
- Tests cover tenant isolation and retrieval basics.
- Execution log and decision log are updated.

### Suggested agent roles

- RAG/AI Agent.
- Database Agent.
- Backend Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: provider abstraction, ingestion status UI/API planning, retrieval tests.
- Should not run in parallel: final vector schema and tenant retrieval contract.

## Phase 4: Chat widget and conversation API

### Objective

Create the customer-facing chat path from embeddable widget to backend conversation API.

### Deliverables

- Conversation and message API.
- Tenant-aware widget initialization.
- Embeddable chat widget.
- RAG-backed answer generation.
- Basic lead capture prompts.
- Usage logging for messages.

### Tasks

- Build widget token/key validation.
- Create conversation start and message endpoints.
- Connect retrieval and AI response generation.
- Build embeddable widget UI bundle.
- Store conversation messages.
- Add deterministic lead capture field collection.
- Add tests for tenant-scoped conversations.

### Dependencies

- Phase 2 tenant/database model.
- Phase 3 retrieval service.
- Provider abstraction for AI chat.

### Expected files/folders

- `backend/app/chat/`
- `backend/app/widget/`
- `backend/app/models/conversation*`
- `widget/` or `frontend/widget/`
- `backend/tests/chat/`

### Acceptance criteria

- A widget can be initialized for a tenant.
- Visitor messages create tenant-scoped conversations.
- AI answers use only current tenant retrieval results.
- Lead capture fields can be collected during conversation.
- Widget can be embedded on a test page.
- Tests cover cross-tenant access denial.
- Execution log and decision log are updated.

### Suggested agent roles

- Backend Agent.
- Frontend Agent.
- RAG/AI Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: widget UI and backend conversation endpoint after API contract is agreed.
- Should not run in parallel: widget auth/key contract and conversation schema.

## Phase 5: Business portal

### Objective

Build the tenant business portal for owners/admins to manage knowledge, leads, conversations, and basic settings.

### Deliverables

- Business portal shell.
- Authentication flow for business users.
- Knowledge base document management.
- Lead list and detail view.
- Conversation history.
- Widget install/configuration view.
- Basic analytics dashboard.

### Tasks

- Create Next.js app structure.
- Add TailwindCSS and shared layout.
- Add business authentication and session handling.
- Build document upload/status views.
- Build leads and conversation views.
- Build widget configuration page.
- Build basic analytics page.

### Dependencies

- Phase 1 backend foundation.
- Phase 2 tenant/user model.
- Phase 3 document ingestion APIs.
- Phase 4 conversation and lead APIs.

### Expected files/folders

- `frontend/` or `apps/business-portal/`
- `frontend/app/`
- `frontend/components/`
- `frontend/lib/api/`
- `frontend/tests/` if frontend testing is introduced.

### Acceptance criteria

- Business user can sign in.
- Business user only sees their tenant data.
- Documents can be uploaded and ingestion status can be viewed.
- Leads and conversations can be reviewed.
- Widget install details are visible.
- Basic analytics render from backend usage data.
- Execution log and decision log are updated.

### Suggested agent roles

- Frontend Agent.
- Backend Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: frontend screens can be split after API contracts are stable.
- Should not run in parallel: authentication/session model and tenant authorization.

## Phase 6: Super admin portal

### Objective

Build the master admin experience for platform operators.

### Deliverables

- Super admin authentication/authorization.
- Tenant management.
- Business account management.
- Usage and system health views.
- Support context views.
- Admin audit logging.

### Tasks

- Define super admin roles and permissions.
- Build tenant list/detail pages.
- Build tenant creation and status management.
- Build usage overview.
- Build system health overview.
- Add audit logging for admin actions.

### Dependencies

- Phase 2 tenant model.
- Phase 5 frontend foundation or shared frontend setup.
- Usage logging model from Phase 4 or Phase 8.

### Expected files/folders

- `frontend/app/admin/` or `apps/admin-portal/`
- `backend/app/admin/`
- `backend/app/audit/`
- `backend/tests/admin/`

### Acceptance criteria

- Only super admins can access admin portal.
- Admins can create and manage tenants.
- Tenant details and usage are visible.
- Admin access to tenant data is audit-logged.
- No business user can access admin-only routes.
- Execution log and decision log are updated.

### Suggested agent roles

- Frontend Agent.
- Backend Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: admin UI and backend admin API after permission contract is agreed.
- Should not run in parallel: role model and audit requirements.

## Phase 7: Notifications and lead workflow

### Objective

Make lead capture reliable and useful for the business through deterministic qualification and email notification.

### Deliverables

- Lead qualification rules.
- Lead status workflow.
- Email notification provider abstraction.
- Business notification settings.
- Notification delivery logging.

### Tasks

- Define lead data fields and qualification rules.
- Implement lead create/update workflow.
- Implement SMTP provider abstraction.
- Queue notification jobs.
- Add delivery logging and retry behavior.
- Add business notification settings.
- Add tests for lead qualification and email dispatch behavior.

### Dependencies

- Phase 2 tenant model.
- Phase 4 chat and lead capture.
- Worker/queue foundation.

### Expected files/folders

- `backend/app/leads/`
- `backend/app/notifications/`
- `backend/app/providers/email/`
- `backend/tests/leads/`
- `backend/tests/notifications/`

### Acceptance criteria

- Qualified leads trigger email notifications.
- Notification failures are logged and retryable.
- Lead status is visible to business users.
- Lead logic is deterministic and testable.
- No notification leaks tenant data.
- Execution log and decision log are updated.

### Suggested agent roles

- Backend Agent.
- DevOps Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: email provider and lead status UI after workflow contract is defined.
- Should not run in parallel: qualification criteria and notification privacy rules.

## Phase 8: Analytics and usage tracking

### Objective

Track basic product usage and provide tenant and admin analytics.

### Deliverables

- Usage event model.
- Tenant analytics API.
- Super admin usage overview.
- Basic dashboards for conversations, leads, document ingestion, and AI usage.

### Tasks

- Define usage event taxonomy.
- Implement usage logging service.
- Add tenant analytics queries.
- Add admin aggregate analytics queries.
- Build business analytics UI.
- Build admin usage UI.
- Add tests for tenant-scoped analytics.

### Dependencies

- Phase 2 tenant model.
- Phase 4 conversations.
- Phase 7 lead workflow.
- Phase 5 and Phase 6 portal foundations.

### Expected files/folders

- `backend/app/usage/`
- `backend/app/analytics/`
- `frontend/app/analytics/`
- `frontend/app/admin/usage/`
- `backend/tests/analytics/`

### Acceptance criteria

- Usage events are recorded with `tenant_id` where tenant-scoped.
- Business analytics only show current tenant data.
- Super admin can view aggregate usage.
- Dashboards render without exposing other tenants.
- Execution log and decision log are updated.

### Suggested agent roles

- Backend Agent.
- Frontend Agent.
- Database Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: analytics UI and query tests after event taxonomy is agreed.
- Should not run in parallel: event taxonomy and aggregation privacy rules.

## Phase 9: Security, testing, CI, and deployment

### Objective

Harden the MVP for reliable development and first deployment.

### Deliverables

- Security review fixes.
- Expanded test coverage.
- CI workflow.
- Docker Compose local/dev deployment.
- Nginx configuration.
- Deployment notes for OCI VPS.
- Backup and environment secret guidance.

### Tasks

- Run tenant isolation review.
- Add missing backend and frontend tests.
- Add lint/type/test CI pipeline.
- Finalize Docker Compose services.
- Add Nginx routing configuration.
- Document environment variables and secrets.
- Document deployment and rollback process.

### Dependencies

- Phases 1 through 8 complete enough for integration.
- Decision on deployment layout.

### Expected files/folders

- `.github/workflows/`
- `docker-compose.yml`
- `infra/nginx/`
- `docs/deployment.md`
- `docs/security.md`
- Updated test folders.

### Acceptance criteria

- CI runs tests and lint/type checks where configured.
- Local Docker Compose environment starts successfully.
- Tenant isolation tests pass.
- Deployment documentation is practical and complete.
- Security and privacy rules are reviewed against implementation.
- Execution log and decision log are updated.

### Suggested agent roles

- DevOps Agent.
- Security Agent.
- QA/Test Agent.
- Backend Agent.
- Frontend Agent.
- Documentation Agent.

### Parallel execution

- Can run in parallel: docs, CI, and test expansion if ownership is split clearly.
- Should not run in parallel: final deployment topology changes without coordination.

## Phase 10: Premium/future modules

### Objective

Plan and implement premium modules only after the MVP is stable.

### Deliverables

- Future module plans.
- Optional prototypes behind feature flags.
- Clear commercial packaging decisions.

### Tasks

- Evaluate Voice AI.
- Evaluate WhatsApp and SMS add-ons.
- Evaluate Stripe billing.
- Evaluate advanced CRM integrations.
- Evaluate n8n automation.
- Evaluate local model/Ollama support.
- Evaluate multi-region architecture.

### Dependencies

- MVP completion and operational learnings.
- Customer demand validation.
- Security and privacy review for each module.

### Expected files/folders

- Future module folders only when approved.
- `docs/future-modules/`
- Feature flag configuration where needed.

### Acceptance criteria

- No future-scope module is implemented before explicit approval.
- Each premium feature has a documented scope, risks, costs, and data-flow review.
- MVP stability is not degraded.
- Execution log and decision log are updated.

### Suggested agent roles

- Parent Planning Agent.
- Product/Documentation Agent.
- Backend Agent.
- Frontend Agent.
- RAG/AI Agent.
- DevOps Agent.
- Security Agent.
- QA/Test Agent.

### Parallel execution

- Can run in parallel: research and planning for independent modules.
- Should not run in parallel: production implementation of multiple premium modules without a release plan.
