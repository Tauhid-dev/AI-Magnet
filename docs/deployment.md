# Deployment Guide

## Scope

This guide covers the MVP Docker Compose deployment path for an OCI VPS or similar single-host Linux server. It assumes one hosted platform with tenant-isolated data in PostgreSQL and pgvector.

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
6. Copy `.env.example` to `.env` and replace placeholder values before starting services.

## Production Environment Rules

Set these values in `.env` for production:

```bash
APP_ENV=production
APP_DEBUG=false
ENABLE_API_DOCS=false
CORS_ALLOWED_ORIGINS=https://your-domain.example
BUSINESS_PORTAL_SESSION_SECRET=<strong-random-secret>
ADMIN_PORTAL_SESSION_SECRET=<strong-random-secret>
POSTGRES_PASSWORD=<strong-random-password>
DATABASE_URL=postgresql+psycopg://ai_tradie:<strong-random-password>@postgres:5432/ai_tradie
NEXT_PUBLIC_API_BASE_URL=/api
EMAIL_PROVIDER=smtp
SMTP_HOST=<smtp-host>
SMTP_USERNAME=<smtp-username>
SMTP_PASSWORD=<smtp-password>
SMTP_FROM_EMAIL=<verified-sender>
AI_API_KEY=<provider-api-key>
```

Do not use wildcard CORS, placeholder session secrets, or enabled API docs in production. The backend refuses to start in production when these unsafe settings are detected.

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

## Database Migrations

Run migrations after services are built and PostgreSQL is healthy:

```bash
docker compose run --rm backend python -m alembic -c backend/alembic.ini upgrade head
```

For the current backend image, Alembic is available when the repository is mounted or when running from a development checkout. If a future production image removes migration files, run migrations from a release artifact that includes `backend/migrations`.

## Nginx Routing

The bundled `infra/nginx/default.conf` routes:

- `/api/*` to the backend after stripping `/api`.
- `/health` to backend health.
- all other paths to the Next.js frontend.

When using Nginx as the browser entrypoint, set:

```bash
NEXT_PUBLIC_API_BASE_URL=/api
```

Terminate TLS at Nginx or an upstream load balancer before production traffic. Add certificate automation before public launch.

## Backups

Minimum MVP backup process:

1. Schedule daily PostgreSQL dumps.
2. Store dumps outside the VPS.
3. Encrypt backups at rest.
4. Test restore into a clean PostgreSQL instance before launch.

Example dump:

```bash
docker compose exec postgres pg_dump -U ai_tradie ai_tradie > backups/ai_tradie_$(date +%Y%m%d_%H%M%S).sql
```

## Rollback

1. Stop browser traffic at Nginx or maintenance mode.
2. Record the current git commit and database migration revision.
3. Check out the previous release commit.
4. Rebuild services with `docker compose up --build -d`.
5. Run smoke checks against `/health`, business portal login, and admin login.
6. Restore the last known-good database backup only if a migration or data change requires it.

Do not downgrade database migrations casually. Prefer forward fixes unless a restore is explicitly planned and tested.

## Smoke Checks

After deployment:

```bash
docker compose ps
docker compose logs --tail=100 backend
curl -f http://127.0.0.1:8080/health
curl -f http://127.0.0.1:8080/api/health
```

Then verify:

- Business portal login.
- Super admin login.
- Widget initialization with an active widget key.
- A test conversation does not retrieve another tenant's knowledge.
- Email notification provider is configured for the environment.
