# Master Production Roadmap

Last updated: 2026-05-29

The original MVP Phase 0-10 roadmap remains historical/build evidence. This PR-00 through PR-12 roadmap is the production-remediation execution plan and the source of truth for future production phase commands.

## Phase Table

| Phase | Objective | Dependencies | Task checklist summary | Acceptance gate | Status | Branch | Commit | Evidence |
|---|---|---|---|---|---|---|---|---|
| PR-00 | Visible roadmap, persistent memory, verified baseline | None | Inspect repo/audit; create production-control; create visuals/dashboard; add AGENTS protocol | Future run can execute `Implement production phase PR-01` using persisted context | verified | `production/pr-00-roadmap-memory-system` | `59bd9f3` | `production-control/` |
| PR-01 | Production authentication, session security, admin access | PR-00 | Replace email-only auth; admin MFA/protection; secure session strategy; revocation; roles; tests | No email-only production auth path remains | verified | `production/pr-01-auth-session-security` | pending | `phases/PR-01_PRODUCTION_AUTHENTICATION_SESSION_SECURITY_AND_ADMIN_ACCESS.md` |
| PR-02 | Public API abuse protection and widget origin controls | PR-01 | Rate limits; widget origin enforcement; key rotate/revoke/disable; CORS/CSRF/CSP/security headers; abuse logs | Public endpoints have tested abuse controls | verified | `production/pr-02-api-abuse-widget-security` | pending | `phases/PR-02_PUBLIC_API_ABUSE_PROTECTION_WIDGET_ORIGIN_CONTROLS_AND_API_SECURITY.md` |
| PR-03 | Tenant isolation, data lifecycle, privacy, DB integrity | PR-01, PR-02 | DB tenant constraints; privacy lifecycle; export/delete/offboarding; global audit model; tests | Cross-tenant relationships prevented and lifecycle implemented | verified | `production/pr-03-tenant-privacy-db-integrity` | pending | `phases/PR-03_TENANT_ISOLATION_DATA_LIFECYCLE_PRIVACY_AND_DATABASE_INTEGRITY.md` |
| PR-04 | Production infrastructure, TLS, secrets, backups, CI security | PR-01, PR-02, PR-03 | Prod Compose; private DB/Redis; TLS/HSTS; secret validation; backups/restore; CI scans; pgvector validation | Secure production topology is configured and testable without public DB/Redis | verified | `production/pr-04-production-infrastructure-security` | pending | `phases/PR-04_PRODUCTION_INFRASTRUCTURE_TLS_SECRETS_BACKUPS_AND_CI_SECURITY.md` |
| PR-05 | Real async queue, worker reliability, job visibility | PR-04 | Queue choice; Redis integration; retries/backoff; job status; worker health; tests | Worker consumes jobs with observable retry/failure behavior | verified | `production/pr-05-real-async-queue-worker` | pending | `phases/PR-05_REAL_ASYNC_QUEUE_WORKER_RELIABILITY_AND_JOB_VISIBILITY.md` |
| PR-06 | Secure website and sitemap ingestion | PR-05 | Website/sitemap APIs/UI; SSRF controls; domain approval; crawl limits; refresh/delete | Tenant can safely index approved website/sitemap content | verified | `production/pr-06-secure-website-sitemap-ingestion` | pending | `phases/PR-06_SECURE_WEBSITE_AND_SITEMAP_INGESTION.md`, `docs/website-ingestion.md` |
| PR-07 | Secure document ingestion, storage, OCR path | PR-05 | Multipart upload; PDF/DOCX; file checks; storage; deletion; gated OCR | Supported documents process safely under tenant boundaries | verified | `production/pr-07-secure-document-ingestion-storage-ocr` | pending | `phases/PR-07_SECURE_DOCUMENT_INGESTION_STORAGE_AND_OCR_PATH.md`, `docs/document-ingestion.md` |
| PR-08 | Scalable RAG retrieval, citations, safety, quality eval | PR-06, PR-07 | SQL pgvector retrieval; thresholds; citations; prompt injection defenses; eval fixtures | RAG is scalable, grounded, cited, and fails safely | verified | `production/pr-08-scalable-rag-citations-safety` | pending | `phases/PR-08_SCALABLE_RAG_RETRIEVAL_CITATIONS_SAFETY_AND_QUALITY_EVALUATION.md`, `docs/rag-quality.md` |
| PR-09 | Customer onboarding, agent testing, widget installation UX | PR-08 | Onboarding; knowledge setup UI; agent sandbox; widget domains/keys/branding; e2e UX | Test tenant can self-serve setup to controlled widget install | verified | `production/pr-09-customer-onboarding-agent-widget-ux` | pending | `phases/PR-09_CUSTOMER_ONBOARDING_AGENT_TESTING_AND_WIDGET_INSTALLATION_EXPERIENCE.md` |
| PR-10 | Monitoring, analytics, metering, quotas, cost protection | PR-09 | Structured logs; metrics; alerts; usage/cost metering; quotas; runbooks | Operator can observe failures and enforce cost/usage limits | verified | `production/pr-10-monitoring-metering-quotas-cost-protection` | pending | `phases/PR-10_MONITORING_ANALYTICS_METERING_QUOTAS_AND_COST_PROTECTION.md` |
| PR-11 | Billing, compliance controls, paid-beta readiness | PR-10 | Entitlements/plans; manual paid-beta controls; privacy/support disclosures; paid-beta review | Manual paid beta controls are enforceable and predecessor repo gates pass | verified | `production/pr-11-billing-compliance-paid-beta` | pending | `phases/PR-11_BILLING_COMPLIANCE_CONTROLS_AND_PAID_BETA_READINESS.md`, `docs/paid-beta-readiness.md` |
| PR-12 | Final production validation and launch gate | PR-11 | Independent re-audit; full validation; staging/VPS runbook; final go/no-go | Production GO only with evidence and explicit owner approval | not_started | TBD | TBD | `phases/PR-12_FINAL_PRODUCTION_VALIDATION_AND_LAUNCH_GATE.md` |

## Launch Gates

- Gate A: Controlled Internal Demo - synthetic/sample data only. Current status: GO WITH CONDITIONS.
- Gate B: Secure Private Internet Demo - requires validated PR-01 through PR-05.
- Gate C: Real Customer Pilot - requires validated PR-01 through PR-10.
- Gate D: Paid Beta - requires validated PR-01 through PR-11.
- Gate E: Public Production Launch - requires successful PR-12 final audit and explicit owner approval.

## Phase Status Rules

- `not_started`: no meaningful implementation evidence for this production remediation phase.
- `in_progress`: implementation has begun but gate is not met.
- `blocked`: work cannot safely proceed because a prerequisite or unresolved risk blocks completion.
- `complete`: implementation tasks are finished but final required verification is not complete.
- `verified`: implementation and required validation evidence satisfy the phase completion criteria.
