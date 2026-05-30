# Frontend E2E Tests

This directory contains Playwright browser tests for the Next.js customer portal and admin console.

## Coverage Boundary

The committed PR-13A E2E suite is UI-level browser coverage with synthetic API mocking. It starts the real frontend app, renders real routes, exercises form and navigation behavior in Chromium, and intercepts calls to `NEXT_PUBLIC_API_BASE_URL` with deterministic in-memory responses.

This does not prove live backend, database, Redis, MFA TOTP, rate-limit, worker, widget-origin, or production cookie integration. Those remain backend tests plus staging/VPS validation evidence.

## Local Run

```bash
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

The Playwright config starts Next.js on `http://127.0.0.1:3100` and points the frontend API client at `http://127.0.0.1:8000`, which the tests intercept.

## Scripts

- `npm run test:e2e` runs the Chromium E2E suite.
- `npm run test:e2e:report` opens the latest Playwright HTML report.

## Current Flow Coverage

| Area | Flow | Data source |
|---|---|---|
| Business auth | Login failure, login success, redirect to `/portal` | Synthetic mocked API |
| Customer portal | Overview, setup checklist, profile save, knowledge source add, agent sandbox with citation, leads update, conversation detail, widget title/origin controls and embed snippet | Synthetic mocked API |
| Admin auth | MFA input visibility, failed login without MFA, successful login with MFA code | Synthetic mocked API |
| Admin console | Overview metrics and tenant creation UI | Synthetic mocked API |

## CI Wiring For Agent D

Agent C did not edit `.github/workflows/ci.yml` because the delegated ownership scope was frontend-owned files only. A stable CI addition would be:

```yaml
- name: Install Playwright Chromium
  run: npx playwright install --with-deps chromium

- name: Run frontend E2E
  run: npm run test:e2e
```

Place those steps in the existing frontend job after `npm ci` and before or after `npm run build`. The tests are mocked browser coverage; CI status should not be described as full backend E2E proof.
