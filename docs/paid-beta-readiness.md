# Paid Beta Readiness

## Status

PR-11 implements a controlled manual paid-beta entitlement path. It does not add Stripe,
card storage, payment webhooks, or self-service checkout.

## Commercial Decision

The first paid beta uses platform-owner approval and manual invoicing. This keeps payment
risk low while the product validates real customer onboarding, RAG quality, support load,
usage limits, and Australian SMB privacy operations.

## Entitlement Model

Each tenant can have one server-side subscription record:

- `pilot_trial`
- `starter_manual`
- `growth_manual`

Subscription status controls billable operations:

- `trialing` and `active` allow access within configured limits.
- `past_due`, `paused`, and `canceled` block billable chat, agent, document, and crawl work.
- Tenants without a subscription are treated as internal/demo tenants until an admin assigns
  a paid-beta plan.

The backend enforces plan limits through the existing quota service. The frontend only
displays subscription state; it is not trusted for entitlement decisions.

## Admin Workflow

1. Create or select a tenant in the super admin portal.
2. Open Admin > Billing.
3. Assign the tenant a plan and status.
4. Record the manual invoice or approval reference.
5. Review global and tenant audit logs for the entitlement change.
6. Monitor usage and quota warnings in Admin > Usage.

## Business Workflow

Businesses can open Portal > Billing to view:

- Current plan and subscription status.
- Manual payment collection notice.
- Usage limits and blocked states.
- Privacy export/deletion/offboarding expectations.
- Support escalation path.

## Privacy And Compliance

Paid beta remains blocked from self-service public signup until owner-approved release gates
pass. Before accepting broad paid usage:

- Confirm privacy policy, data retention, export, deletion, and offboarding language.
- Confirm GST/invoice handling and refund terms.
- Confirm support process and incident-response ownership.
- Confirm production deployment smoke tests, backups, and restore evidence.

No payment-card data is collected or stored by this application in PR-11.

## Future Stripe Path

Stripe remains deferred until pricing, tax, refund, and webhook operations are approved.
When implemented, the backend must verify webhook signatures, store processed event IDs,
map each Stripe customer to exactly one tenant, and keep entitlement state server-side.
