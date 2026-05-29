# External Launch Evidence Still Required

Date: 2026-05-30

The following items are not repository implementation tasks. They require owner-approved staging/VPS execution, external proof files, or business/legal approval before launch status can change.

## Required External Technical Evidence

| Evidence item | Required before | Current PR-13 status |
|---|---|---|
| Remote CI evidence after PR-13 and any remediation merge | Staging and all later gates | Not verified from this environment; `gh` unavailable. |
| Owner-approved staging/VPS deployment smoke | Secure private demo and later | Not present in repository. |
| Live TLS certificate issuance and renewal proof | Private internet demo and later | Not present in repository. |
| External firewall/private-port proof for PostgreSQL and Redis | Private internet demo and later | Repository production Compose has no data-service published ports, but live firewall proof is absent. |
| Scheduled encrypted backup proof | Real customer pilot and later | Scripts exist; live schedule evidence absent. |
| Restore drill from encrypted backup | Real customer pilot and later | Runbook exists; live drill proof absent. |
| Live PostgreSQL/pgvector migration and RAG retrieval smoke | Real customer pilot and later | Unit/SQLite tests and migrations exist; live pgvector smoke absent. |
| Live Redis-backed application limiter smoke | Private internet demo and later | Repository tests pass; target-host smoke absent. |
| Live worker/Redis queue smoke | Private internet demo and later | Repository tests pass; target-host smoke absent. |
| Controlled website/sitemap ingestion smoke | Real customer pilot if website ingestion used | Repository tests pass; real-site smoke absent. |
| Controlled document upload/extraction smoke | Real customer pilot if documents used | Repository tests pass; target-host smoke absent. |
| `/ready` health/readiness smoke with production-like dependencies | Private internet demo and later | Not present in repository. |
| Log/alert destination verification | Real customer pilot and later | Integration seam/runbook exists; live proof absent. |
| Quota-limit and abuse-control smoke | Real customer pilot and later | Repository tests pass; live smoke absent. |

## Required Business/Owner Evidence

| Evidence item | Required before | Current status |
|---|---|---|
| Owner approval for real customer pilot | Real customer pilot | Not present. |
| Pricing, GST/tax, refund and support approval | Paid beta | Not present. |
| Manual invoicing acceptance or payment-provider launch decision | Paid beta | Manual entitlements exist; owner decision not present. |
| Privacy/legal/customer consent approval | Paid beta and public launch | Repository docs exist; owner/legal approval not present. |
| Explicit public production launch approval | Public production launch | Not present. |

## Public Production Gate

Public production launch remains NO-GO until repository remediation findings are closed where required and the external evidence above is recorded.

