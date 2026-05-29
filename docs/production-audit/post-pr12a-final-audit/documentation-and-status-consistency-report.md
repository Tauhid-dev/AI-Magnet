# Documentation And Status Consistency Report

Date: 2026-05-30

## Consistent Claims

- `docs/production-launch/final-go-no-go-statement.md` keeps public production launch as NO-GO.
- `docs/security.md` reflects password authentication, HttpOnly/SameSite cookies, CSRF confirmation, and mandatory production super-admin MFA.
- `frontend/README.md` no longer describes authentication as MVP-only email login.
- `docker-compose.prod.yml` and `docs/deployment.md` consistently describe private PostgreSQL/Redis production networking.
- `docs/document-ingestion.md`, `production-control/04_CURRENT_STATUS.md`, and `backend/app/rag/extraction.py` consistently treat scanned-document OCR as gated/not implemented.
- `docs/future-modules/*` and production-control deferred scope correctly keep voice, SMS/WhatsApp, marketplace, mobile, advanced CRM, multi-region, n8n runtime and local Ollama out of current production scope.

## Stale Or Overstated Claims Corrected In PR-13

| Area | Previous representation | Evidence | PR-13 correction |
|---|---|---|---|
| Production roadmap scope | `production-control/02_MASTER_PRODUCTION_ROADMAP.md` said PR-00 through PR-12 even after PR-12A | Phase file and status JSON include PR-12A | Updated roadmap/status to include PR-13 audit and PR-12A history. |
| Dashboard progress | `production-status-dashboard.html` showed `14 / 14 phases` and PR-12A final state | PR-13 audit branch adds a new audit phase and findings | Updated dashboard/diagram/status to show PR-13 and follow-up remediation. |
| PR-09 browser/e2e tests | PR-09 phase checklist marked browser/e2e tests complete | `frontend/package.json` runs only `node --test tests/static-check.mjs`; previous browser smoke was manual | Recorded as `AUD-HIGH-003` and reopened PR-09 as implemented with residual evidence risk. |
| PR-10 rate-limit analytics | PR-02/PR-10 docs claim abuse/rate-limit usage events | `backend/app/core/rate_limit.py` logs rate-limit exceed but does not persist `UsageEventType.RATE_LIMIT_EXCEEDED` | Recorded as `AUD-HIGH-002`; recommend PR-13A. |
| PR-05 production worker reliability | PR-05 status claimed verified worker reliability | `backend/app/jobs/service.py` lacks atomic/locked claim semantics and concurrent worker tests | Recorded as `AUD-HIGH-001`; recommend PR-13A. |

## Historical Audit Files

The old files under `docs/audit/2026-05-23-end-to-end/` intentionally preserve the historical audit baseline. They still mention email-only auth and missing ingestion features from the original baseline. PR-13 does not treat those as stale, because `production-control/01_AUDIT_BASELINE_2026-05-23.md` maps the historical findings to later remediation phases.

## Production-Control Consistency

Before PR-13 edits:

- `production-control/status/production-status.json` was valid JSON.
- Phase files and status JSON matched for PR-00 through PR-12A.
- The SVG parsed as XML.
- Public production status was NO-GO.

After PR-13 edits:

- PR-13 is added as an audit phase.
- PR-05, PR-09 and PR-10 are explicitly represented as implemented with residual/reopened findings.
- Public production remains NO-GO.
- Recommended next action is remediation phase PR-13A, not external launch.

