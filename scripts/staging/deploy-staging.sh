#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-$(pwd)}}"
COMPOSE_FILE="${STAGING_COMPOSE_FILE:-${COMPOSE_FILE:-docker-compose.prod.yml}}"
ENV_FILE="${ENV_FILE:-.env.staging}"
DEPLOY_REF="${STAGING_BRANCH:-${DEPLOY_REF:-master}}"
DEPLOY_COMMIT="${STAGING_COMMIT:-}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ai_magnet_staging}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-180}"

info() {
  printf '[deploy] %s\n' "$*"
}

fail() {
  printf '[deploy] ERROR: %s\n' "$*" >&2
  exit 1
}

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" "$@"
}

[ -d "$APP_DIR" ] || fail "Application directory does not exist: $APP_DIR"
cd "$APP_DIR"

[ -d .git ] || fail "$APP_DIR is not a git checkout"
[ -f "$ENV_FILE" ] || fail "Missing staging environment file: $ENV_FILE"
[ -f "$COMPOSE_FILE" ] || fail "Missing compose file: $COMPOSE_FILE"

info "Fetching repository metadata."
git fetch origin --prune

if [ -n "$DEPLOY_COMMIT" ]; then
  info "Checking out requested commit."
  git checkout --detach "$DEPLOY_COMMIT"
elif git show-ref --verify --quiet "refs/remotes/origin/$DEPLOY_REF"; then
  info "Checking out origin/$DEPLOY_REF."
  git checkout -B "$DEPLOY_REF" "origin/$DEPLOY_REF"
else
  info "Checking out deploy ref $DEPLOY_REF."
  git checkout --detach "$DEPLOY_REF"
fi

info "Validating Docker Compose configuration."
compose config --quiet

info "Building staging images."
compose build

info "Running database migrations."
compose run --rm backend python -m alembic -c backend/alembic.ini upgrade head

info "Starting staging services."
compose up -d --remove-orphans

info "Waiting for backend readiness."
deadline=$((SECONDS + HEALTH_TIMEOUT_SECONDS))
until compose exec -T backend python - <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/ready", timeout=5) as response:
        sys.exit(0 if response.status == 200 else 1)
except Exception:
    sys.exit(1)
PY
do
  if [ "$SECONDS" -ge "$deadline" ]; then
    compose ps
    fail "Backend readiness did not pass within ${HEALTH_TIMEOUT_SECONDS}s"
  fi
  sleep 5
done

info "Waiting for frontend health."
deadline=$((SECONDS + HEALTH_TIMEOUT_SECONDS))
until compose exec -T frontend node -e "fetch('http://127.0.0.1:3000').then((r)=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
do
  if [ "$SECONDS" -ge "$deadline" ]; then
    compose ps
    fail "Frontend health did not pass within ${HEALTH_TIMEOUT_SECONDS}s"
  fi
  sleep 5
done

info "Staging deploy completed for commit $(git rev-parse --short HEAD)."
