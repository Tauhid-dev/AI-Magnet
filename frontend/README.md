# Business Portal

Phase 5 adds the tenant business portal as a Next.js, TypeScript, and TailwindCSS app.

## Local commands

```bash
cd frontend
npm install
npm run dev
```

The app expects the backend API at `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.

## Current scope

- Business login and signed session storage.
- Tenant dashboard.
- Knowledge document upload/status view.
- Leads and conversation review.
- Widget setup and key creation.
- Basic analytics.

The current login flow is an MVP tenant-session contract for active `BusinessUser` records. Production password or identity-provider authentication should be hardened before launch.
