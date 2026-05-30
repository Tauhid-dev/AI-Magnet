#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-$(pwd)}}"
COMPOSE_FILE="${STAGING_COMPOSE_FILE:-${COMPOSE_FILE:-docker-compose.prod.yml}}"
ENV_FILE="${ENV_FILE:-.env.staging}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ai_magnet_staging}"
CONFIRM_RESTORE_DRILL="${CONFIRM_RESTORE_DRILL:-}"
BACKUP_PATH="${BACKUP_PATH:-}"
TIMESTAMP="${STAGING_EVIDENCE_TIMESTAMP:-$(date -u +%Y%m%d_%H%M%S)}"
RESTORE_DB="${RESTORE_DB:-ai_magnet_restore_drill_${TIMESTAMP}}"

info() {
  printf '[restore-drill] %s\n' "$*"
}

fail() {
  printf '[restore-drill] ERROR: %s\n' "$*" >&2
  exit 1
}

if [ "$CONFIRM_RESTORE_DRILL" != "RESTORE_DRILL_ONLY" ]; then
  fail "Set CONFIRM_RESTORE_DRILL=RESTORE_DRILL_ONLY to run the safe temporary restore drill."
fi

cd "$APP_DIR"
[ -f "$ENV_FILE" ] || fail "Missing staging environment file: $ENV_FILE"
[ -f "$COMPOSE_FILE" ] || fail "Missing compose file: $COMPOSE_FILE"

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"

if [ -z "$BACKUP_PATH" ]; then
  BACKUP_PATH="$(find staging-evidence -type f -name 'ai_magnet_*.dump.enc' 2>/dev/null | sort | tail -n 1 || true)"
fi

[ -n "$BACKUP_PATH" ] || fail "No encrypted PostgreSQL backup found. Set BACKUP_PATH explicitly."
[ -f "$BACKUP_PATH" ] || fail "Backup file not found: $BACKUP_PATH"

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" "$@"
}

info "Creating temporary restore database $RESTORE_DB."
compose exec -T postgres createdb -U "$POSTGRES_USER" "$RESTORE_DB"

cleanup() {
  if [ "${KEEP_RESTORE_DRILL_DB:-false}" != "true" ]; then
    info "Dropping temporary restore database $RESTORE_DB."
    compose exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$RESTORE_DB" || true
  else
    info "KEEP_RESTORE_DRILL_DB=true; temporary database retained for owner inspection."
  fi
}
trap cleanup EXIT

info "Restoring encrypted backup into temporary database only."
openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_ENCRYPTION_PASSPHRASE -in "$BACKUP_PATH" \
  | compose exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$RESTORE_DB" --no-owner

info "Checking restored database tables."
compose exec -T postgres psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -Atc "select count(*) from information_schema.tables where table_schema = 'public';"

info "Restore drill completed without touching staging database $POSTGRES_DB."
