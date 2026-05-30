#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${STAGING_APP_DIR:-${APP_DIR:-/opt/ai-magnet-staging}}"
DEPLOY_USER="${DEPLOY_USER:-aimagnet}"
REPO_URL="${STAGING_REPO_URL:-${REPO_URL:-}}"
INSTALL_DOCKER="${INSTALL_DOCKER:-false}"
CREATE_DEPLOY_USER="${CREATE_DEPLOY_USER:-false}"
CONFIGURE_UFW="${CONFIGURE_UFW:-false}"
BOOTSTRAP_APT_UPDATE="${BOOTSTRAP_APT_UPDATE:-true}"
LOG_DIR="${LOG_DIR:-/var/log/ai-magnet-staging}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ai-magnet-staging}"

info() {
  printf '[bootstrap] %s\n' "$*"
}

warn() {
  printf '[bootstrap] WARNING: %s\n' "$*" >&2
}

run_as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  else
    sudo "$@"
  fi
}

if [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  if [ "${ID:-}" != "ubuntu" ] && [ "${ID_LIKE:-}" != "debian" ]; then
    warn "This helper is intended for Ubuntu/Debian-like staging VPS hosts."
  fi
fi

if [ "$BOOTSTRAP_APT_UPDATE" = "true" ]; then
  info "Updating package metadata."
  run_as_root apt-get update
fi

if ! command -v git >/dev/null 2>&1; then
  info "Installing git."
  run_as_root apt-get install -y git ca-certificates curl openssl
fi

if ! command -v docker >/dev/null 2>&1; then
  if [ "$INSTALL_DOCKER" = "true" ]; then
    info "Installing Docker using the official convenience script. Review this before use on hardened hosts."
    curl -fsSL https://get.docker.com | run_as_root sh
  else
    warn "Docker is not installed. Set INSTALL_DOCKER=true to install, or install Docker manually."
  fi
fi

if command -v docker >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
  warn "Docker Compose plugin is not available. Install docker-compose-plugin before running deployment."
fi

if [ "$CREATE_DEPLOY_USER" = "true" ]; then
  if id "$DEPLOY_USER" >/dev/null 2>&1; then
    info "Deploy user $DEPLOY_USER already exists."
  else
    info "Creating deploy user $DEPLOY_USER."
    run_as_root useradd --create-home --shell /bin/bash "$DEPLOY_USER"
  fi
  if command -v docker >/dev/null 2>&1; then
    run_as_root usermod -aG docker "$DEPLOY_USER"
  fi
fi

info "Creating staging directories."
run_as_root mkdir -p "$APP_DIR" "$LOG_DIR" "$BACKUP_DIR"
run_as_root chmod 750 "$APP_DIR" "$LOG_DIR" "$BACKUP_DIR"
if id "$DEPLOY_USER" >/dev/null 2>&1; then
  run_as_root chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR" "$LOG_DIR" "$BACKUP_DIR"
fi

if [ -n "$REPO_URL" ]; then
  if [ -d "$APP_DIR/.git" ]; then
    info "Repository already exists in $APP_DIR; fetching latest metadata."
    git -C "$APP_DIR" fetch origin --prune
  elif [ -z "$(find "$APP_DIR" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
    info "Cloning repository into $APP_DIR."
    git clone "$REPO_URL" "$APP_DIR"
  else
    warn "$APP_DIR is not empty and is not a git checkout; clone skipped."
  fi
else
  warn "REPO_URL/STAGING_REPO_URL not set; repository clone skipped."
fi

cat <<'GUIDANCE'

Firewall guidance:
- Expose only SSH, HTTP 80 and HTTPS 443 to the public internet.
- PostgreSQL and Redis must remain private to Docker internal networking.
- Review cloud firewall/security-list rules in addition to host firewall rules.

Optional UFW commands:
  sudo ufw allow OpenSSH
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw deny 5432/tcp
  sudo ufw deny 6379/tcp
  sudo ufw enable
GUIDANCE

if [ "$CONFIGURE_UFW" = "true" ]; then
  if ! command -v ufw >/dev/null 2>&1; then
    run_as_root apt-get install -y ufw
  fi
  run_as_root ufw allow OpenSSH
  run_as_root ufw allow 80/tcp
  run_as_root ufw allow 443/tcp
  run_as_root ufw deny 5432/tcp
  run_as_root ufw deny 6379/tcp
  info "UFW rules staged. Run 'sudo ufw status verbose' and enable manually if needed."
fi

info "Bootstrap review complete. No secrets were written by this script."
