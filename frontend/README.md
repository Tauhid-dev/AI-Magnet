# Business Portal

Phase 5 adds the tenant business portal as a Next.js, TypeScript, and TailwindCSS app.
Phase 6 adds the super admin portal in the same app under `/admin`.

## Local commands

```bash
cd frontend
npm install
npm run dev
```

The app expects the backend API at `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.

## Current scope

- Business password login with HttpOnly/SameSite browser sessions.
- Tenant dashboard.
- Knowledge document upload/status view.
- Leads and conversation review.
- Widget setup and key creation.
- Basic analytics.
- Super admin tenant management, usage, health, support, and audit views.
- Super admin password login with production TOTP enforcement.

Production browser sessions are stored in HttpOnly cookies and unsafe cookie-authenticated writes require the `X-AI-Magnet-CSRF` confirmation header. Local development may still use the bearer-token compatibility path for tests and scripts.

In production, every active `super_admin` must have `mfa_required=true` and a valid TOTP secret before login or existing session validation succeeds. Local/test setup may keep MFA disabled only outside production for developer ergonomics.

## Browser E2E tests

Playwright tests live in `e2e/` and can be run with:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

The committed suite starts the real Next.js frontend and mocks `NEXT_PUBLIC_API_BASE_URL` with synthetic API responses. It covers business login success/failure UI, portal setup/profile/knowledge/agent/leads/conversations/widget screens, admin login MFA UI, and admin tenant UI. Treat this as reproducible mocked browser coverage, not live backend/staging proof.
