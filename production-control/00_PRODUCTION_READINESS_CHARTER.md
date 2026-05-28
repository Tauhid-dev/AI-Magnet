# Production Readiness Charter

Last updated: 2026-05-28

## Product Direction

AI-Magnet should remain a reusable multi-tenant RAG agent SaaS platform. The AI tradie receptionist is the first-market implementation, not an architectural limit.

The intended production workflow is:

1. Business account is created and authenticated securely.
2. Tenant adds an approved website, sitemap, and/or approved knowledge documents.
3. Tenant-owned knowledge is safely ingested, extracted, indexed, refreshed, and deleted under tenant boundaries.
4. The business tests grounded AI answers with source evidence.
5. The business configures and embeds an approved website chat widget.
6. The platform captures leads/conversations and exposes tenant/admin analytics, usage, and support controls.

## Production-Ready Definition

Production-ready means the platform can safely serve real customers and real customer data on an internet-facing deployment with:

- Verified business and administrator authentication.
- Enforced public endpoint abuse controls.
- Tenant isolation validated in code, database constraints, APIs, and tests.
- Secure ingestion for websites, sitemaps, and approved documents.
- Source-grounded RAG responses with safe fallback behavior.
- Private database/Redis networking, HTTPS/TLS/HSTS, secret validation, backups, restore tests, and operational runbooks.
- Real queue processing, observable jobs, monitoring, logs, alerts, and incident response.
- Cost controls, quotas, and launch gates satisfied with evidence.

## Paid-Beta-Ready Definition

Paid beta is allowed only after PR-01 through PR-11 are verified. Paid beta additionally requires:

- Commercial entitlement or billing controls, even if the initial payment process is manual.
- Per-tenant quotas and usage/cost monitoring.
- Privacy, data retention, export/delete/offboarding, support, and incident response workflows.
- Clear residual risk review and owner approval.

## In Scope For Production Remediation

- Production authentication and session security.
- Rate limiting, abuse controls, widget origin enforcement, CORS/CSRF/security header review.
- Tenant isolation integrity, privacy lifecycle, data export/delete/offboarding, and global audit handling.
- Production infrastructure design for OCI VPS without live deployment unless explicitly instructed.
- Real async queue/worker behavior.
- Secure website/sitemap ingestion.
- Secure document/PDF/DOCX ingestion and gated OCR path.
- Scalable pgvector retrieval, citations, RAG safety, and evaluation.
- Customer onboarding, knowledge setup, agent testing, and widget installation UX.
- Monitoring, analytics, metering, quotas, cost controls, and runbooks.
- Paid-beta readiness and final production validation.

## Deferred Scope

The following remain deferred unless explicitly requested later:

- Voice AI.
- SMS and WhatsApp.
- Marketplace.
- Mobile apps.
- Advanced CRM.
- Enterprise/multi-region infrastructure.
- n8n runtime.
- Local Ollama provider runtime.

The following are conditional, not production-security blockers:

- Browser/Playwright crawling: implement only if ordinary crawler cannot support required customer sites.
- Streaming chat: optional UX enhancement unless chosen for beta.
- Public SEO/marketing pages: growth-track work, not a production-security blocker.

## Non-Negotiable Safety Rules

- Do not use email-only authentication for production users or admins.
- Do not expose PostgreSQL or Redis publicly in production configurations.
- Do not accept unrestricted public widget use in production.
- Do not ingest customer websites or documents without SSRF/file safety controls.
- Do not retrieve, answer, analyze, export, or notify using another tenant's data.
- Do not place secrets in source control.
- Do not mark authentication, tenant isolation, data safety, release gates, or production launch complete without relevant validation evidence.
- Do not deploy, migrate a live production database, change DNS, open firewall ports, or execute VPS destructive actions unless the user explicitly instructs that deployment step.

## Definition Of Done For A Production Phase

A PR phase is done only when:

- Current source code was inspected before changes.
- The selected phase file checklist is complete or the phase is explicitly marked blocked.
- Required implementation, tests, docs, config, and migration notes are present.
- Relevant validation commands have run and results are recorded.
- `status/production-status.json`, `04_CURRENT_STATUS.md`, `06_EXECUTION_LOG.md`, `07_RISK_REGISTER.md`, and `08_VALIDATION_MATRIX.md` are updated.
- Visual roadmap/dashboard artifacts are updated.
- Remaining blockers and launch gate status are stated clearly.
- Changes are committed only after validation is recorded.
