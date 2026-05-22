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

- Business login and signed session storage.
- Tenant dashboard.
- Knowledge document upload/status view.
- Leads and conversation review.
- Widget setup and key creation.
- Basic analytics.
- Super admin tenant management, usage, health, support, and audit views.

The current login flow is an MVP tenant-session contract for active `BusinessUser` records. Production password or identity-provider authentication should be hardened before launch.

The admin login flow is a separate MVP session contract for active `AdminUser` records with the `super_admin` role.
