# GitHub Staging Environment Secrets

This document explains how the repository owner should configure the GitHub `staging` Environment before running the PR-14A staging deployment workflow.

The workflow is intentionally manual-first. It does not deploy on push, does not contain VPS details, and does not expose secrets to pull requests from forks.

## Environment

Create a GitHub Environment named:

```text
staging
```

Recommended protection rules:

- Require reviewer approval before deployments.
- Restrict deployment branches to `master`, release branches, or another owner-approved branch.
- Do not expose staging secrets to pull requests from forks.
- Keep `staging` separate from any future `production` environment.

## Required Environment Variables

Configure these as GitHub Environment variables because they are non-secret operational values:

| Variable | Purpose |
| --- | --- |
| `STAGING_HOST` | VPS SSH host name or IP address. |
| `STAGING_SSH_USER` | Dedicated staging deploy user. |
| `STAGING_DOMAIN` | Staging domain used for HTTPS and public smoke checks. |
| `STAGING_APP_DIR` | Absolute directory for the app checkout on the VPS, for example `/opt/ai-magnet-staging`. |
| `STAGING_COMPOSE_FILE` | Compose file to run, normally `docker-compose.prod.yml` until a dedicated staging compose file is introduced. |
| `STAGING_BRANCH` | Branch to deploy, normally `master` after the PR-14A branch is merged. |

## Required Environment Secrets

Configure these as GitHub Environment secrets:

| Secret | Purpose |
| --- | --- |
| `STAGING_SSH_PRIVATE_KEY` | Private key for the dedicated staging deploy user. |
| `STAGING_SSH_KNOWN_HOSTS` | Host key entry generated with `ssh-keyscan`; used for strict host identity checking. |
| `STAGING_ENV_FILE` | Full `.env.staging` content for the VPS. This is written securely during the approved workflow run. |

Do not store these values in repository files.

## Required Values Inside `STAGING_ENV_FILE`

The current production compose and backend settings require the staging environment file to contain the same production-safe configuration shape as `.env.production.example`.

At minimum include:

- `APP_ENV=production`
- `APP_DEBUG=false`
- `APP_LOG_FORMAT=json`
- `ENABLE_API_DOCS=false`
- `CORS_ALLOWED_ORIGINS=https://<staging-domain>`
- `PUBLIC_HOSTNAME=<staging-domain>`
- `PUBLIC_BASE_URL=https://<staging-domain>`
- `NEXT_PUBLIC_API_BASE_URL=/api`
- `BUSINESS_PORTAL_SESSION_SECRET=<strong random value>`
- `ADMIN_PORTAL_SESSION_SECRET=<strong random value>`
- `AUTH_COOKIE_SECURE=true`
- `WIDGET_REQUIRE_ALLOWED_ORIGINS=true`
- `RATE_LIMIT_ENABLED=true`
- `RATE_LIMIT_BACKEND=redis`
- `POSTGRES_DB=<staging db name>`
- `POSTGRES_USER=<staging db user>`
- `POSTGRES_PASSWORD=<strong random value>`
- `DATABASE_URL=postgresql+psycopg://<user>:<password>@postgres:5432/<db>`
- `REDIS_URL=redis://redis:6379/0`
- `AI_PROVIDER=openai-compatible`
- `AI_API_BASE_URL=<provider base URL>`
- `AI_API_KEY=<staging provider key>`
- `SMTP_HOST=<provider host>`
- `SMTP_USERNAME=<provider username>`
- `SMTP_PASSWORD=<provider password>`
- `SMTP_FROM_EMAIL=<staging sender>`
- `SMTP_STARTTLS=true`
- `BACKUP_ENCRYPTION_PASSPHRASE=<strong random value>`

The generic checklist item `STAGING_SECRET_KEY` maps to the repository's two explicit session secrets: `BUSINESS_PORTAL_SESSION_SECRET` and `ADMIN_PORTAL_SESSION_SECRET`.

`STAGING_REDIS_PASSWORD` is not required by the current compose file because Redis is private to the Docker `data` network and Redis AUTH is not configured. Add Redis AUTH support before introducing that secret.

Owner-managed smoke-test secrets such as `STAGING_ADMIN_BOOTSTRAP_PASSWORD`, `STAGING_ADMIN_MFA_SECRET`, `STAGING_AI_PROVIDER_API_KEY`, and `STAGING_EMAIL_PROVIDER_API_KEY` should be represented in `STAGING_ENV_FILE` or added as dedicated workflow secrets only when the corresponding PR-14B smoke step consumes them. Do not commit those values.

## SSH Key Setup

Generate a dedicated deploy key on a trusted machine:

```bash
ssh-keygen -t ed25519 -C "ai-magnet-staging-deploy" -f ai-magnet-staging-deploy
```

Add the public key to the VPS deploy user's `~/.ssh/authorized_keys`.

Store the private key content as `STAGING_SSH_PRIVATE_KEY`.

## Known Hosts Setup

Generate the known-hosts value from a trusted network:

```bash
ssh-keyscan -t ed25519,rsa <staging-host>
```

Verify the fingerprint through the VPS provider console or another trusted channel before storing it as `STAGING_SSH_KNOWN_HOSTS`.

Do not disable host key checking. The workflow uses `StrictHostKeyChecking=yes` to prevent accidental or malicious host substitution.

## Triggering the Workflow

After the `staging` Environment variables and secrets are configured:

1. Open GitHub Actions.
2. Select `Staging deployment validation`.
3. Click `Run workflow`.
4. Set `confirm_synthetic_data_only` to `true`.
5. Optionally set `deploy_ref` to a branch or commit.
6. Leave `run_restore_drill` off until the owner is ready to validate restore evidence.
7. Approve the `staging` Environment deployment when GitHub requests review.

The workflow uploads a `staging-evidence-<run-id>` artifact containing redacted deployment, health, backup, and validation evidence.

## Secret Rotation

Rotate staging secrets when:

- a team member with access leaves;
- a key might have been exposed;
- provider credentials change;
- staging is promoted to a stronger beta environment.

Update the GitHub Environment secret first, then rerun the workflow and verify readiness before removing the old credential from the VPS/provider.

## Future Auto-Deploy

Auto-deploy should remain disabled until manual staging has passed multiple owner-approved runs. See `docs/deployment/staging-auto-deploy-plan.md` for safe future options.
