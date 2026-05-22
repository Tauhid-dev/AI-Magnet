# Security and Privacy Rules

## Security posture

This product handles customer enquiries, business documents, contact details, and AI-generated responses for Australian small businesses. The MVP must treat tenant isolation, consent, data minimization, and access control as core product requirements rather than optional hardening.

## Tenant isolation

- Tenant-owned records must include `tenant_id` where tenant isolation applies.
- Application services must require tenant context before reading or writing tenant data.
- RAG retrieval must never search or return another tenant's document chunks.
- Business portal users must only access their own tenant.
- Widget requests must resolve to exactly one tenant through a safe public widget key or equivalent mechanism.
- Super admin access must be role-protected and audit-logged.

## No cross-tenant retrieval

- Vector search must be scoped to the active tenant.
- Retrieval tests must include at least two tenants with similar content to confirm no leakage.
- Cached RAG results must include tenant context in cache keys.
- Background ingestion jobs must write chunks and embeddings with the correct `tenant_id`.

## Customer consent and AI transparency

- The chat widget should clearly indicate that the visitor is interacting with an AI assistant or automated chat.
- Collection of contact details should be linked to an enquiry or follow-up purpose.
- Future voice, SMS, and WhatsApp modules must include explicit consent and opt-out planning before implementation.

## PII handling

Potential PII includes:

- Visitor name.
- Phone number.
- Email address.
- Address or suburb.
- Job details.
- Conversation history.
- Uploaded business documents that contain personal data.

Rules:

- Collect only what is needed for the enquiry and business follow-up.
- Avoid logging raw PII in application logs.
- Avoid sending unnecessary PII to AI providers.
- Mask or limit PII in admin/support views where full details are not needed.
- Restrict PII access by role.

## Data retention

- Use minimal data retention suitable for the MVP.
- Define retention periods before production launch.
- Support deletion or export planning for tenant data in a future operational phase.
- Do not retain failed uploads, temporary extraction files, or debug payloads longer than needed.

## Document privacy

- Raw documents uploaded by one tenant must not be exposed to another tenant.
- Extracted text and chunks must be tenant-scoped.
- Document download or preview features must require tenant permission.
- Admin access to documents should be limited, justified, and audit-logged.

## Audit logs

Audit logs should record security-relevant actions such as:

- Super admin login.
- Tenant creation, suspension, or deletion.
- Admin access to tenant records.
- Business user management.
- API key/widget key rotation.
- Document deletion.
- Major settings changes.

Audit records should include:

- Actor identity where known.
- Tenant ID if applicable.
- Action.
- Timestamp.
- Target resource type and ID where safe.
- Request context where useful, without storing secrets.

## Admin access control

- Super admin routes must be separate from business-user routes.
- Admin privileges must never be inferred from tenant membership alone.
- Support access should be least-privilege if introduced later.
- Admin actions that affect tenants should be logged.
- Dangerous admin actions should require confirmation in the UI when implemented.

## Secrets and environment handling

- Do not hardcode API keys, passwords, tokens, SMTP credentials, or database credentials.
- Use environment variables and excluded local `.env` files.
- Commit only safe examples such as `.env.example`.
- Do not log secrets.
- Rotate secrets if accidental exposure is suspected.

## AI provider privacy

- AI provider requests should send only the minimum necessary conversation and tenant knowledge context.
- Prompts must not include unrelated tenant data.
- Provider configuration should allow changing endpoints and providers without rewriting business logic.
- Future local model/Ollama support may reduce external data exposure but still requires tenant isolation.

## Australian privacy considerations

The platform should be designed with future Australian Privacy Act obligations in mind, including:

- Clear purpose for collecting customer data.
- Reasonable steps to protect personal information.
- Minimal collection and retention.
- Ability to explain how customer enquiries are handled.
- Future support for data access, correction, deletion, and breach response workflows.

This file is not legal advice. Before production launch, privacy policy, terms, data retention, and incident response processes should be reviewed by qualified legal and security professionals.

## Security validation before MVP launch

- Tenant isolation tests pass.
- Admin authorization tests pass.
- RAG cross-tenant retrieval tests pass.
- No real secrets are committed.
- Logs do not expose secrets.
- Widget key behavior is reviewed.
- Basic rate limiting or abuse mitigation is planned.
- Deployment environment has backups and secure secret handling.
