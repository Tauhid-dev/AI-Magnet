# Voice AI Premium Module Scope

## Status

Research and scoping only. No voice calling, telephony provider, speech-to-text, text-to-speech, or AI phone agent code is implemented in Phase 10.

## Product intent

Voice AI may become a premium module for tradies who miss calls while on tools, driving, or visiting job sites. The module should answer inbound calls, capture job details, qualify the enquiry, and hand off a clear lead summary to the business.

The first commercial version should focus on inbound call answering only. Outbound AI phone calling should remain out of scope until consent, compliance, reliability, and brand-risk questions are resolved.

## Candidate use cases

- Answer missed inbound calls after hours or when the business is unavailable.
- Ask deterministic lead qualification questions for trade type, suburb, urgency, contact details, and job description.
- Escalate urgent jobs or unsafe scenarios to the business by email or future messaging channels.
- Summarize the call into the same tenant-scoped lead workflow used by chat.
- Provide transcript and call summary access inside the business portal.

## Out of scope for first release

- AI outbound cold calling.
- Emergency dispatch or safety-critical decision-making.
- Payment collection by phone.
- Deep CRM automation without human review.
- Voice cloning or impersonation.
- Call recording without clear consent.

## Recommended architecture

Voice should be added behind provider abstractions instead of binding the product to one telephony stack.

Suggested service boundaries:

- Telephony adapter: provider webhooks, call lifecycle events, recordings, and phone numbers.
- Speech adapter: speech-to-text and text-to-speech provider contracts.
- Voice session service: turn handling, call state, interruption handling, and timeout handling.
- Lead handoff service: deterministic conversion from call transcript to tenant-scoped lead fields.
- Consent service: greeting, recording notice, and region-specific consent settings.

Voice data should reuse existing tenant boundaries:

- Every call, transcript, summary, recording pointer, and generated lead must include `tenant_id`.
- Voice retrieval must use only the tenant's knowledge base.
- Public phone numbers must resolve server-side to exactly one active tenant.

## Data flow

1. Visitor calls a tenant-owned phone number.
2. Telephony provider sends an inbound call webhook.
3. Backend resolves the phone number to one tenant.
4. Voice session starts with consent and AI transparency wording.
5. Speech-to-text turns caller audio into text.
6. AI answer generation uses tenant-scoped RAG context and safe prompts.
7. Deterministic lead rules extract and validate lead fields.
8. Lead is stored under the tenant and notification workflow is triggered.
9. Transcript, summary, and usage events are available in the portal.

## Privacy and consent

Voice has higher privacy risk than chat. The module should not ship until the following are documented and approved:

- Caller notice that the call is handled by an AI assistant.
- Recording notice where recording is enabled.
- Clear purpose for collecting name, phone number, address/suburb, and job details.
- Retention period for recordings and transcripts.
- Tenant controls for recording on/off.
- Admin views that avoid exposing full transcripts unless needed.
- Provider data processing terms reviewed for Australian SMB use.

## Reliability requirements

Voice feels broken faster than chat when latency or interruptions are poor. A pilot should define:

- Maximum acceptable response latency.
- Fallback when AI provider, speech provider, or telephony provider fails.
- Business fallback phone number or voicemail handoff.
- Call timeout rules.
- Repeat and clarification behavior.
- Monitoring for failed calls and abandoned sessions.

## Cost model

Voice has multiple variable costs:

- Phone number rental.
- Per-minute telephony.
- Speech-to-text.
- Text-to-speech.
- LLM tokens.
- Storage for transcripts or recordings.

Recommended packaging:

- Charge as a premium add-on with included monthly minutes.
- Bill overage by minute or usage tier.
- Keep outbound calling, if ever approved, as a separate add-on.

## Security risks

- Callers may disclose sensitive personal information.
- Prompt injection can happen through spoken content.
- Fraudsters may try to extract tenant information.
- Recordings and transcripts are high-value PII.
- Phone number routing mistakes can cause cross-tenant leakage.

Required controls:

- Tenant-scoped phone number ownership table.
- Tenant-filtered RAG retrieval before answer generation.
- Minimal transcript exposure in admin/support views.
- Audit logs for transcript or recording access.
- Feature flag and tenant entitlement checks.

## Implementation gates

Do not implement voice until:

- MVP chat, lead, notification, and portal workflows are stable in production.
- A telephony provider is selected.
- Consent copy and recording policy are approved.
- Data retention policy is approved.
- Pricing and usage metering are defined.
- A pilot tenant agrees to a constrained beta.

## Suggested later phases

1. Provider selection and consent design.
2. Tenant phone number mapping and webhook receiver.
3. Inbound call session prototype behind feature flag.
4. Transcript and summary storage with strict tenant access.
5. Lead handoff and notification integration.
6. Pilot monitoring, cost tracking, and reliability review.

## Acceptance checklist

- Scope, risks, costs, and data flow are documented.
- No voice production code exists from Phase 10.
- Tenant isolation and consent requirements are explicit.
- Outbound AI calling remains deferred.
