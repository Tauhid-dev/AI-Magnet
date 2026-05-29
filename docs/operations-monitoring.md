# Operations, Metering, Quotas, and Cost Protection

PR-10 adds the repository-controlled operating layer required before a real customer pilot.

## Runtime Signals

- Every HTTP response includes `X-Request-ID` and `X-Correlation-ID`.
- `APP_LOG_FORMAT=json` is required in production for container log aggregation.
- `/health` returns liveness context.
- `/ready` validates database connectivity and production configuration state.
- `ERROR_REPORTING_DSN` is an optional integration seam for a future error-reporting provider. Do not commit provider secrets.

## Metering Model

Usage is derived from tenant-scoped `usage_logs` plus current tenant-owned operational rows.

Tracked beta metrics:

- chat conversations per month
- AI responses per month, including sandbox tests
- estimated prompt/completion/total tokens
- estimated AI provider cost in cents
- knowledge document count
- uploaded document storage in MB
- website pages crawled per month
- rate-limit and quota-limit events

Provider cost is estimated from:

```text
AI_PROMPT_COST_CENTS_PER_1K_TOKENS
AI_COMPLETION_COST_CENTS_PER_1K_TOKENS
```

The default pricing values are intentionally configurable estimates. Update them before paid usage if the selected AI provider/model changes.

## Tenant Quotas

Configured limits:

```text
TENANT_QUOTA_CHAT_CONVERSATIONS_PER_MONTH
TENANT_QUOTA_AI_RESPONSES_PER_MONTH
TENANT_QUOTA_TOKENS_PER_MONTH
TENANT_BUDGET_MONTHLY_CENTS
TENANT_QUOTA_DOCUMENTS_TOTAL
TENANT_QUOTA_STORAGE_MB
TENANT_QUOTA_PAGES_CRAWLED_PER_MONTH
QUOTA_WARNING_THRESHOLD_PERCENT
```

Quota checks fail closed for:

- starting a new widget conversation when the monthly conversation quota is exhausted
- generating a widget or sandbox AI response when AI response, token, or budget limits are exhausted
- accepting new knowledge files when document/storage limits are exhausted
- queueing website crawls when the monthly crawled-page limit is exhausted

When a quota blocks an operation, the API returns HTTP 429 and records a tenant-scoped `quota_limit_exceeded` event without raw customer content.

## Operator Views

- Business portal analytics shows per-tenant quota gauges and cost/usage status.
- Super admin usage shows platform estimated tokens, cost, crawl/storage totals, and tenant quota alert states.
- Admin health shows database/job/worker state from earlier PR-05 job visibility.

## Alerting Expectations

Repository PR-10 does not connect a hosted alerting provider. For Gate C pilot readiness, configure log collection and alert rules for:

- repeated `status_code=500`
- `quota_limit_exceeded`
- `rate_limit_exceeded`
- failed or retrying background jobs
- degraded `/ready`
- AI provider failures or cost spikes
- backup failures and missed backup windows

## Incident Response Checklist

1. Identify the tenant, request ID, and time window.
2. Check `/admin/health`, recent jobs, worker heartbeats, and admin usage.
3. Search JSON logs by `request_id`/`X-Correlation-ID`.
4. If abuse or spend is suspected, lower tenant quota env values or suspend the tenant in the admin portal.
5. For ingestion incidents, pause workers, inspect failed jobs, and avoid deleting tenant data until export/retention requirements are understood.
6. For database incidents, follow `docs/deployment.md` backup and restore steps and record the restore evidence.
7. Update `production-control/07_RISK_REGISTER.md` and `production-control/06_EXECUTION_LOG.md` with the incident outcome.

## Release-Gate Evidence Still Required

Before Gate C real customer pilot:

- run `/ready` against the VPS/staging deployment
- verify JSON logs reach the chosen logging destination
- perform a controlled quota-limit smoke test
- confirm backup/restore evidence from PR-04
- confirm PostgreSQL/pgvector smoke from PR-08
- confirm worker/Redis smoke from PR-05
