#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-$(pwd)}}"
COMPOSE_FILE="${STAGING_COMPOSE_FILE:-${COMPOSE_FILE:-docker-compose.prod.yml}}"
ENV_FILE="${ENV_FILE:-.env.staging}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ai_magnet_staging}"
STAGING_DOMAIN="${STAGING_DOMAIN:-}"
BASE_URL="${STAGING_BASE_URL:-}"
RUN_RESTORE_DRILL="${RUN_RESTORE_DRILL:-false}"
TIMESTAMP="${STAGING_EVIDENCE_TIMESTAMP:-$(date -u +%Y%m%d_%H%M%S)}"
OUTPUT_DIR="${VALIDATION_OUTPUT_DIR:-staging-evidence/${TIMESTAMP}/validation}"

info() {
  printf '[validate] %s\n' "$*" | tee -a "$OUTPUT_DIR/validation.log"
}

manual_required() {
  printf 'MANUAL_EVIDENCE_REQUIRED: %s\n' "$*" | tee -a "$OUTPUT_DIR/manual-evidence-required.log"
}

fail() {
  printf '[validate] ERROR: %s\n' "$*" | tee -a "$OUTPUT_DIR/validation.log" >&2
  exit 1
}

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" "$@"
}

mkdir -p "$OUTPUT_DIR"
cd "$APP_DIR"

[ -f "$ENV_FILE" ] || fail "Missing staging environment file: $ENV_FILE"
[ -f "$COMPOSE_FILE" ] || fail "Missing compose file: $COMPOSE_FILE"

if [ -z "$BASE_URL" ] && [ -n "$STAGING_DOMAIN" ]; then
  BASE_URL="https://${STAGING_DOMAIN}"
fi

info "Rendering compose configuration."
compose config --quiet
compose ps | tee "$OUTPUT_DIR/docker-compose-ps.txt"

info "Checking backend health and readiness inside the Docker network."
compose exec -T backend python - <<'PY' | tee "$OUTPUT_DIR/backend-health.json"
import json
import urllib.request

for path in ("/health", "/ready"):
    with urllib.request.urlopen(f"http://127.0.0.1:8000{path}", timeout=10) as response:
        body = response.read().decode("utf-8", errors="replace")
        print(json.dumps({"path": path, "status": response.status, "body": body[:1000]}))
PY

info "Checking frontend from inside its container."
compose exec -T frontend node -e "fetch('http://127.0.0.1:3000').then(async (r)=>{console.log(JSON.stringify({status:r.status,ok:r.ok})); process.exit(r.ok?0:1)}).catch((e)=>{console.error(e.message); process.exit(1)})" \
  | tee "$OUTPUT_DIR/frontend-health.json"

if [ -n "$BASE_URL" ]; then
  info "Checking public frontend URL and security headers."
  curl -fsSIL "$BASE_URL" | tee "$OUTPUT_DIR/public-headers.txt"
  if curl -fsSI "$BASE_URL" | grep -iq '^strict-transport-security:'; then
    info "HSTS header detected."
  else
    manual_required "Verify HSTS once TLS is issued and Nginx uses the production HTTPS template."
  fi
  if [ "${BASE_URL#https://}" != "$BASE_URL" ]; then
    http_url="http://${BASE_URL#https://}"
    curl -fsSI "$http_url" | tee "$OUTPUT_DIR/http-redirect-headers.txt" || true
    if grep -Eiq '^location: https://' "$OUTPUT_DIR/http-redirect-headers.txt"; then
      info "HTTP-to-HTTPS redirect evidence captured."
    else
      manual_required "Verify HTTP-to-HTTPS redirect after DNS and TLS are owner-approved."
    fi
  fi
else
  manual_required "Set STAGING_DOMAIN or STAGING_BASE_URL to validate external frontend reachability and TLS headers."
fi

info "Checking PostgreSQL, migration version and pgvector from inside the Docker network."
compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "select version(); select extname || '"'"':'"'"' || extversion from pg_extension where extname = '"'"'vector'"'"';"' \
  | tee "$OUTPUT_DIR/postgres-pgvector.txt"
compose run --rm backend python -m alembic -c backend/alembic.ini current \
  | tee "$OUTPUT_DIR/alembic-current.txt"

info "Checking Redis and worker health."
compose exec -T redis redis-cli ping | tee "$OUTPUT_DIR/redis-ping.txt"
compose exec -T worker python -m app.workers.healthcheck | tee "$OUTPUT_DIR/worker-health.txt"

info "Checking host-level exposed ports for PostgreSQL and Redis."
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | tee "$OUTPUT_DIR/listening-ports.txt" >/dev/null || true
  if grep -Eq ':(5432|6379)[[:space:]]' "$OUTPUT_DIR/listening-ports.txt"; then
    fail "Host appears to expose PostgreSQL or Redis ports. Review firewall and compose configuration."
  fi
else
  manual_required "Run 'ss -ltnp' or cloud firewall proof to show PostgreSQL 5432 and Redis 6379 are not public."
fi

manual_required "Create or verify a synthetic tenant/business account and record business login evidence."
manual_required "Validate production-style admin MFA login with synthetic credentials without storing the MFA secret in artifacts."
manual_required "Submit a controlled synthetic website/sitemap and capture ingestion status evidence."
manual_required "Upload a synthetic document fixture and capture extraction/indexing evidence."
manual_required "Ask a synthetic RAG question and capture citation metadata evidence."
manual_required "Run a live multi-worker job claim smoke and capture no-duplicate-claim evidence."
manual_required "Trigger a rate-limit denial and capture persisted abuse analytics evidence."
manual_required "Trigger quota/abuse limit behaviour and capture graceful user-facing response evidence."
manual_required "Attach live logging/alerting proof from the owner-approved staging monitoring target."

if [ "$RUN_RESTORE_DRILL" = "true" ]; then
  info "Running owner-requested restore drill."
  CONFIRM_RESTORE_DRILL=RESTORE_DRILL_ONLY scripts/staging/restore-staging-drill.sh | tee "$OUTPUT_DIR/restore-drill.txt"
else
  manual_required "Run restore drill with run_restore_drill=true after owner approval and backup evidence."
fi

info "Running staging backup framework smoke."
scripts/staging/backup-staging.sh | tee "$OUTPUT_DIR/backup-staging.txt"

info "Validation completed. Manual evidence items remain gates until PR-14B runs in owner-approved staging."
