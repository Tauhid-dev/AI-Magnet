# PR-09: Customer Onboarding, Agent Testing and Widget Installation Experience

Status: verified

## Purpose

Turn hardened backend capabilities into a controlled beta-ready customer workflow.

## Why It Is Needed

The current portal has useful MVP screens, but a tenant cannot complete a production-grade setup flow from account to approved knowledge to grounded agent testing to controlled widget installation.

## Preconditions

- PR-08 is verified.
- Auth, ingestion, RAG, and widget origin controls are available.

## In-Scope Work

- Secure customer onboarding and business profile configuration.
- Knowledge setup UI for website, sitemap, documents, indexing progress, failures, refresh, and delete.
- Agent sandbox/test UI showing responses and sources.
- Widget setup UI for approved domains, beta-scope branding controls, key rotation/revocation, and copyable embed snippet.
- Conversation and lead review UX with meaningful empty/loading/error states.
- Accessibility, responsive layout, and browser end-to-end coverage for primary flows.

## Out-Of-Scope Work

- Public SEO/marketing pages unless separately requested.
- Streaming chat unless selected as beta UX requirement.
- Advanced CRM.

## Source Areas Likely Affected

- `frontend/app/portal/`
- `frontend/components/`
- `frontend/lib/api/`
- `backend/app/api/business_portal.py`
- `backend/app/schemas/`
- `widget/chat-widget.js`
- `frontend/tests/`
- `backend/tests/`

## Detailed Tasks

- [x] Map end-to-end tenant setup journey.
- [x] Add onboarding/business profile screens.
- [x] Add knowledge setup and job status UI.
- [x] Add agent sandbox with citations.
- [x] Add widget domain/key/branding controls.
- [x] Improve conversations/leads UX states.
- [x] Add responsive/accessibility checks.
- [x] Add committed/reproducible browser/e2e tests. Reopened by PR-13 and closed by PR-13A with Playwright Chromium tests for supported business/admin flows using synthetic API mocks.
- [x] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Frontend lint/typecheck/test/build.
- Browser/e2e tests for onboarding, ingestion, agent test, widget setup, leads. PR-13A adds committed Playwright tests for supported browser flows; PR-14 must still run live backend-integrated smoke before real customer pilot use.
- Backend API tests for new workflow routes.

## Security Considerations

Do not expose secrets or private tenant IDs unnecessarily. Widget keys remain public identifiers and must be revocable.

## Migration And Rollback Notes

Schema changes may be needed for onboarding/profile/branding. Provide migrations and data defaults.

## Evidence

- Backend profile, agent sandbox, widget branding, and tenant-scoped portal APIs: `backend/app/api/business_portal.py`, `backend/app/business/service.py`, `backend/app/schemas/business_portal.py`, `backend/app/widget/service.py`.
- Frontend setup, agent test, knowledge-job, widget branding/copy, leads, and conversations UX: `frontend/app/portal/onboarding/page.tsx`, `frontend/app/portal/agent/page.tsx`, `frontend/app/portal/documents/page.tsx`, `frontend/app/portal/widget/page.tsx`, `frontend/app/portal/leads/page.tsx`, `frontend/app/portal/conversations/page.tsx`, `frontend/components/PortalShell.tsx`.
- API client/types and static checks: `frontend/lib/api/client.ts`, `frontend/lib/api/types.ts`, `frontend/tests/static-check.mjs`.
- Committed browser evidence: `frontend/playwright.config.ts`, `frontend/e2e/business-portal.spec.ts`, `frontend/e2e/admin-console.spec.ts`, `frontend/e2e/support/mock-api.ts`, and `frontend/e2e/README.md`.
- Backend tests: `backend/tests/business/test_business_portal_api.py`.
- Validation: `backend/.venv/bin/python -m pytest backend/tests/business/test_business_portal_api.py` passed; `backend/.venv/bin/python -m pytest backend/tests` passed with 116 tests; `backend/.venv/bin/python -m ruff check backend/app backend/tests` passed; `npm run test`, `npm run typecheck`, `npm run lint`, `npm run build`, and `npm run test:e2e` passed. PR-13A browser tests are mocked UI-flow evidence, not live backend-integrated proof.

## Blockers

No repository-controlled High blocker remains after PR-13A. Live backend-integrated customer/admin/widget smoke on the target VPS/staging environment remains PR-14 external release-gate evidence.

## Completion Criteria

A test tenant can move from authenticated onboarding to safely indexed knowledge, source-grounded agent testing, and controlled widget setup without manual database intervention.
