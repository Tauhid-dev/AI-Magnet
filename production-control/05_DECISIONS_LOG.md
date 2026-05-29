# Decisions Log

Append-only ADR-lite log for production remediation.

## DEC-PR-20260528-001: Separate Production Remediation From MVP Build History

- Date: 2026-05-28
- Decision: Create `production-control/` as the source of truth for PR-00 through PR-12 production-remediation work, while preserving `project-control/` as historical MVP build evidence and memory.
- Reason: The original MVP Phase 0-10 roadmap tracks build progress and overstates production readiness if reused as launch evidence. The new `PR-*` roadmap maps audit blockers to explicit production gates.
- Affected files/phases: `production-control/*`, `AGENTS.md`, all PR phases.
- Alternatives rejected:
  - Overwrite `project-control/` status files: rejected because it would blur historical MVP implementation state with production remediation.
  - Keep only the audit report: rejected because future Codex runs need executable phase files, status JSON, and visual gates.
- Follow-up impact: Future short commands such as `Implement production phase PR-01` must use `production-control/`, not the historical MVP roadmap.

## DEC-PR-20260528-002: Keep Architecture Generic, Tradie-First

- Date: 2026-05-28
- Decision: Production remediation should preserve AI-Magnet as a reusable multi-tenant RAG agent SaaS, with tradie receptionist as the first-market positioning.
- Reason: Website/sitemap/document ingestion, tenant isolation, source-grounded answers, widget deployment, lead capture, analytics, and admin operations are reusable across many SMB verticals.
- Affected files/phases: PR-00 through PR-12.
- Alternatives rejected:
  - Hard-code tradie-only product concepts into core architecture.
  - Rewrite the platform for a new generic product before hardening.
- Follow-up impact: New code should keep vertical-specific labels/content at UI/config boundaries where practical.

## DEC-PR-20260528-003: PR-00 Does Not Implement Production Remediation

- Date: 2026-05-28
- Decision: PR-00 creates the production-control memory, roadmap, visual status, and protocol only.
- Reason: The user explicitly limited this first run to PR-00. Production feature remediation begins with PR-01.
- Affected files/phases: PR-00.
- Alternatives rejected:
  - Fix auth or infra during PR-00.
  - Mark later phases partially complete because MVP foundations exist.
- Follow-up impact: PR-01 is the next permitted implementation phase.

## DEC-PR-20260528-004: Password Auth With Cookie Sessions For PR-01

- Date: 2026-05-28
- Decision: Implement production authentication using PBKDF2-SHA256 password hashes, per-account failed-login lockout, session-version revocation, and HttpOnly/SameSite browser cookies. Retain bearer-token compatibility for API clients and tests, but the frontend no longer stores bearer tokens in `localStorage`.
- Reason: The current stack can support password auth immediately without introducing an external identity provider. Cookie-backed browser sessions remove the highest-risk token storage issue while keeping existing API structure stable.
- Affected files/phases: PR-01, `backend/app/business/auth.py`, `backend/app/admin/auth.py`, `backend/app/api/*`, `frontend/lib/auth/*`, `frontend/lib/api/client.ts`, migrations and tests.
- Alternatives rejected:
  - Keep email-only auth until an identity provider is selected: rejected because it keeps the critical blocker open.
  - Build a full external IdP integration in PR-01: rejected as too large for the current stack and not necessary to remove the immediate blocker.
- Follow-up impact: PR-02 must complete CSRF/CSP/security-header review for cookie sessions and public endpoint abuse controls.

## DEC-PR-20260528-005: Admin MFA Uses TOTP Enrollment Fields

- Date: 2026-05-28
- Decision: Add admin `mfa_required` and `mfa_secret` fields and require valid TOTP codes when MFA is enabled.
- Reason: This gives the platform a strong admin-authentication path without depending on SMS, email-only codes, or a future premium module.
- Affected files/phases: PR-01, `backend/app/models/admin.py`, `backend/app/core/totp.py`, admin API/tests.
- Alternatives rejected:
  - SMS/WhatsApp MFA: rejected because those channels are explicitly deferred.
  - Email OTP only: rejected because email-only administrator proof is not strong enough for the critical admin-auth blocker.
- Follow-up impact: PR-09 or a later admin UX pass should add guided MFA enrollment/rotation UI; PR-04 should address secret-handling hardening.

## DEC-PR-20260528-006: In-Process Rate Limiter As PR-02 Safety Net

- Date: 2026-05-28
- Decision: Implement app-level in-memory rate limits now, with per-IP plus per-account/tenant/widget/conversation scopes, and leave distributed Redis/proxy enforcement to PR-04/PR-05.
- Reason: PR-02 must remove the immediate no-limit public API blocker without pulling queue/infrastructure work forward. The in-process limiter is deterministic, testable, and enough for a single-process controlled demo.
- Affected files/phases: PR-02, `backend/app/core/rate_limit.py`, `backend/app/api/widget.py`, `backend/app/api/chat.py`, `backend/app/api/business_portal.py`, `backend/app/api/admin.py`.
- Alternatives rejected:
  - Nginx-only limits: rejected for PR-02 because local/API tests would not verify endpoint-specific tenant/widget/account policies.
  - Redis-backed distributed limits: deferred because PR-05 owns the real Redis worker/queue reliability layer and PR-04 owns production topology.
- Follow-up impact: PR-04/PR-05 must harden this into proxy/distributed controls before Gate B can pass in scaled production-like deployment.

## DEC-PR-20260528-007: Widget Origins Required In Production, Optional In Local Dev

- Date: 2026-05-28
- Decision: Add normalized allowed-origin enforcement for widget keys and require `WIDGET_REQUIRE_ALLOWED_ORIGINS=true` for production startup, while keeping local default false for existing developer/demo flows.
- Reason: Public widgets must not be embeddable from arbitrary domains in production, but local development and existing sample tests need a non-breaking path.
- Affected files/phases: PR-02, `backend/app/widget/service.py`, `backend/app/api/business_portal.py`, `frontend/app/portal/widget/page.tsx`, `.env.example`.
- Alternatives rejected:
  - Always deny keys without origins in every environment: rejected because it would break existing local seed/demo usage abruptly.
  - Wildcard origin support: rejected for beta scope because it weakens the control being added.
- Follow-up impact: PR-04 must verify production environment variables and deployment runbooks set widget origin enforcement before any public/private internet demo.

## DEC-PR-20260528-008: Enforce Same-Tenant Relationships With Composite Constraints

- Date: 2026-05-28
- Decision: Add parent unique constraints and child composite foreign keys for tenant-owned relationships where cross-tenant linkage would be dangerous: business users to businesses, chunks to documents, messages/leads to conversations, notification settings to businesses, and notification deliveries to leads.
- Reason: Application-layer `tenant_id` filters are necessary but not sufficient for production SaaS data ownership. The database should reject wrong-tenant parent/child references even if a future service bug attempts to create them.
- Affected files/phases: PR-03, `backend/app/models/*`, `backend/migrations/versions/20260528_0007_pr03_tenant_privacy_integrity.py`, `backend/tests/security/test_pr03_tenant_integrity.py`.
- Alternatives rejected:
  - Rely only on service filters: rejected because it leaves data integrity dependent on every caller being correct.
  - Add PostgreSQL row-level security in PR-03: deferred because the current migration/test stack is SQLAlchemy/Alembic-centric and RLS policy design should happen alongside production PostgreSQL validation in PR-04/PR-12 if chosen.
- Follow-up impact: Future migrations must preserve same-tenant constraints for new tenant-owned relationships.

## DEC-PR-20260528-009: Preserve Admin Evidence Outside Tenant Cascades

- Date: 2026-05-28
- Decision: Add `global_audit_logs` for platform-wide administrator actions and retain tenant-scoped audit logs for ordinary tenant events. Global audit attributes are redacted before storage, and tenant deletion writes retained global evidence before removing tenant data.
- Reason: Tenant-scoped audit logs cascade with tenant deletion, which is appropriate for tenant-owned logs but unsafe for platform evidence of export/offboarding/deletion actions.
- Affected files/phases: PR-03, `backend/app/models/usage.py`, `backend/app/audit/service.py`, `backend/app/admin/service.py`, `backend/app/api/admin.py`.
- Alternatives rejected:
  - Make existing `audit_logs.tenant_id` nullable: rejected because it weakens the clear tenant-scoped table contract and would require broader query/UI changes.
  - Retain all tenant audit logs forever: rejected because it conflicts with deletion/offboarding goals for beta privacy lifecycle.
- Follow-up impact: PR-04/PR-10 must extend PII-safe structured logging and operational audit review without exposing raw customer content.

## DEC-PR-20260528-010: Separate Development And Production Compose Topologies

- Date: 2026-05-28
- Decision: Keep `docker-compose.yml` as the local development topology and add `docker-compose.prod.yml` for production with only Nginx publishing host ports. PostgreSQL and Redis are private internal services in production.
- Reason: The development compose file intentionally exposes developer conveniences. Reusing it for OCI production risks public PostgreSQL/Redis exposure and frontend dev-server deployment.
- Affected files/phases: PR-04, `docker-compose.prod.yml`, `.env.production.example`, `docs/deployment.md`, CI compose checks.
- Alternatives rejected:
  - Mutate development compose into production compose: rejected because it would slow local iteration and mix incompatible requirements.
  - Rely only on firewall rules while still publishing DB/Redis ports: rejected because the secure default should be private Docker networking.
- Follow-up impact: Deployment docs and future VPS work must use `docker-compose.prod.yml`; release validation must confirm no host ports are published for data services.

## DEC-PR-20260528-011: Repository-Controlled PR-04 Stops Before Live Deployment

- Date: 2026-05-28
- Decision: PR-04 provides production topology, TLS/HSTS templates, backup/restore scripts, pgvector migration smoke path, CI scans, and runbooks, but does not execute live DNS, certificate issuance, production database migration, firewall changes, or restore drills.
- Reason: The production phase protocol forbids live VPS deployment or destructive operational actions unless separately instructed. The repository can be verified statically, while live evidence belongs to a later explicit deployment/release gate.
- Affected files/phases: PR-04, `docs/deployment.md`, `production-control/08_VALIDATION_MATRIX.md`, `production-control/07_RISK_REGISTER.md`.
- Alternatives rejected:
  - Run certbot/VPS migration from Codex: rejected because it requires explicit owner permission and live infrastructure access.
  - Mark TLS/backups fully launch-validated after writing scripts only: rejected because first live execution remains release evidence.
- Follow-up impact: PR-05 can proceed after PR-04, but Gate B still needs PR-05 plus successful remote CI/VPS validation evidence.

## DEC-PR-20260528-012: Durable DB Job Ledger With Redis Wake Signals

- Date: 2026-05-28
- Decision: Implement PR-05 with a durable `background_jobs` database ledger and `worker_heartbeats`, using Redis only as a wake signal for queued work.
- Reason: The current stack is synchronous SQLAlchemy plus Redis in Docker Compose. A DB-ledger queue gives durable status, idempotency, tenant ownership, retry visibility, failed-job visibility, and simple admin/tenant APIs without introducing Celery/RQ operational complexity before the ingestion workload is fully expanded in PR-06/PR-07.
- Affected files/phases: PR-05, `backend/app/jobs/*`, `backend/app/models/job.py`, `backend/app/workers/runner.py`, `backend/migrations/versions/20260528_0008_pr05_background_jobs.py`, `docs/worker-queue.md`.
- Alternatives rejected:
  - Keep the placeholder sleep worker: rejected because it leaves ingestion/notification workflows without reliable async execution.
  - Introduce Celery/RQ immediately: deferred because the current product needs observable durable jobs more than a larger framework, and the DB ledger remains compatible with adopting a larger queue later.
- Follow-up impact: PR-06 and PR-07 should add website, sitemap, file extraction, and OCR jobs through this ledger; PR-10 should extend metrics/alerts around queue age, failures, and worker liveness.

## DEC-PR-20260528-013: Authenticated Tenant Owner Website Approval For PR-06 Beta Scope

- Date: 2026-05-28
- Decision: PR-06 authorizes website/sitemap source submission through the authenticated business portal owner. If the business profile has a `website_url`, submitted sources must match that domain or its subdomains. If no business website is configured, the submitted source domain is recorded as the approved tenant source domain.
- Reason: The beta workflow needs safe website/sitemap ingestion without delaying PR-06 for external DNS or file-based verification. Authenticated tenant ownership plus business-domain matching removes the immediate unrestricted crawler risk while preserving a practical onboarding path.
- Affected files/phases: PR-06, `backend/app/rag/website_ingestion.py`, `backend/app/api/business_portal.py`, `frontend/app/portal/documents/page.tsx`, `docs/website-ingestion.md`.
- Alternatives rejected:
  - Require DNS TXT or hosted-file verification immediately: deferred because it is stronger but adds onboarding and support complexity before the controlled pilot phase.
  - Allow arbitrary URLs for any tenant: rejected because it would weaken tenant source ownership and crawler abuse boundaries.
- Follow-up impact: PR-09 customer onboarding may add guided domain verification UX if beta customers need stronger proof. PR-12 should re-evaluate whether authenticated-owner approval remains acceptable for launch.

## DEC-PR-20260528-014: Ordinary HTTP Crawler First, Browser Crawling Deferred

- Date: 2026-05-28
- Decision: Implement PR-06 with a deterministic HTTP crawler, sitemap parser, HTML text extractor, robots.txt handling, SSRF protections, and bounded crawl settings. Browser/Playwright crawling remains conditional.
- Reason: The audit classified browser crawling as conditional, not a production-security blocker. A normal HTTP crawler covers many SMB sites, is easier to bound safely, and avoids adding headless browser runtime and attack surface during PR-06.
- Affected files/phases: PR-06, `backend/app/rag/web_fetcher.py`, `backend/app/rag/web_extraction.py`, `backend/app/rag/website_ingestion.py`.
- Alternatives rejected:
  - Add Playwright crawling now: rejected for PR-06 scope because it increases runtime complexity and SSRF/browser isolation requirements.
  - Defer all website ingestion until PR-09: rejected because website/sitemap ingestion is a product workflow blocker and must exist before RAG quality and onboarding phases.
- Follow-up impact: Add browser crawling only if controlled beta websites cannot be ingested through ordinary HTTP/sitemap paths.

## DEC-PR-20260529-015: Private Local Document Storage With Gated OCR

- Date: 2026-05-29
- Decision: Implement PR-07 document ingestion with authenticated multipart uploads, private local storage rooted at `DOCUMENT_STORAGE_ROOT`, a `rag.document_file_ingestion` job carrying only `document_id`, `pypdf` for selectable PDF text, `python-docx` for DOCX text, deterministic basic malware screening, and fail-closed OCR-required status for scanned PDFs.
- Reason: The current Docker/VPS topology can support private mounted storage immediately without adding object-storage complexity. Keeping raw file bytes out of job payloads reduces accidental exposure, while explicit OCR gating avoids falsely claiming scanned-document support before an OCR runtime is selected and secured.
- Affected files/phases: PR-07, `backend/app/rag/document_validation.py`, `backend/app/rag/document_storage.py`, `backend/app/rag/extraction.py`, `backend/app/jobs/*`, `backend/app/api/business_portal.py`, `frontend/app/portal/documents/page.tsx`, `docker-compose*.yml`, `docs/document-ingestion.md`.
- Alternatives rejected:
  - Store raw file bytes in background job payloads: rejected because customer documents are sensitive and job payload visibility is broader than private storage.
  - Add full OCR runtime immediately: deferred because OCR engine selection, resource limits, malware/quarantine flow, and operational costs need a dedicated hardening pass.
  - Add cloud object storage immediately: deferred because the PR-04 OCI VPS topology does not yet require external storage, and a local abstraction keeps the path replaceable later.
- Follow-up impact: PR-08 can now assume tenant document content exists but must still add scalable SQL pgvector retrieval, citations, thresholds, and RAG safety evaluation. A later OCR/storage hardening pass may replace the local storage backend or add an external scanner without changing the API contract.

## DEC-PR-20260529-016: SQL pgvector Retrieval With SQLite Test Fallback

- Date: 2026-05-29
- Decision: Implement PR-08 production retrieval with a PostgreSQL/pgvector SQL query that filters by tenant and ingested document status inside the database, while retaining a SQLite/Python scoring fallback only for local unit tests.
- Reason: Production must avoid loading every tenant chunk into Python, but the existing local test suite uses in-memory SQLite. Keeping both paths lets CI verify tenant filtering, citations, thresholds, and safety behavior without requiring a local PostgreSQL service for every unit test.
- Affected files/phases: PR-08, `backend/app/rag/retrieval.py`, `backend/migrations/versions/20260529_0011_pr08_pgvector_retrieval_indexes.py`, `backend/tests/rag/test_ingestion_and_retrieval.py`, `docs/rag-quality.md`.
- Alternatives rejected:
  - Keep Python-side scoring as the production path: rejected because it was the audited scalability blocker.
  - Require PostgreSQL for every local test: deferred because the current repo keeps a fast SQLite unit test path; staging/VPS PostgreSQL smoke remains a release-gate validation.
- Follow-up impact: PR-10 should add retrieval latency/cost dashboards and quota enforcement. PR-12 must include production-equivalent PostgreSQL/pgvector retrieval smoke before launch.

## DEC-PR-20260529-017: No-Answer Fallback Before LLM Invocation

- Date: 2026-05-29
- Decision: When no tenant-owned chunks clear the configured similarity threshold, return `RAG_NO_ANSWER_MESSAGE` directly instead of asking the LLM to improvise.
- Reason: The beta product must fail safely when the knowledge base is empty or irrelevant. Avoiding an LLM call in the no-context path reduces hallucination risk and avoids unnecessary provider cost.
- Affected files/phases: PR-08, `backend/app/chat/service.py`, `backend/app/core/config.py`, `.env.example`, `.env.production.example`, `docker-compose*.yml`, `backend/tests/rag/test_rag_safety_eval.py`.
- Alternatives rejected:
  - Always call the LLM with "no context": rejected because it encourages plausible unsupported answers.
  - Hardcode the fallback copy in the service: rejected because launch copy should be configurable by environment.
- Follow-up impact: PR-09 may tune the displayed no-answer copy in the agent test/widget UX; PR-10 can meter saved no-context provider calls.

## DEC-PR-20260529-018: Portal Setup Flow Uses Existing Hardened Tenant APIs

- Date: 2026-05-29
- Decision: Implement PR-09 as an incremental business-portal setup flow over the existing hardened APIs: profile update, knowledge/job status, source-grounded agent sandbox, and widget branding/key controls. The agent sandbox does not create conversations or leads, and portal session hydration can fall back to the HttpOnly cookie session when local storage metadata is unavailable.
- Reason: PR-09 should turn the verified PR-01 through PR-08 capabilities into a beta-ready customer workflow without introducing a parallel onboarding service, a second chat path, or mock/demo-only frontend state.
- Affected files/phases: PR-09, `backend/app/api/business_portal.py`, `backend/app/business/service.py`, `backend/app/widget/service.py`, `frontend/app/portal/onboarding/page.tsx`, `frontend/app/portal/agent/page.tsx`, `frontend/app/portal/widget/page.tsx`, `frontend/components/PortalShell.tsx`, `frontend/lib/auth/session.ts`.
- Alternatives rejected:
  - Create a separate onboarding backend module: rejected because the existing tenant-scoped portal APIs already own the same data and authorization boundaries.
  - Persist sandbox tests as conversations: rejected because sandbox testing should not pollute customer chat history, lead workflows, or analytics meant for real visitors.
  - Require local storage metadata for portal access: rejected because the secure source of truth is the HttpOnly cookie-backed server session.
- Follow-up impact: PR-10 should meter sandbox tests, widget setup changes, and setup completion as part of quota/cost/operations visibility. PR-12 should re-check whether authenticated-owner website approval remains sufficient for public launch.

## DEC-PR-20260529-019: PR-10 Uses Existing Usage Logs For Beta Quotas

- Date: 2026-05-29
- Decision: Implement PR-10 quota, token, and cost metering from existing tenant-scoped `usage_logs`, current conversation/document/crawl rows, and configurable environment limits rather than adding a new rollup table in this phase.
- Reason: The repository already records tenant-scoped usage events and PR-10 needed enforceable beta controls without adding migration complexity or a premature billing schema before PR-11. The design keeps the response/API shape compatible with a future rollup table if usage volume requires it.
- Affected files/phases: PR-10, `backend/app/usage/quotas.py`, `backend/app/analytics/service.py`, `backend/app/api/chat.py`, `backend/app/api/business_portal.py`, `frontend/app/admin/usage/page.tsx`, `frontend/app/portal/analytics/page.tsx`, `docs/operations-monitoring.md`.
- Alternatives rejected:
  - Add a dedicated usage-rollup table now: deferred because the current pilot scale can compute monthly quota snapshots from existing rows and PR-11 may still change entitlement dimensions.
  - Rely only on external provider billing dashboards: rejected because tenant-level budget controls must be enforceable inside the SaaS workflow before customer pilot use.
  - Leave quotas as documentation only: rejected because chat, AI, document, storage, and crawl entrypoints now need graceful limit enforcement.
- Follow-up impact: PR-11 can map plans/entitlements onto the PR-10 quota keys, and PR-12 should decide whether to require persistent rollups or external observability integration before public launch.

## DEC-PR-20260529-020: PR-11 Uses Manual Paid-Beta Entitlements Before Stripe

- Date: 2026-05-29
- Decision: Implement PR-11 with tenant-scoped manual subscription entitlements, a code-defined beta plan catalog, server-side quota enforcement, admin assignment controls, and business-visible billing status. Do not add Stripe, checkout, webhook processing, card storage, or automated payment collection in PR-11.
- Reason: Controlled paid beta needs enforceable plan/status controls now, but payment-provider automation introduces tax, refund, webhook, idempotency, and operational support complexity that should follow owner-approved pricing and commercial terms.
- Affected files/phases: PR-11, `backend/app/models/billing.py`, `backend/app/billing/service.py`, `backend/app/usage/quotas.py`, `backend/app/api/admin.py`, `backend/app/api/business_portal.py`, `frontend/app/admin/billing/page.tsx`, `frontend/app/portal/billing/page.tsx`, `docs/paid-beta-readiness.md`.
- Alternatives rejected:
  - Add Stripe immediately: deferred until pricing, GST/tax, refund policy, customer portal, webhook replay/idempotency, and support operations are approved.
  - Leave billing as documentation only: rejected because paid beta must have server-side entitlement and quota controls before any charged use.
  - Trust frontend plan state: rejected because entitlements must be enforced by backend services and tenant-scoped database state.
- Follow-up impact: PR-12 must re-audit paid-beta gates, confirm owner approval, validate live/staging smoke evidence, and decide whether manual entitlements are sufficient for launch or Stripe should become a required pre-launch phase.

## DEC-PR-20260529-021: PR-12 Is A Launch Gate, Not A Live Deployment

- Date: 2026-05-29
- Decision: Complete PR-12 by creating an evidence-backed final validation package, release checklist, VPS/staging validation runbook, rollback/restore runbook, and final GO/NO-GO statement. Public production launch remains NO-GO until owner-approved live evidence and explicit launch approval are recorded.
- Reason: The production phase protocol forbids live deployment, DNS/TLS changes, production migrations, payment activation, or real customer onboarding without separate explicit permission. Repository-controlled checks can verify code and configuration, but they cannot substitute for target-host TLS, firewall, backup/restore, pgvector, worker, quota, alerting, and customer-workflow smoke evidence.
- Affected files/phases: PR-12, `docs/production-launch/*`, `production-control/*`, production visual status artifacts.
- Alternatives rejected:
  - Mark public production GO after repository tests only: rejected because external operational evidence and owner approval are mandatory release gates.
  - Deploy or run live VPS commands during PR-12 automatically: rejected because the user did not grant explicit deployment permission.
  - Add new product features during PR-12: rejected because PR-12 is the final validation and launch-gate phase.
- Follow-up impact: The next safe command is an owner-approved staging/VPS validation or launch-candidate review, not another automatic production phase.

## DEC-PR-20260529-022: PR-12A Corrects Repository Security Gates Before Staging

- Date: 2026-05-29
- Decision: Add PR-12A as a corrective repository security phase after independent review. Production super-admin login/session validation now requires configured TOTP MFA for every active `super_admin`, and production application rate limiting now requires Redis-backed coordination instead of per-process memory.
- Reason: PR-12 correctly kept public production NO-GO, but its repository launch-gate package still allowed two issues that should be corrected before staging validation: optional production admin MFA and non-durable app-level limits.
- Affected files/phases: PR-12A, `backend/app/admin/auth.py`, `backend/app/core/rate_limit.py`, `backend/app/core/config.py`, `backend/app/api/health.py`, `backend/tests/admin/test_admin_api.py`, `backend/tests/security/test_rate_limit_backend.py`, docs and production-control artifacts.
- Alternatives rejected:
  - Leave MFA optional and rely on policy: rejected because production enforcement must be code-backed.
  - Rely on Nginx-only limits: rejected because endpoint-specific tenant/account/widget scopes need application enforcement too.
  - Continue with in-memory app limits in production: rejected because they reset on restart and do not coordinate across app instances.
- Follow-up impact: Staging/VPS validation must prove Redis rate limiting and production super-admin MFA readiness before any public launch gate can change.

## DEC-PR-20260530-023: PR-13 Reopens Specific Completion Claims Instead Of Marking Launch Ready

- Date: 2026-05-30
- Decision: Treat PR-13 as a post-merge audit phase and record high findings for worker concurrency-safe job claiming, persisted rate-limit abuse analytics, and reproducible browser/e2e evidence. Keep public production NO-GO and recommend PR-13A/PR-13B before external launch validation.
- Reason: The merged repository passes local tests and contains the PR-12A security corrections, but production readiness requires evidence that claims are true in code and tests. A complete audit should reopen overstated phase claims instead of preserving optimistic status.
- Affected files/phases: PR-13, PR-05, PR-09, PR-10, `docs/production-audit/post-pr12a-final-audit/*`, `production-control/*`, `production-control/visual/*`.
- Alternatives rejected:
  - Mark all phases fully complete because tests pass: rejected because PR-13 found untested production-risk paths and documentation overclaims.
  - Proceed directly to staging/VPS validation: rejected because repository findings should be remediated or explicitly scoped first.
  - Implement fixes inside PR-13: rejected because the instruction defined PR-13 as audit-only except for documentation/status corrections.
- Follow-up impact: The next safe command is `Implement remediation phase PR-13A`, followed by PR-13B where customer browser-flow evidence is required, then owner-approved PR-14 external validation.
- PR-13A update: PR-13A closed the repository High findings in one consolidated phase, including the browser/e2e evidence originally proposed as PR-13B. The next safe command is now owner-approved PR-14 external validation.

## DEC-PR-20260530-024: PR-13A Uses Atomic Database Job Claiming

- Date: 2026-05-30
- Decision: Replace background job select-then-update acquisition with an atomic `UPDATE ... RETURNING` claim path. In PostgreSQL, the candidate subquery uses `FOR UPDATE SKIP LOCKED`; SQLite test mode uses the same atomic update shape without pretending to prove PostgreSQL row-lock behavior.
- Reason: PR-13 found that multiple workers could race because the repository had no database-level proof that one job could only be claimed once. Atomic claiming preserves ordering while ensuring only one worker receives a job row.
- Affected files/phases: PR-13A, PR-05, `backend/app/jobs/service.py`, `backend/tests/workers/test_background_jobs.py`.
- Alternatives rejected:
  - Keep single-worker operation as policy: rejected because the production architecture should not silently depend on a human operational limit.
  - Introduce a new queue framework during PR-13A: rejected because the existing durable job ledger can be hardened incrementally without rewriting worker architecture.
- Follow-up impact: PR-14 must still run a production-equivalent PostgreSQL multi-worker smoke test before trusting horizontal worker scaling.

## DEC-PR-20260530-025: PR-13A Persists Privacy-Safe Rate-Limit Exceed Events

- Date: 2026-05-30
- Decision: Persist denied rate-limit events as tenant `UsageLog(rate_limit_exceeded)` when tenant context is safely resolvable, otherwise as `GlobalAuditLog(action=rate_limit_exceeded)`. Persist only safe metadata: scope, route template, method, limit/window/retry-after, actor category, hashed actor/client/limiter fingerprints, identifier count, and safe-shaped request IDs.
- Reason: PR-13 found that rate-limit denials were logged but not durable for abuse investigation, quota analytics, or admin monitoring. The event payload must support operations without storing credentials, tokens, raw IPs, MFA codes, widget secrets, or request bodies.
- Affected files/phases: PR-13A, PR-02, PR-10, `backend/app/core/rate_limit.py`, `backend/app/usage/service.py`, `backend/app/analytics/service.py`, affected API routes and tests.
- Alternatives rejected:
  - Store raw request identifiers for investigation: rejected because it creates unnecessary privacy and secret-exposure risk.
  - Allow abused requests when analytics persistence fails: rejected; the request must remain blocked even if the best-effort analytics write fails.
- Follow-up impact: PR-14 should smoke-test Redis-backed rate-limit denials and abuse metrics in the target environment.

## DEC-PR-20260530-026: PR-13A Adds Mocked Browser E2E As Repository Evidence

- Date: 2026-05-30
- Decision: Add Playwright browser tests that start the real Next.js frontend and intercept the API boundary with deterministic synthetic responses for critical business and admin flows. Wire the mocked browser suite into CI while documenting that it is not live backend/staging proof.
- Reason: PR-13 found that PR-09 browser evidence was overstated. Mocked browser E2E is stable and reproducible in repository CI, covers routing/forms/state/citation/widget UI behavior, and avoids requiring live secrets or real customer data.
- Affected files/phases: PR-13A, PR-09, `.github/workflows/ci.yml`, `frontend/playwright.config.ts`, `frontend/e2e/*`, `frontend/package.json`, `frontend/README.md`.
- Alternatives rejected:
  - Add only more static/unit tests: rejected because the finding specifically required browser-level evidence.
  - Claim mocked E2E proves backend integration: rejected; PR-14 still needs owner-approved target-environment smoke for live backend, Redis, PostgreSQL, worker, widget-origin, and cookie/MFA behavior.
- Follow-up impact: Future frontend changes should keep the mocked browser suite green, and PR-14 should add live/staging smoke evidence without real customer data.
