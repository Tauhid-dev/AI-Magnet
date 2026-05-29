# Rollback And Restore Runbook

Date: 2026-05-29  
Phase: PR-12

This runbook defines the minimum rollback and restore path for an OCI VPS-style deployment. It must be tested in staging before public production launch.

## Decision Rule

Prefer a forward fix when:

- no unsafe database migration has run
- no customer data integrity issue exists
- the issue is application-only and can be patched quickly

Use application rollback when:

- the new release causes auth, ingestion, chat, worker, or frontend breakage
- the database schema remains compatible with the previous release
- customer data integrity is not at risk

Use restore only when:

- data was corrupted or deleted
- a migration must be reversed and forward repair is unsafe
- the owner accepts the restore point objective and data loss window

## Application Rollback

1. Announce maintenance window to affected operators/customers.
2. Record current commit, image tags, migration revision, and incident time.
3. Stop public traffic or enable maintenance routing at Nginx/firewall.
4. Check out the previous known-good commit:

```bash
git checkout <previous-known-good-commit>
docker compose --env-file .env -f docker-compose.prod.yml up --build -d
```

5. Run smoke checks:

```bash
curl -f https://your-domain.example/health
curl -f https://your-domain.example/api/health
curl -f https://your-domain.example/api/ready
```

6. Verify business login, admin login, worker heartbeat, and one safe tenant read path.
7. Restore public traffic only after smoke checks pass.

## Migration Rollback Policy

Do not run database downgrades on live customer data without an explicit restore plan.

Before any downgrade:

- export affected tenant data if possible
- confirm the Alembic downgrade target
- confirm whether the downgrade drops columns/tables/data
- create an encrypted backup
- test the downgrade against staging or a restored copy first

If a migration is unsafe to downgrade, use a forward repair migration instead.

## Database Restore

1. Identify the selected encrypted backup.
2. Stop application and worker writes:

```bash
docker compose --env-file .env -f docker-compose.prod.yml stop backend worker frontend nginx
```

3. Restore to a clean target first using:

```bash
ENV_FILE=.env.restore COMPOSE_FILE=docker-compose.prod.yml scripts/restore_postgres.sh /secure/offsite/ai_magnet_YYYYMMDD_HHMMSS.dump.enc
```

4. Validate:

- tenant count
- business user count
- document/chunk count
- subscription count
- latest migration revision
- pgvector extension exists

5. If owner approves production restore, run the restore against production.
6. Restart services and run `/ready`.
7. Record the restore evidence and affected data window.

## Document Storage Restore

Uploaded files are stored in the private `document_storage` volume. If customer document upload is enabled, the backup strategy must preserve database and document storage consistency.

Minimum evidence before launch:

- database backup timestamp
- document storage backup timestamp
- restore test proves uploaded document metadata and stored bytes still match
- delete/offboarding flows still remove private files

## Incident Record

Every rollback or restore must record:

- incident ID
- start/end time
- affected tenants
- affected data categories
- decision maker
- selected rollback or restore path
- commands run
- validation evidence
- customer communication status
- follow-up risks or fixes

Update:

- `production-control/06_EXECUTION_LOG.md`
- `production-control/07_RISK_REGISTER.md`
- `docs/production-launch/release-evidence-checklist.md`
