# SMS and WhatsApp Premium Module Scope

## Status

Research and scoping only. No SMS, WhatsApp, messaging provider, webhook, or notification-channel code is implemented in Phase 10.

## Product intent

Messaging add-ons may help tradies follow up with leads quickly, confirm job details, and keep customers informed after the AI receptionist captures an enquiry.

The first release should focus on business-approved follow-up messages and lead notifications. Fully automated two-way customer conversations over SMS or WhatsApp should wait until consent, opt-out, moderation, and provider operations are ready.

## Candidate use cases

- Send the business an SMS when a high-priority qualified lead arrives.
- Send the customer a confirmation after they submit a chat enquiry.
- Send appointment reminders after a business user schedules follow-up in a future CRM workflow.
- Allow WhatsApp follow-up for tenants that explicitly enable it and complete provider setup.
- Record outbound message status in the tenant's lead timeline.

## Out of scope for first release

- Bulk promotional campaigns.
- Automated spam-like outreach.
- Cold SMS or WhatsApp messaging.
- Two-way AI negotiation without human approval.
- Emergency or safety-critical messaging.
- Cross-channel marketing automation.

## Provider options

Potential providers:

- Twilio for SMS and WhatsApp Business API access.
- MessageBird/Bird for multi-channel messaging.
- Vonage for SMS and WhatsApp messaging.
- Direct Meta WhatsApp Cloud API for WhatsApp only.

Provider choice should consider:

- Australian number support.
- WhatsApp Business onboarding effort.
- Message template review process.
- Delivery receipt support.
- Webhook reliability.
- Data processing terms.
- Cost per message and monthly number fees.

## Recommended architecture

Messaging should be provider-neutral:

- MessagingProvider protocol for send, delivery status, and provider metadata.
- Tenant messaging settings for enabled channels, sender IDs, and consent settings.
- Message delivery table with tenant_id, lead_id, channel, recipient hash or masked value, status, attempts, provider message ID, and error summary.
- Webhook receiver that maps provider events back to tenant-scoped deliveries.
- Entitlement checks before sending any premium-channel message.

Message sends should be deterministic business actions. LLM output should not directly decide to send customer messages.

## Consent and opt-out

SMS and WhatsApp require explicit consent planning before implementation.

Minimum rules:

- Capture the purpose for contacting the customer.
- Store consent source and timestamp where customer follow-up is enabled.
- Include opt-out wording where required.
- Stop sending to customers who opt out.
- Do not reuse a phone number for marketing unless marketing consent exists.
- Keep WhatsApp templates approved and purpose-specific.

## Data handling

Messaging data may include names, phone numbers, job details, suburbs, message content, and delivery metadata.

Rules:

- Store message records with `tenant_id`.
- Mask phone numbers in admin/support views where possible.
- Avoid logging message bodies and full phone numbers.
- Keep provider webhook payloads out of long-term logs.
- Do not expose one tenant's delivery events to another tenant.

## Delivery workflow

1. Tenant enables a messaging channel and accepts messaging terms.
2. Lead qualifies through chat, portal, or future voice flow.
3. Deterministic rules decide whether an internal business alert or customer confirmation is allowed.
4. Backend creates a tenant-scoped message delivery record.
5. Provider sends the message.
6. Provider webhook updates delivery status.
7. Portal shows delivery state and any opt-out state.

## Security risks

- Accidental messages to the wrong recipient.
- Cross-tenant webhook event mapping mistakes.
- Provider credentials leaked through logs or frontend code.
- Customer opt-out ignored.
- LLM-generated message content that overpromises business availability or pricing.

Required controls:

- Server-side tenant ownership checks.
- Provider credentials in environment variables or secret store only.
- Template or deterministic message copy for MVP.
- Delivery audit trail.
- Opt-out enforcement before send.

## Pricing model

Recommended packaging:

- Premium add-on with included monthly message volume.
- Separate SMS and WhatsApp entitlements.
- Overage or fair-use policy.
- Higher tier for two-way messaging when approved.

## Implementation gates

Do not implement messaging until:

- Messaging provider is selected.
- Consent and opt-out requirements are approved.
- Pricing model and usage metering are defined.
- Tenant entitlement model exists.
- Delivery log and webhook security design is reviewed.

## Suggested later phases

1. Messaging provider and consent decision.
2. Tenant messaging settings and entitlement checks.
3. Internal business SMS alerts.
4. Customer confirmation messages with opt-out.
5. Delivery receipt webhooks.
6. Optional WhatsApp Business template support.

## Acceptance checklist

- Provider options, consent, opt-out, and data handling are documented.
- No messaging provider code exists from Phase 10.
- Future implementation is constrained by tenant isolation and entitlement checks.
