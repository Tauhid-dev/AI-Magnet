# VPS/Staging Validation Runbook

Date: 2026-05-29  
Phase: PR-12

This runbook is for an owner-approved staging or OCI VPS validation pass. Do not run these commands against live production infrastructure unless the owner explicitly authorizes the deployment step, target host, domain, and data policy.

## Preconditions

- A reviewed branch or release commit has been selected.
- `.env` is created from `.env.production.example` with real non-placeholder secrets.
- The host firewall is configured before starting public services.
- The test data set is synthetic or explicitly owner-approved.
- Backup destination and encryption passphrase are prepared.

## Static Checks On The Operator Machine

```bash
git status --short --branch
docker compose --env-file .env.production.example -f docker-compose.prod.yml config
```

Confirm generated production Compose exposes only:

- `80:80`
- `443:443`

PostgreSQL and Redis must not publish host ports.

## Host Firewall And Network Exposure

Expected public exposure:

- SSH from approved operator IPs only
- HTTP 80
- HTTPS 443

From an external machine, record:

```bash
nmap -Pn -p 1-65535 your-domain.example
```

The release record must show that PostgreSQL 5432 and Redis 6379 are not reachable from the public internet.

## First Start

```bash
docker compose --env-file .env -f docker-compose.prod.yml pull
docker compose --env-file .env -f docker-compose.prod.yml up --build -d
docker compose --env-file .env -f docker-compose.prod.yml ps
```

## TLS Certificate Bootstrap

Use the deployment guide certificate flow:

```bash
NGINX_TEMPLATE=bootstrap.conf.template docker compose --env-file .env -f docker-compose.prod.yml up -d nginx
docker compose --env-file .env -f docker-compose.prod.yml run --rm certbot
NGINX_TEMPLATE=prod.conf.template docker compose --env-file .env -f docker-compose.prod.yml up -d nginx
```

Validate:

```bash
curl -I https://your-domain.example/health
curl -I https://your-domain.example/api/health
```

Record the certificate expiry date and renewal command result.

## Database And pgvector Smoke

```bash
scripts/validate_pgvector_migrations.sh
```

Then run a controlled RAG smoke:

1. Create a test tenant.
2. Upload one approved knowledge document or crawl one approved test site.
3. Wait for the worker job to complete.
4. Ask a supported question.
5. Confirm the answer includes only same-tenant citations.
6. Ask an unsupported question.
7. Confirm no-answer fallback is returned.

## Health And Readiness

```bash
curl -f https://your-domain.example/health
curl -f https://your-domain.example/api/health
curl -f https://your-domain.example/api/ready
```

Expected:

- `/health` passes.
- `/ready` passes with database and production config checks healthy.
- Responses include request/correlation identifiers.

## Worker And Redis Smoke

1. Queue a document upload or website crawl.
2. Confirm the job appears in admin job visibility.
3. Confirm a worker heartbeat exists.
4. Confirm the job completes or fails with visible retry/failure state.

Record:

```bash
docker compose --env-file .env -f docker-compose.prod.yml logs --tail=100 worker
```

## Backup And Restore Drill

Create an encrypted backup:

```bash
ENV_FILE=.env COMPOSE_FILE=docker-compose.prod.yml BACKUP_DIR=/var/backups/ai-magnet scripts/backup_postgres.sh
```

Restore into a clean non-production target:

```bash
ENV_FILE=.env.restore COMPOSE_FILE=docker-compose.prod.yml scripts/restore_postgres.sh /secure/offsite/ai_magnet_YYYYMMDD_HHMMSS.dump.enc
```

Record:

- backup filename
- backup checksum if available
- restore target
- restore start/end time
- validation query result
- operator

## Abuse And Quota Smoke

Perform controlled tests only:

- login failures trigger lockout/rate limit without account leakage
- widget origin from an unapproved domain is rejected
- a tenant with a low quota receives a graceful 429 on a billable operation
- a valid tenant remains able to use allowed operations

Do not run uncontrolled load tests against a public environment.

## Log And Alert Smoke

Confirm the logging destination receives:

- normal request logs with request/correlation ID
- failed login/rate-limit event
- failed or retrying worker job
- quota-limit event
- readiness failure simulation if safely possible

## Release Record

Append the results to:

- `docs/production-launch/release-evidence-checklist.md`
- `production-control/06_EXECUTION_LOG.md`
- `production-control/08_VALIDATION_MATRIX.md`
- `production-control/07_RISK_REGISTER.md`

Only after this evidence exists can Gate B, C, D, or E move beyond repository-ready-with-conditions.
