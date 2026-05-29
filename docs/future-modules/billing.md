# Billing Premium Module Scope

## Status

PR-11 adds manual paid-beta subscription and entitlement controls. Stripe, checkout,
customer portal, webhook processing, card storage, and automated payment collection remain
future scope.

See `docs/paid-beta-readiness.md` for the current manual paid-beta workflow.

## Product intent

Billing should let the platform charge businesses for SaaS access and premium add-ons while keeping entitlements clear, auditable, and safe. The likely first billing provider is Stripe because it supports subscriptions, checkout, invoices, tax configuration, and webhooks.

## Candidate capabilities

- Tenant subscription plans.
- Trial period management.
- Plan limits for usage, documents, conversations, and premium add-ons.
- Stripe Checkout or customer portal for self-service billing.
- Webhook-driven subscription state updates.
- Super admin visibility into tenant plan and billing health.
- Entitlement checks for premium modules such as Voice AI, SMS, WhatsApp, and advanced automation.

## Out of scope for first release

- Marketplace payouts.
- Multi-currency complexity beyond the first target currency.
- Usage-based billing for every event from day one.
- Manual invoice reconciliation workflows.
- In-app card handling outside Stripe-hosted pages.
- Premium feature activation without server-side entitlement checks.

## Recommended plan model

Initial commercial packaging could use:

- Starter: chat widget, RAG knowledge base, lead capture, email notifications, basic analytics.
- Growth: higher usage limits, more documents, richer analytics, priority support.
- Premium add-ons: Voice AI, SMS/WhatsApp, advanced CRM/automation, local model/private deployment.

Each tenant should have:

- Current plan.
- Subscription status.
- Billing customer ID.
- Optional subscription ID.
- Entitlement flags or derived entitlements.
- Usage limits and reset window.
- Billing contact metadata.

## Stripe architecture

Use Stripe-hosted flows where possible:

- Checkout Session for new subscriptions.
- Customer Portal for card, invoice, and plan management.
- Webhooks for subscription lifecycle updates.
- Price IDs configured through environment variables or admin-managed settings.

Do not trust browser-provided billing status. Backend entitlement checks must be based on database state updated by verified webhooks or super admin override.

## Webhook requirements

Billing webhooks are security-sensitive.

Required controls:

- Verify Stripe webhook signatures.
- Store processed event IDs for idempotency.
- Process events asynchronously or with safe retry behavior.
- Keep raw event payload retention minimal.
- Never log card details or full billing payloads.
- Map Stripe customer/subscription IDs to exactly one tenant.

Important events:

- Checkout completed.
- Customer subscription created, updated, deleted.
- Invoice paid.
- Invoice payment failed.
- Trial ending.
- Payment method changed.

## Entitlement checks

Premium modules must check entitlements server-side before use.

Examples:

- Voice AI enabled for tenant.
- SMS channel enabled and monthly message quota available.
- WhatsApp channel enabled and provider onboarding complete.
- Automation workflows enabled.
- Local model/private deployment flag enabled.

Entitlement checks should happen in services and API routes, not only frontend navigation.

## Failure handling

Billing failure should degrade gracefully.

Recommended states:

- trialing
- active
- past_due
- unpaid
- canceled
- suspended

Operational behavior:

- Warn tenants before suspending access where possible.
- Keep existing data available to admins according to policy.
- Disable premium add-ons before disabling core access.
- Log super admin billing overrides.

## Australian business considerations

Before production billing:

- Confirm GST handling.
- Confirm invoice requirements.
- Prepare terms, refund policy, and privacy policy.
- Confirm whether Stripe Tax or accountant-managed tax setup is used.
- Avoid storing card data directly in this platform.

## Security risks

- Forged webhook events.
- Cross-tenant subscription mapping errors.
- Feature access granted by stale browser state.
- Accidental exposure of billing IDs or invoices to other tenants.
- Subscription downgrade not reflected in entitlements.

Required controls:

- Signature verification.
- Idempotent event processing.
- Tenant-scoped entitlement table or derived entitlement service.
- Audit logs for manual billing overrides.
- Tests for webhook mapping and entitlement denial.

## Implementation gates

Do not implement billing until:

- Pricing model is approved.
- Stripe account and product/price strategy are ready.
- Terms, tax, refund, and privacy implications are reviewed.
- Entitlement model is designed.
- Webhook and idempotency strategy is approved.

## Suggested later phases

1. Plan and entitlement data model.
2. Stripe Checkout and Customer Portal integration.
3. Verified webhook receiver with idempotency.
4. Super admin billing status view.
5. Entitlement checks for premium modules.
6. Billing failure and suspension workflows.

## Acceptance checklist

- Plan model, webhooks, entitlement checks, and failure handling are documented.
- No billing implementation exists from Phase 10.
- Future code must keep billing state server-side and tenant-scoped.
