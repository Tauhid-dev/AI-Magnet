#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-$(pwd)}}"
COMPOSE_FILE="${STAGING_COMPOSE_FILE:-${COMPOSE_FILE:-docker-compose.prod.yml}}"
ENV_FILE="${ENV_FILE:-.env.staging}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ai_magnet_staging}"
STAGING_DOMAIN="${STAGING_DOMAIN:-}"
BASE_URL="${STAGING_BASE_URL:-}"
TIMESTAMP="${STAGING_EVIDENCE_TIMESTAMP:-$(date -u +%Y%m%d_%H%M%S)}"
EVIDENCE_DIR="${EVIDENCE_DIR:-staging-evidence/${TIMESTAMP}}"

info() {
  printf '[evidence] %s\n' "$*"
}

redact() {
  sed -E \
    -e 's/(password|secret|token|api[_-]?key|mfa)[^[:space:]=:"]*([=:"]+)[^[:space:]"'\''`]+/\1\2[REDACTED]/Ig' \
    -e 's/(Authorization: Bearer )[A-Za-z0-9._~+\/=-]+/\1[REDACTED]/Ig' \
    -e 's/(Cookie: )[^\r\n]+/\1[REDACTED]/Ig'
}

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT_NAME" "$@"
}

cd "$APP_DIR"
mkdir -p "$EVIDENCE_DIR"

{
  echo "captured_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "app_dir=$APP_DIR"
  echo "compose_file=$COMPOSE_FILE"
  echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
} > "$EVIDENCE_DIR/summary.txt"

info "Capturing Docker service status."
compose ps > "$EVIDENCE_DIR/docker-compose-ps.txt" 2>&1 || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' > "$EVIDENCE_DIR/docker-ps.txt" 2>&1 || true
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}' > "$EVIDENCE_DIR/docker-images.txt" 2>&1 || true
compose config > "$EVIDENCE_DIR/compose-config-rendered.yml" 2>&1 || true
redact < "$EVIDENCE_DIR/compose-config-rendered.yml" > "$EVIDENCE_DIR/compose-config-rendered.redacted.yml" || true
rm -f "$EVIDENCE_DIR/compose-config-rendered.yml"

info "Capturing health and readiness evidence."
compose exec -T backend python - <<'PY' > "$EVIDENCE_DIR/backend-health-ready.json" 2>&1 || true
import json
import urllib.request

for path in ("/health", "/ready"):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8000{path}", timeout=10) as response:
            print(json.dumps({"path": path, "status": response.status, "body": response.read().decode("utf-8", errors="replace")[:2000]}))
    except Exception as exc:
        print(json.dumps({"path": path, "error": str(exc)}))
PY

info "Capturing TLS and header evidence where available."
if [ -z "$BASE_URL" ] && [ -n "$STAGING_DOMAIN" ]; then
  BASE_URL="https://${STAGING_DOMAIN}"
fi
if [ -n "$BASE_URL" ]; then
  curl -fsSIL "$BASE_URL" > "$EVIDENCE_DIR/public-headers.txt" 2>&1 || true
  echo | openssl s_client -servername "${BASE_URL#https://}" -connect "${BASE_URL#https://}:443" -brief \
    > "$EVIDENCE_DIR/tls-s_client.txt" 2>&1 || true
else
  echo "MANUAL_EVIDENCE_REQUIRED: Set STAGING_DOMAIN/STAGING_BASE_URL for public TLS/header capture." > "$EVIDENCE_DIR/tls-manual-required.txt"
fi

info "Capturing firewall and private-port evidence."
if command -v ss >/dev/null 2>&1; then
  ss -ltnp > "$EVIDENCE_DIR/listening-ports.txt" 2>&1 || true
else
  echo "MANUAL_EVIDENCE_REQUIRED: Capture host listening ports with ss/netstat and cloud firewall rules." > "$EVIDENCE_DIR/firewall-manual-required.txt"
fi

info "Capturing migration, pgvector, Redis and worker status."
compose run --rm backend python -m alembic -c backend/alembic.ini current > "$EVIDENCE_DIR/alembic-current.txt" 2>&1 || true
compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "select extname || '"'"':'"'"' || extversion from pg_extension where extname = '"'"'vector'"'"';"' \
  > "$EVIDENCE_DIR/pgvector-extension.txt" 2>&1 || true
compose exec -T redis redis-cli ping > "$EVIDENCE_DIR/redis-ping.txt" 2>&1 || true
compose exec -T worker python -m app.workers.healthcheck > "$EVIDENCE_DIR/worker-health.txt" 2>&1 || true

info "Capturing recent redacted service logs."
mkdir -p "$EVIDENCE_DIR/logs"
for service in backend worker frontend nginx postgres redis; do
  compose logs --tail=200 "$service" 2>&1 | redact > "$EVIDENCE_DIR/logs/${service}.log" || true
done

if [ -d "staging-evidence" ]; then
  find staging-evidence -maxdepth 3 -type f \( -name '*validation*' -o -name '*backup*' -o -name '*restore*' \) \
    -not -path "${EVIDENCE_DIR}/*" -print > "$EVIDENCE_DIR/related-evidence-files.txt" 2>/dev/null || true
fi

info "Evidence bundle written to $EVIDENCE_DIR."
