# PR-05: Real Async Queue, Worker Reliability and Job Visibility

Status: not_started

## Purpose

Replace placeholder/synchronous long-running workflows with observable reliable jobs.

## Why It Is Needed

The current worker process sleeps and does not process Redis or database jobs. Ingestion and notification work is synchronous or only queue-shaped, which is not reliable enough for private internet demos or real customer pilots.

## Preconditions

- PR-04 is verified.
- Redis production networking/protection decision is available.

## In-Scope Work

- Choose queue approach consistent with FastAPI/Python/Redis stack, such as ARQ, Celery, Dramatiq, or RQ.
- Record queue decision.
- Move ingestion, crawling/indexing, embedding generation, notification sends, and retries into queue where appropriate.
- Add idempotency, retry/backoff, failure/dead-letter or failed job visibility.
- Add job status/progress model/API for later portal/admin UX.
- Add worker health checks, logs, safe shutdown, and tests.

## Out-Of-Scope Work

- Website crawling feature implementation beyond queue primitives.
- Full monitoring stack beyond worker/job visibility.

## Source Areas Likely Affected

- `backend/app/workers/`
- `backend/app/rag/`
- `backend/app/notifications/`
- `backend/app/models/`
- `backend/migrations/`
- `backend/app/api/`
- `docker-compose*.yml`
- `backend/tests/`

## Detailed Tasks

- [ ] Inspect current synchronous ingestion/notification paths.
- [ ] Choose and document queue framework.
- [ ] Add job model/status APIs if needed.
- [ ] Implement enqueue and worker consume behavior.
- [ ] Add retry/backoff/idempotency.
- [ ] Add failed job visibility.
- [ ] Add worker health/shutdown behavior.
- [ ] Add tests for success, retry, failure, and idempotency.
- [ ] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Unit tests for job handlers.
- Integration tests for enqueue/process/failure.
- Worker startup/config validation.
- Compose config validation.

## Security Considerations

Jobs must preserve tenant boundaries and must not leak job data across tenants or logs.

## Migration And Rollback Notes

Schema may be needed for job status. Provide downgrade and job-state compatibility notes.

## Evidence

To be filled during PR-05.

## Blockers

Requires secure production Redis/topology from PR-04.

## Completion Criteria

A real worker consumes queued jobs with reliable failure/retry visibility; placeholder worker is no longer presented as production-ready.
