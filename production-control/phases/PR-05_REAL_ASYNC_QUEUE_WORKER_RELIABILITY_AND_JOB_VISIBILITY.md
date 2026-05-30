# PR-05: Real Async Queue, Worker Reliability and Job Visibility

Status: verified

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

- [x] Inspect current synchronous ingestion/notification paths.
- [x] Choose and document queue framework.
- [x] Add job model/status APIs if needed.
- [x] Implement enqueue and worker consume behavior.
- [x] Add retry/backoff/idempotency.
- [x] Add failed job visibility.
- [x] Add worker health/shutdown behavior.
- [x] Add tests for success, retry, failure, and idempotency.
- [x] Update status/risk/validation/visual artifacts.

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

- Queue decision: durable `background_jobs` database ledger with Redis wake signals, documented in `docs/worker-queue.md` and `production-control/05_DECISIONS_LOG.md`.
- Models and migration: `backend/app/models/job.py`, `backend/migrations/versions/20260528_0008_pr05_background_jobs.py`.
- Queue services and worker: `backend/app/jobs/*`, `backend/app/workers/runner.py`, `backend/app/workers/healthcheck.py`.
- Async integrations: business document upload queues `rag.document_ingestion`; chat lead notifications queue `notification.send_delivery`.
- Visibility APIs: `GET /business-portal/jobs`, `GET /business-portal/jobs/{job_id}`, `GET /admin/jobs`, `GET /admin/worker-heartbeats`, and queue counts in `GET /admin/health`.
- Tests: `backend/tests/workers/test_background_jobs.py`, updated business/admin API tests.
- PR-13A concurrency remediation: `backend/app/jobs/service.py` now claims jobs through an atomic `UPDATE ... RETURNING` path with PostgreSQL `FOR UPDATE SKIP LOCKED` candidate selection, preserving queue/status/schedule guards while setting `locked_by`, `locked_at`, `started_at`, `attempts`, and `running` in one database operation.
- Validation: full backend tests passed with 116 tests; focused worker tests passed with 11 tests; migration upgrade/downgrade/upgrade smoke passed on SQLite.

## Blockers

PR-13 reopened one repository-controlled risk: job acquisition was not proven atomic/concurrency-safe for multiple worker processes. PR-13A closed the repository risk with atomic claim implementation and concurrent worker tests. Live PostgreSQL multi-worker smoke on the target VPS remains PR-14B external release-gate evidence before horizontal worker scaling is trusted.

## Completion Criteria

A real worker consumes queued jobs with reliable failure/retry visibility; placeholder worker is no longer presented as production-ready. PR-13A closes the repository-level atomic claim/concurrency evidence gap. Production scaling still needs PR-14 owner-approved PostgreSQL/Redis worker smoke evidence.
