# Task Dependency Graph

## Rules for using this graph

- Treat this file as the task map for future Codex sessions.
- Do not start a task until all `depends_on` tasks are complete or explicitly waived in `10_decisions_log.md`.
- When tasks run in parallel, keep file ownership separate and merge carefully.
- Update `09_phase_execution_log.md` after each phase.
- Update `10_decisions_log.md` for major technical or product decisions.

## Phase 0 tasks

### P0-T1: Create project control documents

- Description: Create the planning and control Markdown files for the repository.
- Phase: Phase 0.
- Depends_on: none.
- Can_run_parallel_with: P0-T2, P0-T3.
- Required_agent_role: Parent Planning Agent, Documentation Agent.
- Output_files: `project-control/*.md`.
- Validation_steps: Confirm all requested files exist; run `git diff --stat`; confirm no app code was created.
- Risk_level: Low.

### P0-T2: Define execution rules

- Description: Document build rules, safety rules, phase logging, and decision logging expectations.
- Phase: Phase 0.
- Depends_on: none.
- Can_run_parallel_with: P0-T1, P0-T3.
- Required_agent_role: Parent Planning Agent, Security Agent, Documentation Agent.
- Output_files: `project-control/05_build_rules.md`, `project-control/06_security_privacy_rules.md`.
- Validation_steps: Confirm rules include tenant isolation, provider abstraction, no hardcoded keys, and phase logging.
- Risk_level: Low.

### P0-T3: Define roadmap and dependencies

- Description: Create the phase roadmap and task dependency graph for future work.
- Phase: Phase 0.
- Depends_on: none.
- Can_run_parallel_with: P0-T1, P0-T2.
- Required_agent_role: Parent Planning Agent, Documentation Agent.
- Output_files: `project-control/02_phase_roadmap.md`, `project-control/03_task_dependency_graph.md`.
- Validation_steps: Confirm phases 0 through 10 exist and each phase has objective, deliverables, tasks, dependencies, expected files, acceptance criteria, agent roles, and parallel notes.
- Risk_level: Low.

## Phase 1 tasks

### P1-T1: Select backend tooling

- Description: Decide Python package manager, FastAPI project layout, test runner, linting, and formatting tools.
- Phase: Phase 1.
- Depends_on: P0-T1, P0-T2, P0-T3.
- Can_run_parallel_with: none.
- Required_agent_role: Backend Agent, QA/Test Agent.
- Output_files: `10_decisions_log.md`, future backend config files.
- Validation_steps: Record decision before scaffolding; confirm tools support local and CI usage.
- Risk_level: Medium.

### P1-T2: Create FastAPI backend foundation

- Description: Create the initial backend app structure with application factory or equivalent startup pattern.
- Phase: Phase 1.
- Depends_on: P1-T1.
- Can_run_parallel_with: P1-T3, P1-T4.
- Required_agent_role: Backend Agent.
- Output_files: `backend/`.
- Validation_steps: Backend imports successfully; server can start locally.
- Risk_level: Medium.

### P1-T3: Add config and environment loading

- Description: Implement typed configuration loaded from environment variables without hardcoded secrets.
- Phase: Phase 1.
- Depends_on: P1-T1.
- Can_run_parallel_with: P1-T2, P1-T4.
- Required_agent_role: Backend Agent, Security Agent.
- Output_files: `backend/app/config*`, `.env.example`.
- Validation_steps: Missing required config fails clearly; no secrets committed.
- Risk_level: Medium.

### P1-T4: Add health endpoint and logging

- Description: Add `/health` endpoint and structured logging baseline.
- Phase: Phase 1.
- Depends_on: P1-T2, P1-T3.
- Can_run_parallel_with: P1-T5.
- Required_agent_role: Backend Agent.
- Output_files: `backend/app/health*`, `backend/app/logging*`.
- Validation_steps: Health endpoint returns success; logs include service and environment context.
- Risk_level: Low.

### P1-T5: Add backend tests

- Description: Add minimal test framework and health endpoint test.
- Phase: Phase 1.
- Depends_on: P1-T2, P1-T4.
- Can_run_parallel_with: none.
- Required_agent_role: QA/Test Agent, Backend Agent.
- Output_files: `backend/tests/`.
- Validation_steps: Test suite passes locally.
- Risk_level: Low.

## Phase 2 tasks

### P2-T1: Select database and migration tooling

- Description: Choose ORM, migration tool, and session management pattern for PostgreSQL.
- Phase: Phase 2.
- Depends_on: P1-T1.
- Can_run_parallel_with: none.
- Required_agent_role: Database Agent, Backend Agent.
- Output_files: `10_decisions_log.md`, future database config.
- Validation_steps: Decision includes migration workflow and async/sync database access strategy.
- Risk_level: Medium.

### P2-T2: Create tenant and business schema

- Description: Add tenant/business tables and core identifiers.
- Phase: Phase 2.
- Depends_on: P2-T1.
- Can_run_parallel_with: P2-T3 after shared conventions are agreed.
- Required_agent_role: Database Agent.
- Output_files: `backend/app/models/tenant*`, migration files.
- Validation_steps: Migration applies cleanly; tenant/business records can be created.
- Risk_level: High.

### P2-T3: Create tenant-owned core data models

- Description: Add initial models for documents, conversations, messages, leads, usage logs, and audit logs with `tenant_id`.
- Phase: Phase 2.
- Depends_on: P2-T1, P2-T2.
- Can_run_parallel_with: P2-T4.
- Required_agent_role: Database Agent, Backend Agent.
- Output_files: `backend/app/models/`.
- Validation_steps: Tenant-owned tables include `tenant_id`; indexes support tenant-scoped queries.
- Risk_level: High.

### P2-T4: Add database session and repository helpers

- Description: Implement database session lifecycle and helpers for tenant-scoped queries.
- Phase: Phase 2.
- Depends_on: P2-T1.
- Can_run_parallel_with: P2-T3.
- Required_agent_role: Backend Agent, Database Agent.
- Output_files: `backend/app/db/`.
- Validation_steps: Sessions open and close correctly; repository helpers require tenant context.
- Risk_level: Medium.

### P2-T5: Add tenant isolation tests

- Description: Validate that tenant-scoped queries do not return another tenant's data.
- Phase: Phase 2.
- Depends_on: P2-T2, P2-T3, P2-T4.
- Can_run_parallel_with: none.
- Required_agent_role: QA/Test Agent, Security Agent.
- Output_files: `backend/tests/tenant_isolation/`.
- Validation_steps: Tests create two tenants and confirm data boundaries.
- Risk_level: High.

## Phase 3 tasks

### P3-T1: Enable pgvector and vector schema

- Description: Add pgvector support and document chunk/embedding tables.
- Phase: Phase 3.
- Depends_on: P2-T1, P2-T3.
- Can_run_parallel_with: P3-T2.
- Required_agent_role: Database Agent, RAG/AI Agent.
- Output_files: migration files, `backend/app/models/document_chunk*`.
- Validation_steps: pgvector extension exists; vector columns support similarity search with tenant filters.
- Risk_level: High.

### P3-T2: Define AI provider abstraction

- Description: Create provider interface for embeddings and chat completions using an OpenAI-compatible provider first.
- Phase: Phase 3.
- Depends_on: P1-T3.
- Can_run_parallel_with: P3-T1, P3-T3.
- Required_agent_role: RAG/AI Agent, Backend Agent.
- Output_files: `backend/app/providers/ai/`.
- Validation_steps: Provider can be mocked in tests; keys come from env vars.
- Risk_level: Medium.

### P3-T3: Build ingestion pipeline

- Description: Implement document upload metadata, text extraction, chunking, embedding generation, and status updates.
- Phase: Phase 3.
- Depends_on: P3-T1, P3-T2.
- Can_run_parallel_with: P3-T4 after provider and schema contracts are stable.
- Required_agent_role: RAG/AI Agent, Backend Agent.
- Output_files: `backend/app/rag/`, `backend/app/workers/`.
- Validation_steps: Sample document ingests to tenant-scoped chunks.
- Risk_level: High.

### P3-T4: Build tenant-scoped retrieval service

- Description: Implement retrieval that always filters by current `tenant_id`.
- Phase: Phase 3.
- Depends_on: P3-T1, P3-T2.
- Can_run_parallel_with: P3-T3.
- Required_agent_role: RAG/AI Agent, Security Agent.
- Output_files: `backend/app/rag/retrieval*`.
- Validation_steps: Retrieval tests prove no cross-tenant chunks are returned.
- Risk_level: High.

### P3-T5: Add RAG tests

- Description: Test ingestion, retrieval, provider mocking, and tenant isolation.
- Phase: Phase 3.
- Depends_on: P3-T3, P3-T4.
- Can_run_parallel_with: none.
- Required_agent_role: QA/Test Agent, RAG/AI Agent.
- Output_files: `backend/tests/rag/`.
- Validation_steps: RAG tests pass using mocked AI provider.
- Risk_level: Medium.

## Phase 4 tasks

### P4-T1: Define widget authentication contract

- Description: Define how a public widget key maps to a tenant without exposing private tenant data.
- Phase: Phase 4.
- Depends_on: P2-T2.
- Can_run_parallel_with: none.
- Required_agent_role: Backend Agent, Security Agent.
- Output_files: `10_decisions_log.md`, future widget config model.
- Validation_steps: Contract supports revocation and tenant lookup without secrets in the browser.
- Risk_level: High.

### P4-T2: Build conversation API

- Description: Add endpoints to start conversations and post visitor messages.
- Phase: Phase 4.
- Depends_on: P2-T3, P4-T1.
- Can_run_parallel_with: P4-T3.
- Required_agent_role: Backend Agent.
- Output_files: `backend/app/chat/`.
- Validation_steps: Messages are stored with `tenant_id`; invalid widget keys are rejected.
- Risk_level: High.

### P4-T3: Connect AI answer generation

- Description: Use tenant-scoped retrieval and AI provider to answer chat messages.
- Phase: Phase 4.
- Depends_on: P3-T4, P4-T2.
- Can_run_parallel_with: P4-T4 after API contract is stable.
- Required_agent_role: RAG/AI Agent, Backend Agent.
- Output_files: `backend/app/chat/`, `backend/app/rag/`.
- Validation_steps: Mocked responses include tenant-specific context only.
- Risk_level: High.

### P4-T4: Build embeddable widget

- Description: Create lightweight website chat widget that initializes by widget key and talks to conversation API.
- Phase: Phase 4.
- Depends_on: P4-T1, P4-T2.
- Can_run_parallel_with: P4-T3, P4-T5.
- Required_agent_role: Frontend Agent.
- Output_files: `widget/` or `frontend/widget/`.
- Validation_steps: Widget renders on a test page and can send/receive messages.
- Risk_level: Medium.

### P4-T5: Add lead capture prompts

- Description: Add deterministic prompts and field tracking for name, contact, job type, suburb, urgency, and notes.
- Phase: Phase 4.
- Depends_on: P4-T2.
- Can_run_parallel_with: P4-T4.
- Required_agent_role: Backend Agent, RAG/AI Agent.
- Output_files: `backend/app/leads/`, `backend/app/chat/`.
- Validation_steps: Lead fields are stored predictably and do not rely only on free-form LLM output.
- Risk_level: Medium.

### P4-T6: Add chat/widget tests

- Description: Test widget initialization, conversation scoping, AI provider mocks, and lead capture behavior.
- Phase: Phase 4.
- Depends_on: P4-T2, P4-T3, P4-T4, P4-T5.
- Can_run_parallel_with: none.
- Required_agent_role: QA/Test Agent.
- Output_files: `backend/tests/chat/`, widget tests if available.
- Validation_steps: Tests pass and include cross-tenant denial cases.
- Risk_level: Medium.

## Phase 5 tasks

### P5-T1: Select frontend structure

- Description: Decide whether business and admin portals share one Next.js app or separate apps.
- Phase: Phase 5.
- Depends_on: P0-T3.
- Can_run_parallel_with: none.
- Required_agent_role: Frontend Agent, Parent Planning Agent.
- Output_files: `10_decisions_log.md`.
- Validation_steps: Decision covers routing, shared components, auth implications, and deployment.
- Risk_level: Medium.

### P5-T2: Create business portal foundation

- Description: Create Next.js, TypeScript, TailwindCSS portal shell.
- Phase: Phase 5.
- Depends_on: P5-T1.
- Can_run_parallel_with: P5-T3.
- Required_agent_role: Frontend Agent.
- Output_files: `frontend/` or `apps/business-portal/`.
- Validation_steps: Frontend starts locally and renders authenticated shell or placeholder route.
- Risk_level: Medium.

### P5-T3: Implement business auth/session flow

- Description: Implement business user authentication and tenant-aware session handling.
- Phase: Phase 5.
- Depends_on: P2-T2, P5-T1.
- Can_run_parallel_with: P5-T2.
- Required_agent_role: Frontend Agent, Backend Agent, Security Agent.
- Output_files: `frontend/lib/auth/`, backend auth routes.
- Validation_steps: Business user cannot access another tenant.
- Risk_level: High.

### P5-T4: Build knowledge base management UI

- Description: Add document upload, list, and ingestion status screens.
- Phase: Phase 5.
- Depends_on: P3-T3, P5-T2, P5-T3.
- Can_run_parallel_with: P5-T5, P5-T6.
- Required_agent_role: Frontend Agent.
- Output_files: frontend document pages/components.
- Validation_steps: User can upload and see status for current tenant only.
- Risk_level: Medium.

### P5-T5: Build leads and conversations UI

- Description: Add pages for lead list/detail and conversation history.
- Phase: Phase 5.
- Depends_on: P4-T2, P4-T5, P5-T2, P5-T3.
- Can_run_parallel_with: P5-T4, P5-T6.
- Required_agent_role: Frontend Agent.
- Output_files: frontend lead and conversation pages/components.
- Validation_steps: Data visible only for current tenant.
- Risk_level: Medium.

### P5-T6: Build widget setup and analytics UI

- Description: Add embed instructions, widget key display, and basic analytics dashboard.
- Phase: Phase 5.
- Depends_on: P4-T1, P5-T2, P5-T3.
- Can_run_parallel_with: P5-T4, P5-T5.
- Required_agent_role: Frontend Agent.
- Output_files: frontend widget and analytics pages/components.
- Validation_steps: Embed code references correct tenant widget key; analytics query is tenant-scoped.
- Risk_level: Medium.

## Phase 6 tasks

### P6-T1: Define super admin role model

- Description: Define admin permissions, access boundaries, and audit requirements.
- Phase: Phase 6.
- Depends_on: P2-T2, P5-T1.
- Can_run_parallel_with: none.
- Required_agent_role: Security Agent, Backend Agent.
- Output_files: `10_decisions_log.md`, future auth/role files.
- Validation_steps: Role model distinguishes super admin from tenant business users.
- Risk_level: High.

### P6-T2: Build admin backend APIs

- Description: Add tenant management, usage overview, support context, and health APIs for super admins.
- Phase: Phase 6.
- Depends_on: P6-T1.
- Can_run_parallel_with: P6-T3.
- Required_agent_role: Backend Agent.
- Output_files: `backend/app/admin/`.
- Validation_steps: Admin-only endpoints reject business users.
- Risk_level: High.

### P6-T3: Build super admin portal UI

- Description: Add admin tenant list/detail, tenant creation, usage, support, and health pages.
- Phase: Phase 6.
- Depends_on: P5-T1, P6-T1.
- Can_run_parallel_with: P6-T2.
- Required_agent_role: Frontend Agent.
- Output_files: admin frontend routes/components.
- Validation_steps: Admin pages are protected and call admin APIs.
- Risk_level: Medium.

### P6-T4: Add admin audit logging

- Description: Record significant admin actions, especially tenant data access and tenant changes.
- Phase: Phase 6.
- Depends_on: P6-T1, P6-T2.
- Can_run_parallel_with: none.
- Required_agent_role: Security Agent, Backend Agent.
- Output_files: `backend/app/audit/`.
- Validation_steps: Tests verify audit records are created.
- Risk_level: High.

## Phase 7 tasks

### P7-T1: Define lead qualification workflow

- Description: Define required fields, qualification states, and deterministic rules.
- Phase: Phase 7.
- Depends_on: P4-T5.
- Can_run_parallel_with: none.
- Required_agent_role: Backend Agent, Parent Planning Agent.
- Output_files: `10_decisions_log.md`, future lead workflow docs/code.
- Validation_steps: Workflow is testable without relying on LLM free-form judgement.
- Risk_level: Medium.

### P7-T2: Implement lead lifecycle

- Description: Implement create/update/status transitions for leads.
- Phase: Phase 7.
- Depends_on: P7-T1.
- Can_run_parallel_with: P7-T3.
- Required_agent_role: Backend Agent.
- Output_files: `backend/app/leads/`.
- Validation_steps: Lead transitions are valid and tenant-scoped.
- Risk_level: Medium.

### P7-T3: Implement email provider abstraction

- Description: Add SMTP provider abstraction and notification templates.
- Phase: Phase 7.
- Depends_on: P1-T3.
- Can_run_parallel_with: P7-T2.
- Required_agent_role: Backend Agent, DevOps Agent.
- Output_files: `backend/app/providers/email/`, `backend/app/notifications/`.
- Validation_steps: Email provider can be mocked; SMTP secrets come from env vars.
- Risk_level: Medium.

### P7-T4: Queue lead notifications

- Description: Queue and send lead notification emails with delivery logging and retry behavior.
- Phase: Phase 7.
- Depends_on: P7-T2, P7-T3.
- Can_run_parallel_with: none.
- Required_agent_role: Backend Agent, DevOps Agent.
- Output_files: `backend/app/notifications/`, worker files.
- Validation_steps: Qualified lead triggers one tenant-correct email notification.
- Risk_level: High.

### P7-T5: Add notification and lead tests

- Description: Test qualification, notification dispatch, retries, and privacy boundaries.
- Phase: Phase 7.
- Depends_on: P7-T2, P7-T4.
- Can_run_parallel_with: none.
- Required_agent_role: QA/Test Agent, Security Agent.
- Output_files: `backend/tests/leads/`, `backend/tests/notifications/`.
- Validation_steps: Tests pass with mocked SMTP provider.
- Risk_level: Medium.

## Phase 8 tasks

### P8-T1: Define usage event taxonomy

- Description: Define events for messages, leads, document ingestion, AI calls, widget loads, and admin actions.
- Phase: Phase 8.
- Depends_on: P2-T3, P4-T2.
- Can_run_parallel_with: none.
- Required_agent_role: Backend Agent, Database Agent.
- Output_files: `10_decisions_log.md`, future usage docs/code.
- Validation_steps: Event taxonomy distinguishes tenant and global events.
- Risk_level: Medium.

### P8-T2: Implement usage logging service

- Description: Add backend service for consistent usage event logging.
- Phase: Phase 8.
- Depends_on: P8-T1.
- Can_run_parallel_with: P8-T3.
- Required_agent_role: Backend Agent.
- Output_files: `backend/app/usage/`.
- Validation_steps: Events are written with `tenant_id` where applicable.
- Risk_level: Medium.

### P8-T3: Build analytics queries

- Description: Add tenant analytics and super admin aggregate analytics queries.
- Phase: Phase 8.
- Depends_on: P8-T1, P8-T2.
- Can_run_parallel_with: P8-T4.
- Required_agent_role: Database Agent, Backend Agent.
- Output_files: `backend/app/analytics/`.
- Validation_steps: Tenant queries cannot return another tenant's data.
- Risk_level: High.

### P8-T4: Build analytics dashboard UI

- Description: Add business and admin analytics dashboard views.
- Phase: Phase 8.
- Depends_on: P5-T2, P6-T3, P8-T3.
- Can_run_parallel_with: none.
- Required_agent_role: Frontend Agent.
- Output_files: frontend analytics pages/components.
- Validation_steps: Dashboards render with test data and respect tenant/admin permissions.
- Risk_level: Medium.

### P8-T5: Add analytics tests

- Description: Test event logging, tenant analytics, and admin aggregate behavior.
- Phase: Phase 8.
- Depends_on: P8-T2, P8-T3.
- Can_run_parallel_with: P8-T4.
- Required_agent_role: QA/Test Agent.
- Output_files: `backend/tests/analytics/`.
- Validation_steps: Tests pass and include cross-tenant denial cases.
- Risk_level: Medium.

## Phase 9 tasks

### P9-T1: Add CI pipeline

- Description: Add GitHub Actions or equivalent workflow for lint, type checks, and tests.
- Phase: Phase 9.
- Depends_on: P1-T5.
- Can_run_parallel_with: P9-T2, P9-T3.
- Required_agent_role: DevOps Agent, QA/Test Agent.
- Output_files: `.github/workflows/`.
- Validation_steps: CI workflow runs expected checks.
- Risk_level: Medium.

### P9-T2: Finalize Docker Compose development environment

- Description: Create or finalize Docker Compose for backend, frontend, worker, PostgreSQL, Redis, and Nginx.
- Phase: Phase 9.
- Depends_on: P1-T2, P2-T1, P3-T1, P5-T2.
- Can_run_parallel_with: P9-T1, P9-T3.
- Required_agent_role: DevOps Agent.
- Output_files: `docker-compose.yml`, `infra/`.
- Validation_steps: Local environment starts and services can communicate.
- Risk_level: High.

### P9-T3: Expand security and tenant isolation tests

- Description: Add final security-focused tests for auth, tenant boundaries, RAG retrieval, admin access, and analytics.
- Phase: Phase 9.
- Depends_on: P2-T5, P3-T5, P4-T6, P6-T4, P8-T5.
- Can_run_parallel_with: P9-T1, P9-T2.
- Required_agent_role: Security Agent, QA/Test Agent.
- Output_files: test folders across backend/frontend.
- Validation_steps: All security tests pass.
- Risk_level: High.

### P9-T4: Add deployment documentation

- Description: Document OCI VPS deployment, Nginx routing, environment variables, backups, and rollback.
- Phase: Phase 9.
- Depends_on: P9-T2.
- Can_run_parallel_with: P9-T3.
- Required_agent_role: Documentation Agent, DevOps Agent.
- Output_files: `docs/deployment.md`, `docs/security.md`.
- Validation_steps: A new operator can follow the steps on a clean VPS plan.
- Risk_level: Medium.

### P9-T5: Run release readiness review

- Description: Confirm MVP meets scope, tests pass, logs are updated, and no future-scope features slipped in.
- Phase: Phase 9.
- Depends_on: P9-T1, P9-T2, P9-T3, P9-T4.
- Can_run_parallel_with: none.
- Required_agent_role: Parent Planning Agent, Security Agent, QA/Test Agent.
- Output_files: `09_phase_execution_log.md`, possible release notes.
- Validation_steps: Test/lint checks pass; diff summary is provided; known issues are recorded.
- Risk_level: High.

## Phase 10 tasks

### P10-T1: Research voice AI module

- Description: Scope voice AI and AI phone calling as a premium module after MVP.
- Phase: Phase 10.
- Depends_on: P9-T5.
- Can_run_parallel_with: P10-T2, P10-T3, P10-T4.
- Required_agent_role: RAG/AI Agent, Parent Planning Agent.
- Output_files: `docs/future-modules/voice-ai.md`.
- Validation_steps: Document privacy, consent, cost, reliability, and infrastructure requirements.
- Risk_level: High.

### P10-T2: Research SMS and WhatsApp modules

- Description: Scope SMS and WhatsApp as premium add-ons.
- Phase: Phase 10.
- Depends_on: P9-T5.
- Can_run_parallel_with: P10-T1, P10-T3, P10-T4.
- Required_agent_role: Backend Agent, Security Agent.
- Output_files: `docs/future-modules/messaging.md`.
- Validation_steps: Document consent, opt-out, provider options, and data handling.
- Risk_level: High.

### P10-T3: Research billing module

- Description: Scope Stripe billing and subscription automation.
- Phase: Phase 10.
- Depends_on: P9-T5.
- Can_run_parallel_with: P10-T1, P10-T2, P10-T4.
- Required_agent_role: Backend Agent, Security Agent.
- Output_files: `docs/future-modules/billing.md`.
- Validation_steps: Document plan model, webhooks, entitlement checks, and failure handling.
- Risk_level: Medium.

### P10-T4: Research automation and local model support

- Description: Scope n8n automation, local model/Ollama support, and advanced integrations.
- Phase: Phase 10.
- Depends_on: P9-T5.
- Can_run_parallel_with: P10-T1, P10-T2, P10-T3.
- Required_agent_role: RAG/AI Agent, DevOps Agent.
- Output_files: `docs/future-modules/automation-and-local-models.md`.
- Validation_steps: Document operational cost, deployment complexity, and security boundaries.
- Risk_level: Medium.
