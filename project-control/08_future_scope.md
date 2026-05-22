# Future Scope

## Purpose

This file records possible premium and future modules so they are not accidentally implemented during MVP work. These features require explicit approval, separate planning, and security/privacy review before implementation.

## Future premium modules

### Voice AI

Potential capabilities:

- AI receptionist for inbound calls.
- Call transcription and summaries.
- Lead capture from phone calls.
- Business handoff for urgent jobs.

Required before implementation:

- Consent model.
- Call recording policy.
- Provider selection.
- Latency and reliability review.
- Cost model.
- Australian privacy and telecommunications considerations.

### AI phone calling

Potential capabilities:

- Outbound follow-up calls.
- Missed-call recovery.
- Quote follow-up.

Required before implementation:

- Strong consent and opt-out workflow.
- Abuse prevention.
- Clear business approval before any outbound call.
- Legal and regulatory review.

### SMS

Potential capabilities:

- Lead follow-up messages.
- Appointment reminders.
- Missed enquiry recovery.

Required before implementation:

- Opt-in and opt-out rules.
- Provider selection.
- Message template controls.
- Cost and rate limit planning.

### WhatsApp

Potential capabilities:

- WhatsApp chat channel.
- Lead capture and follow-up.
- Conversation continuity with website chat.

Required before implementation:

- Provider and business verification plan.
- Consent and opt-out rules.
- Template approval workflow where required.
- Data retention and support model.

### Stripe billing

Potential capabilities:

- Subscription plans.
- Usage-based billing.
- Payment method management.
- Invoices and receipts.
- Entitlement checks.

Required before implementation:

- Pricing model.
- Plan limits.
- Webhook handling.
- Dunning and failed payment behavior.
- Access control for billing admins.

### Marketplace

Potential capabilities:

- Integrations marketplace.
- Templates for trades.
- Add-on modules.

Required before implementation:

- Stable core product.
- Extension model.
- Review and approval process.
- Support and versioning plan.

### Mobile app

Potential capabilities:

- Business owner mobile lead review.
- Push notifications.
- Simple lead reply tools.

Required before implementation:

- Mobile use case validation.
- Push notification privacy review.
- App store and release process.

### Advanced CRM

Potential capabilities:

- Sales pipeline.
- Job status tracking.
- Customer records.
- Follow-up reminders.
- External CRM integrations.

Required before implementation:

- Clear boundary between lead capture and CRM.
- Data export/import plan.
- Business workflow validation.

### n8n automation

Potential capabilities:

- Self-hosted workflow automation.
- Lead routing.
- Internal notifications.
- CRM handoff.

Required before implementation:

- Tenant-safe automation boundaries.
- Secret handling.
- Failure monitoring.
- Support ownership.

### Local model/Ollama support

Potential capabilities:

- Use self-hosted models for privacy or cost control.
- Offline or lower-cost deployments for some workloads.

Required before implementation:

- Provider abstraction stability.
- Model quality evaluation.
- Hardware cost review.
- Deployment and monitoring plan.

### Multi-region infrastructure

Potential capabilities:

- Regional failover.
- Lower latency.
- Data residency controls.

Required before implementation:

- Customer demand.
- Operational maturity.
- Backup and replication strategy.
- Data residency and privacy review.

## Future scope rules

- Do not implement future modules during MVP phases.
- Research and planning documents are allowed only when requested.
- Future modules must not complicate MVP architecture unless the abstraction is already required for MVP.
- Any future module that touches PII, communications, payments, or admin access must receive security review before coding.
- Every approved future module must have a decision log entry.
