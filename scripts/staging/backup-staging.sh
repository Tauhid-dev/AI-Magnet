#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-$(pwd)}}"
COMPOSE_FILE="${STAGING_COMPOSE_FILE:-${COMPOSE_FILE:-docker-compose.prod.yml}}"
ENV_FILE="${ENV_FILE:-.env.staging}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ai_magnet_staging}"
TIMESTAMP="${STAGING_EVIDENCE_TIMESTAMP:-$(date -u +%Y%m%d_%H%M%S)}"
BACKUP_ROOT="${STAGING_BACKUP_DIR:-staging-evidence/${TIMESTAMP}/backups}"

info() {
  printf '[backup] %s\n' "$*"
}

fail() {
  printf '[backup] ERROR: %s\n' "$*" >&2
  exit 1
}

cd "$APP_DIR"
[ -f "$ENV_FILE" ] || fail "Missing staging environment file: $ENV_FILE"
[ -f "$COMPOSE_FILE" ] || fail "Missing compose file: $COMPOSE_FILE"
mkdir -p "$BACKUP_ROOT"

info "Creating encrypted PostgreSQL backup."
COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME" \
COMPOSE_FILE="$COMPOSE_FILE" \
ENV_FILE="$ENV_FILE" \
BACKUP_DIR="$BACKUP_ROOT/postgres" \
scripts/backup_postgres.sh | tee "$BACKUP_ROOT/postgres-backup-path.txt"

info "Capturing encrypted document storage archive if backend storage exists."
if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" ps backend >/dev/null 2>&1; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
  : "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" exec -T backend \
    tar -C /app/storage -cf - documents 2>/dev/null \
    | openssl enc -aes-256-cbc -salt -pbkdf2 -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
      -out "$BACKUP_ROOT/document_storage_${TIMESTAMP}.tar.enc" || true
  if [ -s "$BACKUP_ROOT/document_storage_${TIMESTAMP}.tar.enc" ]; then
    chmod 600 "$BACKUP_ROOT/document_storage_${TIMESTAMP}.tar.enc"
    info "Document storage archive created."
  else
    info "No document storage archive was produced; this may be expected before document smoke tests."
  fi
fi

info "Backup evidence written to $BACKUP_ROOT."
