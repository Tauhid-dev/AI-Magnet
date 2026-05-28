# Execution Log

Append-only production phase run history.

## 2026-05-28 - PR-00: Visible Roadmap, Persistent Memory and Verified Baseline

- Instruction received: Create the production-ready phase system and execute PR-00 only.
- Phase selected: PR-00.
- Branch: `production/pr-00-roadmap-memory-system`.
- Files changed:
  - `AGENTS.md`
  - `production-control/**`
- Implementation summary:
  - Inspected repository status, existing project-control docs, audit pack, security/deployment docs, and current source/config evidence.
  - Created `production-control/` as the production-remediation source of truth, preserving `project-control/` as historical MVP build evidence.
  - Created PR-00 through PR-12 roadmap, phase files, risk register, validation matrix, release gates, status JSON, Mermaid diagram, SVG diagram, and static HTML dashboard.
  - Added root Codex protocol for future short production phase commands.
  - Reconciled missing-items, security findings, and production-readiness findings into PR phase placements and release gates.
- Validations run/result:
  - `python3 -m json.tool production-control/status/production-status.json` - pass.
  - `git diff --check` - pass.
  - Static review of `production-control/visual/production-status-dashboard.html` - pass.
  - Static review of `production-control/visual/production-roadmap-status.svg` - pass.
  - Product runtime code unchanged - pass; changes are limited to `AGENTS.md` and `production-control/**`.
- Known gaps:
  - No PR-01 or later product remediation was implemented.
  - Production remains NO-GO beyond controlled internal demo with synthetic/sample data.
- Next phase permitted: PR-01.
- Commit hash: pending until commit.

## 2026-05-28 - PR-01: Production Authentication, Session Security and Admin Access

- Instruction received: `Implement production phase PR-01`.
- Phase selected: PR-01.
- Branch: `production/pr-01-auth-session-security`.
- Files changed:
  - Backend auth services, schemas, API routes, models, migration, seed helper, config, and tests.
  - Frontend login forms, API client, auth session helpers, logout flows, and tenant-create password field.
  - Production-control status, risk, validation, visual, and execution memory files.
- Implementation summary:
  - Replaced email-only business/admin login with password verification.
  - Added PBKDF2-SHA256 password hashing helpers and admin TOTP MFA verifier.
  - Added session-version revocation, failed-login lockout, last-login tracking, and logout endpoints.
  - Set HttpOnly/SameSite session cookies for browser sessions; frontend no longer stores bearer tokens in `localStorage`.
  - Added admin-provisioned owner password support during tenant creation.
  - Added migration `20260528_0006_pr01_auth_security.py`.
- Validations run/result:
  - `python3 -m pytest backend/tests` - pass, 48 tests.
  - `python3 -m ruff check backend` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr01_alembic.db python3 -m alembic -c backend/alembic.ini upgrade head` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr01_alembic.db python3 -m alembic -c backend/alembic.ini downgrade base` - pass.
  - `npm run typecheck` - pass.
  - `npm test` - pass.
  - `npm run lint` - pass.
  - `npm run build` - pass.
- Known gaps:
  - PR-02 still must add public endpoint rate limiting, CSRF/CSP/security-header review, and widget origin enforcement.
  - Admin MFA enrollment/rotation UI is not implemented in PR-01; the backend enforcement path exists.
  - Production remains NO-GO beyond controlled internal demo until PR-01 through PR-05 are all verified for Gate B.
- Next phase permitted: PR-02.
- Commit hash: pending until commit.

## 2026-05-28 - PR-02: Public API Abuse Protection, Widget Origin Controls and API Security

- Instruction received: `Implement production phase PR-02`.
- Phase selected: PR-02.
- Branch: `production/pr-02-api-abuse-widget-security`.
- Files changed:
  - Backend API/security/config: `.env.example`, `backend/app/core/rate_limit.py`, `backend/app/core/config.py`, `backend/app/core/security.py`, `backend/app/main.py`, `backend/app/api/session_cookies.py`, `backend/app/api/widget.py`, `backend/app/api/chat.py`, `backend/app/api/business_portal.py`, `backend/app/api/admin.py`.
  - Widget/service/schemas/usage: `backend/app/widget/service.py`, `backend/app/business/service.py`, `backend/app/schemas/*`, `backend/app/usage/taxonomy.py`.
  - Frontend portal/API: `frontend/app/portal/widget/page.tsx`, `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`.
  - Tests: `backend/tests/business/test_business_portal_api.py`, `backend/tests/chat/test_chat_api.py`, `backend/tests/security/test_security_boundaries.py`.
  - Production-control status, risks, validation, roadmap, and visual artifacts.
- Implementation summary:
  - Added an app-level in-memory rate limiter with endpoint-specific scopes for business/admin login, public widget init, chat start/message, portal writes, widget key operations, document ingestion, lead status updates, and high-risk admin writes.
  - Added cookie-session CSRF confirmation for unsafe portal/admin requests via `X-AI-Magnet-CSRF`, while retaining bearer-token compatibility for API clients/tests.
  - Added CSP to security headers and added the CSRF header to CORS allowed headers.
  - Added normalized widget allowed-origin enforcement, production startup validation requiring widget origin enforcement, and widget key create/update-origins/rotate/disable/revoke APIs.
  - Added portal widget UI controls for allowed origins and key lifecycle operations.
  - Added payload length bounds for widget/chat/lead input surfaces.
- Validations run/result:
  - `python3 -m pytest backend/tests/business/test_business_portal_api.py backend/tests/chat/test_chat_api.py backend/tests/security/test_security_boundaries.py` - pass.
  - `python3 -m ruff check backend/app backend/tests` - pass.
  - `npm run lint` - pass.
  - `npm run typecheck` - pass.
  - `python3 -m pytest backend/tests` - pass.
  - `npm test` - pass.
  - `npm run build` - pass.
  - `python3 -m json.tool production-control/status/production-status.json` - pass.
  - `git diff --check` - pass.
- Known gaps:
  - The new limiter is per-process and in-memory. PR-04/PR-05 must add proxy/distributed controls before production-scale or horizontally scaled deployment.
  - PR-04 must verify production topology, headers at Nginx, private DB/Redis, and production env enforcement.
  - Gate B remains NO-GO until PR-03, PR-04, and PR-05 are also verified.
- Next phase permitted: PR-03.
- Commit hash: pending until commit.

## 2026-05-28 - PR-03: Tenant Isolation, Data Lifecycle, Privacy and Database Integrity

- Instruction received: `Implement production phase PR-03`.
- Phase selected: PR-03.
- Branch: `production/pr-03-tenant-privacy-db-integrity`.
- Files changed:
  - Backend models/migration/config: `.env.example`, `backend/app/models/*`, `backend/app/core/config.py`, `backend/app/core/privacy.py`, `backend/migrations/versions/20260528_0007_pr03_tenant_privacy_integrity.py`.
  - Backend admin/audit APIs: `backend/app/admin/service.py`, `backend/app/api/admin.py`, `backend/app/audit/service.py`, `backend/app/schemas/admin.py`.
  - Frontend admin/API: `frontend/app/admin/tenants/[tenantId]/page.tsx`, `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`.
  - Tests/docs/status: `backend/tests/security/test_pr03_tenant_integrity.py`, `backend/tests/admin/test_admin_api.py`, `docs/security.md`, and production-control status/risk/validation/visual artifacts.
- Implementation summary:
  - Added database same-tenant integrity constraints for business users, document chunks, messages, leads, notification settings, and notification deliveries.
  - Added tenant lifecycle fields for offboarding, deletion request time, and retention deadline.
  - Added admin privacy export, offboard, and confirmed tenant deletion endpoints with frontend admin controls.
  - Added global admin audit logs that survive tenant deletion and redact likely PII in audit attributes.
  - Added migration checks that fail before constraints if existing cross-tenant relationships are detected.
- Validations run/result:
  - `python3 -m pytest backend/tests/security/test_pr03_tenant_integrity.py backend/tests/admin/test_admin_api.py` - pass, 9 tests.
  - `python3 -m pytest backend/tests` - pass, 56 tests.
  - `python3 -m ruff check backend/app backend/tests` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr03_alembic_20260528_2.db python3 -m alembic -c backend/alembic.ini upgrade head` - pass.
  - `DATABASE_URL=sqlite:////private/tmp/ai_magnet_pr03_alembic_20260528_2.db python3 -m alembic -c backend/alembic.ini downgrade 20260528_0006` - pass.
  - `npm run lint` - pass.
  - `npm run typecheck` - pass.
  - `npm test` - pass.
  - `npm run build` - pass.
  - `python3 -m json.tool production-control/status/production-status.json` - pass.
  - `python3 -c "import xml.etree.ElementTree as ET; ET.parse('production-control/visual/production-roadmap-status.svg'); print('svg ok')"` - pass.
  - `git diff --check` - pass.
- Known gaps:
  - Gate B remains NO-GO until PR-04 and PR-05 are also verified.
  - PR-04 must still deliver production TLS/HSTS, private PostgreSQL/Redis topology, secret validation, backups/restore, CI scans, production PostgreSQL/pgvector validation, and minimum operational logging/correlation IDs.
  - Privacy lifecycle is beta-scope platform admin controlled; customer self-service export/delete UX remains outside PR-03.
- Next phase permitted: PR-04.
- Commit hash: pending until commit.
