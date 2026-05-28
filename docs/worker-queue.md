# Background Worker Queue

Last updated: 2026-05-28

## Decision

PR-05 uses a durable database-backed job ledger with Redis as a wake signal, instead of adopting Celery/RQ/ARQ immediately.

The database is the source of truth for job state, retry attempts, idempotency keys, failure visibility, tenant ownership, and worker heartbeats. Redis is used to wake worker processes quickly after jobs are enqueued; if Redis notification is temporarily unavailable, queued jobs remain durable and are picked up by polling.

## Job Types

- `rag.document_ingestion`: processes queued tenant text/Markdown documents into chunks and embeddings.
- `notification.send_delivery`: sends one queued lead notification delivery.

Future PR-06 and PR-07 ingestion work should add website, sitemap, file extraction, and OCR jobs through the same job ledger.

## Operational Commands

Run the worker:

```bash
python -m app.workers.runner
```

Run the worker dependency health check:

```bash
python -m app.workers.healthcheck
```

## Visibility

Tenant users can inspect their own jobs through:

- `GET /business-portal/jobs`
- `GET /business-portal/jobs/{job_id}`

Super admins can inspect platform jobs and worker heartbeats through:

- `GET /admin/jobs`
- `GET /admin/worker-heartbeats`
- `GET /admin/health`

Job APIs intentionally do not expose raw payloads. Sensitive document-ingestion payloads are redacted after terminal completion or failure.

## Reliability Notes

- Jobs use idempotency keys to prevent duplicate document-ingestion and notification-send jobs.
- Failed retryable jobs move to `retry_scheduled` with bounded exponential backoff.
- Permanently failed jobs remain visible as `failed`.
- Worker heartbeats record idle/running/stopped state.
- Stale running jobs are returned to retry visibility after the lock timeout.
