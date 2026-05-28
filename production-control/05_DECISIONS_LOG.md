# Decisions Log

Append-only ADR-lite log for production remediation.

## DEC-PR-20260528-001: Separate Production Remediation From MVP Build History

- Date: 2026-05-28
- Decision: Create `production-control/` as the source of truth for PR-00 through PR-12 production-remediation work, while preserving `project-control/` as historical MVP build evidence and memory.
- Reason: The original MVP Phase 0-10 roadmap tracks build progress and overstates production readiness if reused as launch evidence. The new `PR-*` roadmap maps audit blockers to explicit production gates.
- Affected files/phases: `production-control/*`, `AGENTS.md`, all PR phases.
- Alternatives rejected:
  - Overwrite `project-control/` status files: rejected because it would blur historical MVP implementation state with production remediation.
  - Keep only the audit report: rejected because future Codex runs need executable phase files, status JSON, and visual gates.
- Follow-up impact: Future short commands such as `Implement production phase PR-01` must use `production-control/`, not the historical MVP roadmap.

## DEC-PR-20260528-002: Keep Architecture Generic, Tradie-First

- Date: 2026-05-28
- Decision: Production remediation should preserve AI-Magnet as a reusable multi-tenant RAG agent SaaS, with tradie receptionist as the first-market positioning.
- Reason: Website/sitemap/document ingestion, tenant isolation, source-grounded answers, widget deployment, lead capture, analytics, and admin operations are reusable across many SMB verticals.
- Affected files/phases: PR-00 through PR-12.
- Alternatives rejected:
  - Hard-code tradie-only product concepts into core architecture.
  - Rewrite the platform for a new generic product before hardening.
- Follow-up impact: New code should keep vertical-specific labels/content at UI/config boundaries where practical.

## DEC-PR-20260528-003: PR-00 Does Not Implement Production Remediation

- Date: 2026-05-28
- Decision: PR-00 creates the production-control memory, roadmap, visual status, and protocol only.
- Reason: The user explicitly limited this first run to PR-00. Production feature remediation begins with PR-01.
- Affected files/phases: PR-00.
- Alternatives rejected:
  - Fix auth or infra during PR-00.
  - Mark later phases partially complete because MVP foundations exist.
- Follow-up impact: PR-01 is the next permitted implementation phase.

## DEC-PR-20260528-004: Password Auth With Cookie Sessions For PR-01

- Date: 2026-05-28
- Decision: Implement production authentication using PBKDF2-SHA256 password hashes, per-account failed-login lockout, session-version revocation, and HttpOnly/SameSite browser cookies. Retain bearer-token compatibility for API clients and tests, but the frontend no longer stores bearer tokens in `localStorage`.
- Reason: The current stack can support password auth immediately without introducing an external identity provider. Cookie-backed browser sessions remove the highest-risk token storage issue while keeping existing API structure stable.
- Affected files/phases: PR-01, `backend/app/business/auth.py`, `backend/app/admin/auth.py`, `backend/app/api/*`, `frontend/lib/auth/*`, `frontend/lib/api/client.ts`, migrations and tests.
- Alternatives rejected:
  - Keep email-only auth until an identity provider is selected: rejected because it keeps the critical blocker open.
  - Build a full external IdP integration in PR-01: rejected as too large for the current stack and not necessary to remove the immediate blocker.
- Follow-up impact: PR-02 must complete CSRF/CSP/security-header review for cookie sessions and public endpoint abuse controls.

## DEC-PR-20260528-005: Admin MFA Uses TOTP Enrollment Fields

- Date: 2026-05-28
- Decision: Add admin `mfa_required` and `mfa_secret` fields and require valid TOTP codes when MFA is enabled.
- Reason: This gives the platform a strong admin-authentication path without depending on SMS, email-only codes, or a future premium module.
- Affected files/phases: PR-01, `backend/app/models/admin.py`, `backend/app/core/totp.py`, admin API/tests.
- Alternatives rejected:
  - SMS/WhatsApp MFA: rejected because those channels are explicitly deferred.
  - Email OTP only: rejected because email-only administrator proof is not strong enough for the critical admin-auth blocker.
- Follow-up impact: PR-09 or a later admin UX pass should add guided MFA enrollment/rotation UI; PR-04 should address secret-handling hardening.
