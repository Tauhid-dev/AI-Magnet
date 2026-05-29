# PR-10: Monitoring, Analytics, Metering, Quotas and Cost Protection

Status: verified

## Purpose

Operate the AI SaaS safely and prevent uncontrolled spend or usage.

## Why It Is Needed

Current usage analytics are MVP transactional counts. The platform lacks full monitoring, alerts, cost/token metering, quotas, operational runbooks, and incident response evidence.

## Preconditions

- PR-09 is verified.
- Main customer workflows exist.

## In-Scope Work

- Structured logs, request/correlation IDs, error reporting seam, health/readiness endpoints, and operational alerts.
- Metrics for jobs, crawl, ingestion, chat, AI provider, notifications, rate limits, and abuse events.
- Usage metering for chats, tokens/cost, pages crawled, documents/storage, and rate-limit events.
- Tenant quotas/limits and graceful enforcement.
- Budget/cost alert thresholds.
- Analytics rollups, retention, export decisions for beta.
- Incident response and operational runbooks.

## Out-Of-Scope Work

- Paid billing integration, handled in PR-11.
- Multi-region observability.

## Source Areas Likely Affected

- `backend/app/core/logging.py`
- `backend/app/main.py`
- `backend/app/usage/`
- `backend/app/analytics/`
- `backend/app/providers/ai/`
- `frontend/app/admin/`
- `frontend/app/portal/analytics/`
- `docs/`
- `backend/tests/`
- `frontend/tests/`

## Detailed Tasks

- [x] Inspect current logs, health, usage taxonomy, and analytics.
- [x] Confirm existing request/correlation ID middleware and JSON log support.
- [x] Keep logs PII-safe by recording quota/rate/cost metadata without raw messages or documents.
- [x] Add metrics/alerting integration seam through readiness checks, `ERROR_REPORTING_DSN`, and operations runbook.
- [x] Add token/cost usage capture for widget chat and agent sandbox tests.
- [x] Add quotas and graceful limit enforcement for chat, AI responses, documents/storage, and website crawl pages.
- [x] Add admin visibility for ops/cost/rate-limit/quota indicators.
- [x] Add incident and restore runbook validation notes.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Unit/integration tests for quotas and usage metering.
- Log/correlation tests.
- Admin analytics tests.
- Frontend lint/typecheck/test/build.
- Manual runbook validation notes.

## Security Considerations

Logs and metrics must avoid raw customer PII and secrets.

## Migration And Rollback Notes

May require usage/cost/quota tables. Provide migrations and quota default behavior.

## Evidence

- `backend/app/usage/quotas.py` computes tenant quota snapshots from tenant-scoped usage, document, conversation, and crawl data.
- `backend/app/chat/service.py` records estimated AI tokens/cost and blocks exhausted tenant chat/AI quotas gracefully.
- `backend/app/api/business_portal.py` enforces knowledge/document/crawl/agent-test quotas and records `quota_limit_exceeded` events.
- `backend/app/api/health.py` exposes `/ready` for database/configuration readiness checks.
- `backend/app/analytics/service.py`, `backend/app/api/admin.py`, and `backend/app/api/business_portal.py` expose quota/cost/usage metrics to admin and portal clients.
- `frontend/app/admin/usage/page.tsx` shows platform estimated tokens, cost, crawl/storage totals, and tenant quota state.
- `frontend/app/portal/analytics/page.tsx` shows tenant quota gauges and blocked/warning status.
- `docs/operations-monitoring.md` documents metering, quota controls, alerting expectations, and incident response.
- `backend/tests/usage/test_quota_service.py`, `backend/tests/chat/test_chat_api.py`, and `backend/tests/test_health.py` cover quota snapshots, quota blocking, and readiness checks.

Validation:

- `backend/.venv/bin/python -m pytest backend/tests/usage/test_quota_service.py backend/tests/chat/test_chat_api.py backend/tests/test_health.py` - pass, 12 tests.
- `backend/.venv/bin/ruff check backend/app backend/tests` - pass.
- `backend/.venv/bin/python -m pytest backend/tests` - pass, 93 tests.
- `npm run lint` - pass.
- `npm run typecheck` - pass.
- `npm test` - pass.
- `npm run build` - pass.
- `python3 -m json.tool production-control/status/production-status.json` - pass.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('production-control/visual/production-roadmap-status.svg'); print('svg ok')"` - pass.
- `git diff --check` - pass.

## Blockers

No repository-controlled PR-10 blockers remain. Live logging/alert destination setup, VPS `/ready` smoke, quota-limit smoke, and operational incident/restore drills remain release-gate evidence before real customer pilot use.

## Completion Criteria

The operator can observe failures and usage, enforce limits, and identify tenant/provider cost risk before accepting paid usage.
