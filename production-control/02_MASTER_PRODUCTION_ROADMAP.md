# Master Production Roadmap

Last updated: 2026-05-30

The original MVP Phase 0-10 roadmap remains historical/build evidence. This PR-00 through PR-13 roadmap is the production-remediation and audit execution plan and the source of truth for future production phase commands.

## Phase Table

| Phase | Objective | Dependencies | Task checklist summary | Acceptance gate | Status | Branch | Commit | Evidence |
|---|---|---|---|---|---|---|---|---|
| PR-00 | Visible roadmap, persistent memory, verified baseline | None | Inspect repo/audit; create production-control; create visuals/dashboard; add AGENTS protocol | Future run can execute `Implement production phase PR-01` using persisted context | verified | `production/pr-00-roadmap-memory-system` | `59bd9f3` | `production-control/` |
| PR-01 | Production authentication, session security, admin access | PR-00 | Replace email-only auth; admin MFA/protection; secure session strategy; revocation; roles; tests | No email-only production auth path remains | verified | `production/pr-01-auth-session-security` | pending | `phases/PR-01_PRODUCTION_AUTHENTICATION_SESSION_SECURITY_AND_ADMIN_ACCESS.md` |
| PR-02 | Public API abuse protection and widget origin controls | PR-01 | Rate limits; widget origin enforcement; key rotate/revoke/disable; CORS/CSRF/CSP/security headers; abuse logs | Public endpoints have tested abuse controls | verified | `production/pr-02-api-abuse-widget-security` | pending | `phases/PR-02_PUBLIC_API_ABUSE_PROTECTION_WIDGET_ORIGIN_CONTROLS_AND_API_SECURITY.md` |
| PR-03 | Tenant isolation, data lifecycle, privacy, DB integrity | PR-01, PR-02 | DB tenant constraints; privacy lifecycle; export/delete/offboarding; global audit model; tests | Cross-tenant relationships prevented and lifecycle implemented | verified | `production/pr-03-tenant-privacy-db-integrity` | pending | `phases/PR-03_TENANT_ISOLATION_DATA_LIFECYCLE_PRIVACY_AND_DATABASE_INTEGRITY.md` |
| PR-04 | Production infrastructure, TLS, secrets, backups, CI security | PR-01, PR-02, PR-03 | Prod Compose; private DB/Redis; TLS/HSTS; secret validation; backups/restore; CI scans; pgvector validation | Secure production topology is configured and testable without public DB/Redis | verified | `production/pr-04-production-infrastructure-security` | pending | `phases/PR-04_PRODUCTION_INFRASTRUCTURE_TLS_SECRETS_BACKUPS_AND_CI_SECURITY.md` |
| PR-05 | Real async queue, worker reliability, job visibility | PR-04 | Queue choice; Redis integration; retries/backoff; job status; worker health; tests | Worker consumes jobs with observable retry/failure behavior | implemented with PR-13 residual risk | `production/pr-05-real-async-queue-worker` | pending | `phases/PR-05_REAL_ASYNC_QUEUE_WORKER_RELIABILITY_AND_JOB_VISIBILITY.md`, `docs/production-audit/post-pr12a-final-audit/implementation-gap-register.md` |
| PR-06 | Secure website and sitemap ingestion | PR-05 | Website/sitemap APIs/UI; SSRF controls; domain approval; crawl limits; refresh/delete | Tenant can safely index approved website/sitemap content | verified | `production/pr-06-secure-website-sitemap-ingestion` | pending | `phases/PR-06_SECURE_WEBSITE_AND_SITEMAP_INGESTION.md`, `docs/website-ingestion.md` |
| PR-07 | Secure document ingestion, storage, OCR path | PR-05 | Multipart upload; PDF/DOCX; file checks; storage; deletion; gated OCR | Supported documents process safely under tenant boundaries | verified | `production/pr-07-secure-document-ingestion-storage-ocr` | pending | `phases/PR-07_SECURE_DOCUMENT_INGESTION_STORAGE_AND_OCR_PATH.md`, `docs/document-ingestion.md` |
| PR-08 | Scalable RAG retrieval, citations, safety, quality eval | PR-06, PR-07 | SQL pgvector retrieval; thresholds; citations; prompt injection defenses; eval fixtures | RAG is scalable, grounded, cited, and fails safely | verified | `production/pr-08-scalable-rag-citations-safety` | pending | `phases/PR-08_SCALABLE_RAG_RETRIEVAL_CITATIONS_SAFETY_AND_QUALITY_EVALUATION.md`, `docs/rag-quality.md` |
| PR-09 | Customer onboarding, agent testing, widget installation UX | PR-08 | Onboarding; knowledge setup UI; agent sandbox; widget domains/keys/branding; e2e UX | Test tenant can self-serve setup to controlled widget install | implemented with PR-13 evidence gap | `production/pr-09-customer-onboarding-agent-widget-ux` | pending | `phases/PR-09_CUSTOMER_ONBOARDING_AGENT_TESTING_AND_WIDGET_INSTALLATION_EXPERIENCE.md`, `docs/production-audit/post-pr12a-final-audit/implementation-gap-register.md` |
| PR-10 | Monitoring, analytics, metering, quotas, cost protection | PR-09 | Structured logs; metrics; alerts; usage/cost metering; quotas; runbooks | Operator can observe failures and enforce cost/usage limits | implemented with PR-13 residual risk | `production/pr-10-monitoring-metering-quotas-cost-protection` | pending | `phases/PR-10_MONITORING_ANALYTICS_METERING_QUOTAS_AND_COST_PROTECTION.md`, `docs/production-audit/post-pr12a-final-audit/implementation-gap-register.md` |
| PR-11 | Billing, compliance controls, paid-beta readiness | PR-10 | Entitlements/plans; manual paid-beta controls; privacy/support disclosures; paid-beta review | Manual paid beta controls are enforceable and predecessor repo gates pass | verified | `production/pr-11-billing-compliance-paid-beta` | pending | `phases/PR-11_BILLING_COMPLIANCE_CONTROLS_AND_PAID_BETA_READINESS.md`, `docs/paid-beta-readiness.md` |
| PR-12 | Final production validation and launch gate | PR-11 | Independent re-audit; full validation package; staging/VPS runbook; final go/no-go | Production GO only with external evidence and explicit owner approval | verified | `production/pr-12-final-production-validation-launch-gate` | pending | `phases/PR-12_FINAL_PRODUCTION_VALIDATION_AND_LAUNCH_GATE.md`, `docs/production-launch/` |
| PR-12A | Final repository security corrections before staging validation | PR-12 | Mandatory production super-admin MFA; Redis app rate limiting; readiness visibility; corrected launch docs | Independent-review repository blockers are corrected; production still NO-GO pending live evidence | verified | `production/pr-12a-security-corrections-before-staging` | pending | `phases/PR-12A_FINAL_REPOSITORY_SECURITY_CORRECTIONS_BEFORE_STAGING_VALIDATION.md` |
| PR-13 | Full post-merge production readiness audit | PR-12A | Verify merged repository, rerun validation, audit every phase, create evidence pack, update status/dashboard | Repository truth is recorded; remediation phases are recommended before launch work | verified with findings | `production/pr-13-full-post-merge-audit` | pending | `phases/PR-13_FULL_POST_MERGE_PRODUCTION_READINESS_AUDIT.md`, `docs/production-audit/post-pr12a-final-audit/` |

## Launch Gates

- Gate A: Controlled Internal Demo - synthetic/sample data only. Current status: GO WITH CONDITIONS.
- Gate B: Secure Private Internet Demo - requires validated PR-01 through PR-05.
- Gate C: Real Customer Pilot - requires PR-01 through PR-10 plus PR-13A/PR-13B remediation where applicable and external evidence.
- Gate D: Paid Beta - requires PR-01 through PR-11 plus PR-13A/PR-13B remediation where applicable and owner commercial approval.
- Gate E: Public Production Launch - PR-12A security corrections and PR-13 audit are complete, but public launch remains NO-GO until repository findings are remediated where required and owner-approved live evidence plus explicit owner approval are recorded.

## Phase Status Rules

- `not_started`: no meaningful implementation evidence for this production remediation phase.
- `in_progress`: implementation has begun but gate is not met.
- `blocked`: work cannot safely proceed because a prerequisite or unresolved risk blocks completion.
- `complete`: implementation tasks are finished but final required verification is not complete.
- `verified`: implementation and required validation evidence satisfy the phase completion criteria.
