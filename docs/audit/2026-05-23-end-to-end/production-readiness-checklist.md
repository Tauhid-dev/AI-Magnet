# Production Readiness Checklist

Repository root: `/Users/thuda/Desktop/Resources/Personal/Projects/AI-Magnet`

## Overall Decision

Production deployment: NO-GO.

The repository is suitable for local development and internal MVP demos. It is not ready for public production traffic or real customer data.

## Checklist

| Area | Status | Evidence | Blocker |
|---|---|---|---|
| Backend test suite | PASS | 42 backend tests passed | No. |
| Backend lint | PASS | Ruff passed | No. |
| Backend compile | PASS | compileall passed | No. |
| Migrations | PASS/PARTIAL | SQLite Alembic upgrade passed | Live PostgreSQL migration not validated. |
| Frontend lint/typecheck/test/build | PASS/PARTIAL | lint, typecheck, static test, build passed | E2E/browser tests missing. |
| Docker Compose config | PASS/PARTIAL | `docker compose config` passed | Runtime startup not validated in this audit. |
| Tenant isolation | PARTIAL | Tenant-scoped models/tests | DB-level tenant consistency constraints missing. |
| Authentication | FAIL | MVP email-only sessions | Production auth missing. |
| Authorization/RBAC | PARTIAL | Business/admin token separation | Fine-grained roles missing. |
| Rate limiting | FAIL | Documented missing | Critical public endpoint blocker. |
| Secret management | PARTIAL | `.env.example`, runtime guardrails | No secret manager; incomplete required secret validation. |
| CORS safety | PARTIAL | Production wildcard CORS rejected | Widget allowed-origins defaults can allow all origins. |
| HTTPS/TLS | FAIL | Nginx HTTP only | No TLS automation or HSTS. |
| Nginx hardening | PARTIAL | Basic security headers | No rate limit, TLS, HSTS, compression/cache policy. |
| Database exposure | FAIL for production | Compose publishes `5432` | Must be private in production. |
| Redis exposure | FAIL for production | Compose publishes `6379` | Must be private/authenticated in production. |
| Backups | FAIL | Manual doc only | No scheduled backup/restore validation. |
| Logging | PARTIAL | Basic logging | No central logs, correlation IDs, PII policy enforcement. |
| Monitoring | FAIL | `/health` only | No metrics, alerting, uptime checks, SLOs. |
| Queue/worker | FAIL | Worker sleeps only | No async job processing. |
| RAG ingestion | PARTIAL | Text/Markdown only | No crawler/OCR/file security/refresh. |
| RAG retrieval | PARTIAL | Tenant-first Python scoring | Not scalable; no citations/thresholds. |
| AI safety | PARTIAL | Prompt says use tenant context | No prompt-injection controls/evals. |
| File upload safety | FAIL | JSON text upload only | No production upload controls. |
| Email delivery | PARTIAL | SMTP provider exists | No async retries/bounces/provider verification in worker. |
| Analytics | PARTIAL | Basic dashboards | No retention/rollups/billing-grade data model. |
| Billing | FAIL for paid launch | Docs only | No plans/entitlements/payment provider. |
| Deployment automation | FAIL | Docs only | No deploy workflow/image publishing. |
| Dependency/security scanning | FAIL | CI lacks audit scans | Add npm/pip/SAST/secret scans. |
| Incident response | PARTIAL | Security docs mention need | Runbooks incomplete. |
| Privacy/compliance | PARTIAL | Security/privacy rules exist | Legal review, retention, DSR/export/delete missing. |

## Minimum Before Real Customer Data

1. Production auth for business/admin users.
2. Rate limiting and abuse controls.
3. HTTPS/TLS with HSTS.
4. Private database/Redis networking.
5. Scheduled encrypted backups and restore test.
6. Real queue worker for retries/background jobs.
7. RAG/document upload safety controls.
8. Monitoring, logs, alerting, incident runbook.
9. Privacy policy, retention policy, export/delete workflow.
10. Live PostgreSQL/pgvector deployment validation.

## Minimum Before Paid Beta

1. All real-customer-data requirements above.
2. Billing entitlements or at least enforced manual plan/quota controls.
3. Token/cost tracking per tenant.
4. Customer onboarding and domain/widget validation workflow.
5. Stronger UX error/loading/empty states.
6. End-to-end tests for onboarding, ingestion, chat, lead notification, and admin support.

