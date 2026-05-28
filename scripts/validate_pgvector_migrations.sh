#!/usr/bin/env sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm backend \
  python -m alembic -c backend/alembic.ini upgrade head

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "CREATE EXTENSION IF NOT EXISTS vector;" \
  -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';" \
  -c "SELECT '[0.1,0.2,0.3]'::vector AS vector_smoke;"
