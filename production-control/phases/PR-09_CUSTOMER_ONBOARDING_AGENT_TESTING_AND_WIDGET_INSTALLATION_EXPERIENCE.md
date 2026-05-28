# PR-09: Customer Onboarding, Agent Testing and Widget Installation Experience

Status: not_started

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

- [ ] Map end-to-end tenant setup journey.
- [ ] Add onboarding/business profile screens.
- [ ] Add knowledge setup and job status UI.
- [ ] Add agent sandbox with citations.
- [ ] Add widget domain/key/branding controls.
- [ ] Improve conversations/leads UX states.
- [ ] Add responsive/accessibility checks.
- [ ] Add browser/e2e tests.
- [ ] Update status/risk/validation/visual artifacts.

## Tests And Validation Required

- Frontend lint/typecheck/test/build.
- Browser/e2e tests for onboarding, ingestion, agent test, widget setup, leads.
- Backend API tests for new workflow routes.

## Security Considerations

Do not expose secrets or private tenant IDs unnecessarily. Widget keys remain public identifiers and must be revocable.

## Migration And Rollback Notes

Schema changes may be needed for onboarding/profile/branding. Provide migrations and data defaults.

## Evidence

To be filled during PR-09.

## Blockers

Requires PR-08 source-grounded RAG behavior.

## Completion Criteria

A test tenant can move from authenticated onboarding to safely indexed knowledge, source-grounded agent testing, and controlled widget setup without manual database intervention.
