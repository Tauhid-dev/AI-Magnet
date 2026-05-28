# Deployment Guide

## Scope

This guide covers the Docker Compose deployment path for an OCI VPS or similar single-host Linux server. It assumes one hosted platform with tenant-isolated data in PostgreSQL and pgvector.

PR-04 adds a separate production topology in `docker-compose.prod.yml`. The original `docker-compose.yml` remains a local development topology and still publishes development ports.

## Services

- `backend`: FastAPI API service.
- `worker`: long-lived Python worker process reserved for retryable background jobs.
- `frontend`: Next.js business and admin portal.
- `postgres`: PostgreSQL with pgvector.
- `redis`: cache/queue dependency.
- `nginx`: reverse proxy for browser traffic.

## Required Host Setup

1. Provision an Ubuntu LTS VPS.
2. Install Docker Engine and Docker Compose plugin.
3. Configure firewall rules for SSH, HTTP, and HTTPS.
4. Create an unprivileged deployment user.
5. Clone the repository into the deployment user's home directory.
6. Copy `.env.production.example` to `.env` and replace every placeholder before starting services.
7. Confirm the VPS firewall exposes only SSH, HTTP, and HTTPS to the internet. PostgreSQL and Redis must not be reachable from the public internet.

## Production Environment Rules

Set these values in `.env` for production:

```bash
APP_ENV=production
APP_DEBUG=false
APP_LOG_FORMAT=json
ENABLE_API_DOCS=false
CORS_ALLOWED_ORIGINS=https://your-domain.example
PUBLIC_HOSTNAME=your-domain.example
PUBLIC_BASE_URL=https://your-domain.example
NEXT_PUBLIC_API_BASE_URL=/api
BUSINESS_PORTAL_SESSION_SECRET=<strong-random-secret>
ADMIN_PORTAL_SESSION_SECRET=<strong-random-secret>
AUTH_COOKIE_SECURE=true
WIDGET_REQUIRE_ALLOWED_ORIGINS=true
POSTGRES_PASSWORD=<strong-random-password>
DATABASE_URL=postgresql+psycopg://ai_magnet:<strong-random-password>@postgres:5432/ai_magnet
REDIS_URL=redis://redis:6379/0
WORKER_QUEUE_NAME=default
WORKER_REDIS_QUEUE_KEY=ai-magnet:jobs:default
WORKER_DEFAULT_MAX_ATTEMPTS=3
DOCUMENT_STORAGE_ROOT=/app/storage/documents
DOCUMENT_UPLOAD_MAX_BYTES=10485760
DOCUMENT_UPLOAD_MAX_PAGES=50
DOCUMENT_OCR_ENABLED=false
DOCUMENT_MALWARE_SCAN_MODE=basic
EMAIL_PROVIDER=smtp
SMTP_HOST=<smtp-host>
SMTP_USERNAME=<smtp-username>
SMTP_PASSWORD=<smtp-password>
SMTP_FROM_EMAIL=<verified-sender>
AI_API_KEY=<provider-api-key>
BACKUP_ENCRYPTION_PASSPHRASE=<strong-random-backup-passphrase>
```

Do not use wildcard CORS, placeholder session secrets, insecure cookie settings, local Redis URLs, console email delivery, missing AI provider keys, missing SMTP values, missing backup encryption passphrases, disabled document malware scanning, or enabled API docs in production. The backend refuses to start in production when these unsafe settings are detected.

## Local/Dev Start

From the repository root:

```bash
docker compose up --build
```

Useful local URLs:

- Frontend direct: `http://127.0.0.1:3000`
- Backend direct: `http://127.0.0.1:8000/health`
- Nginx reverse proxy: `http://127.0.0.1:8080`
- Nginx API proxy: `http://127.0.0.1:8080/api/health`

## Production Compose Validation

Before touching a VPS, validate the production configuration locally or in CI:

```bash
docker compose --env-file .env.production.example -f docker-compose.prod.yml config
```

The production compose file intentionally exposes only:

- `80:80` for HTTP/ACME redirect.
- `443:443` for HTTPS traffic.

The production `postgres` and `redis` services do not publish host ports and are attached to an internal Docker network only.

## Background Worker

PR-05 replaces the placeholder worker with a durable database-backed job queue and Redis wake signal. The `worker` service runs:

```bash
python -m app.workers.runner
```

The worker health check validates database and Redis reachability:

```bash
python -m app.workers.healthcheck
```

Operational status is available through `GET /admin/health`, `GET /admin/jobs`, and `GET /admin/worker-heartbeats`. See `docs/worker-queue.md` for job types, retry behavior, and visibility rules.

## Document Storage

PR-07 stores uploaded customer documents in the private `document_storage` Docker volume mounted at `/app/storage/documents` for both backend and worker containers. This path must not be exposed through Nginx, the frontend, or static file serving. Back up the database and document storage lifecycle together when customer document uploads are enabled.

## Production Start

After replacing all `.env` placeholders on the VPS:

```bash
docker compose --env-file .env -f docker-compose.prod.yml up --build -d
```

Run migrations and the pgvector smoke check:

```bash
scripts/validate_pgvector_migrations.sh
```

## Database Migrations

Run migrations after services are built and PostgreSQL is healthy:

```bash
docker compose run --rm backend python -m alembic -c backend/alembic.ini upgrade head
```

For the current backend image, Alembic is available when the repository is mounted or when running from a development checkout. If a future production image removes migration files, run migrations from a release artifact that includes `backend/migrations`.

For production, prefer:

```bash
docker compose --env-file .env -f docker-compose.prod.yml run --rm backend \
  python -m alembic -c backend/alembic.ini upgrade head
```

Then confirm the pgvector extension:

```bash
docker compose --env-file .env -f docker-compose.prod.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "CREATE EXTENSION IF NOT EXISTS vector;" \
  -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

## Nginx Routing And TLS

The bundled `infra/nginx/default.conf` routes:

- `/api/*` to the backend after stripping `/api`.
- `/health` to backend health.
- all other paths to the Next.js frontend.

When using Nginx as the browser entrypoint, set:

```bash
NEXT_PUBLIC_API_BASE_URL=/api
```

Production uses `infra/nginx/templates/prod.conf.template`, which:

- redirects HTTP to HTTPS except ACME challenges;
- serves HTTPS with Let's Encrypt certificate paths;
- sets HSTS and core browser security headers;
- forwards `X-Request-ID` to the backend;
- applies coarse Nginx rate limits to login, widget/chat, and general API surfaces.

Initial certificate request:

```bash
NGINX_TEMPLATE=bootstrap.conf.template docker compose --env-file .env -f docker-compose.prod.yml up -d nginx
docker compose --env-file .env -f docker-compose.prod.yml run --rm certbot
NGINX_TEMPLATE=prod.conf.template docker compose --env-file .env -f docker-compose.prod.yml up -d nginx
```

Renewal should be scheduled with host cron or a systemd timer:

```cron
17 3 * * * cd /home/deploy/AI-Magnet && docker compose --env-file .env -f docker-compose.prod.yml run --rm certbot renew --webroot --webroot-path=/var/www/certbot && docker compose --env-file .env -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Backups

Minimum production backup process:

1. Schedule encrypted PostgreSQL dumps using `scripts/backup_postgres.sh`.
2. Store encrypted dumps outside the VPS.
3. Protect `BACKUP_ENCRYPTION_PASSPHRASE` in a password manager or secret store.
4. Test restore into a clean PostgreSQL instance before launch using `scripts/restore_postgres.sh`.

Example encrypted backup:

```bash
ENV_FILE=.env COMPOSE_FILE=docker-compose.prod.yml BACKUP_DIR=/var/backups/ai-magnet \
  scripts/backup_postgres.sh
```

Example cron entry:

```cron
42 2 * * * cd /home/deploy/AI-Magnet && ENV_FILE=.env COMPOSE_FILE=docker-compose.prod.yml BACKUP_DIR=/var/backups/ai-magnet scripts/backup_postgres.sh >> /var/log/ai-magnet-backup.log 2>&1
```

Example restore drill into a clean environment:

```bash
ENV_FILE=.env.restore COMPOSE_FILE=docker-compose.prod.yml scripts/restore_postgres.sh /secure/offsite/ai_magnet_YYYYMMDD_HHMMSS.dump.enc
```

Record the restore date, backup filename, target environment, and result in the release checklist before launch.

## Rollback

1. Stop browser traffic at Nginx or maintenance mode.
2. Record the current git commit and database migration revision.
3. Check out the previous release commit.
4. Rebuild services with `docker compose --env-file .env -f docker-compose.prod.yml up --build -d`.
5. Run smoke checks against `/health`, business portal login, and admin login.
6. Restore the last known-good database backup only if a migration or data change requires it.

Do not downgrade database migrations casually. Prefer forward fixes unless a restore is explicitly planned and tested.

## Incident Response Baseline

For a production incident before PR-10 monitoring is complete:

1. Preserve evidence: record current git commit, compose service versions, recent `backend`, `worker`, and `nginx` logs, and affected tenant IDs.
2. Contain: disable public traffic at Nginx or firewall if customer data, auth, or provider spend is at risk.
3. Triage: check `/health`, container restarts, database health, Redis health, disk usage, failed jobs, and recent admin audit events.
4. Recover: apply a forward fix, roll back the application image, or restore from encrypted backup only after deciding the data impact.
5. Notify: document affected tenants, timeframe, data categories involved, and remediation notes.
6. Review: update `production-control/07_RISK_REGISTER.md` and `production-control/06_EXECUTION_LOG.md` with the incident outcome.

PR-10 should replace this baseline with metrics, alerts, and a fuller operational response process.

## Smoke Checks

After deployment:

```bash
docker compose ps
docker compose logs --tail=100 backend
curl -f https://your-domain.example/health
curl -f https://your-domain.example/api/health
```

Then verify:

- Business portal login.
- Super admin login.
- Widget initialization with an active widget key.
- A test conversation does not retrieve another tenant's knowledge.
- Email notification provider is configured for the environment.
