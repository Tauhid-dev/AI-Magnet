#!/usr/bin/env sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env}"
BACKUP_PATH="${1:-}"

if [ -z "$BACKUP_PATH" ]; then
  echo "Usage: $0 path/to/backup.dump.enc" >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if [ ! -f "$BACKUP_PATH" ]; then
  echo "Missing backup file: $BACKUP_PATH" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"

printf '%s\n' "This will restore into database '$POSTGRES_DB' and may replace existing data."
printf '%s' "Type RESTORE to continue: "
read -r CONFIRM
if [ "$CONFIRM" != "RESTORE" ]; then
  echo "Restore cancelled."
  exit 1
fi

openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
  -in "$BACKUP_PATH" \
  | docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner
