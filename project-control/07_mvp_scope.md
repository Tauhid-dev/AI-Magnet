# MVP Scope

## MVP goal

Deliver the smallest reliable version of the AI Tradie Receptionist Platform that can onboard businesses, answer website visitor questions using tenant-specific knowledge, capture qualified leads, notify the business by email, and provide basic admin and analytics visibility.

## In scope

### Super admin portal

- Super admin login.
- Tenant/business creation and management.
- Tenant status visibility.
- Usage overview.
- Basic support context.
- System health indicators where available.

### Business portal

- Business login.
- Business profile/settings.
- Knowledge base document upload.
- Ingestion status.
- Lead list and lead detail.
- Conversation history.
- Widget install/configuration view.
- Basic analytics dashboard.

### Tenant/business management

- Multi-tenant data model.
- Tenant-scoped users.
- Tenant-owned documents, conversations, leads, usage logs, and audit logs.
- Super admin ability to manage tenants.

### Embeddable chat widget

- Website-embeddable script or widget bundle.
- Tenant-aware initialization.
- Chat UI.
- Message send/receive.
- Lead capture prompts.

### RAG document upload and ingestion

- Upload business knowledge documents.
- Extract text.
- Chunk content.
- Generate embeddings.
- Store vectors in PostgreSQL with pgvector.
- Track ingestion status.

### Business-specific knowledge base

- Tenant-scoped knowledge storage.
- Tenant-scoped retrieval.
- No cross-tenant retrieval.

### Chat conversation handling

- Conversation start/resume.
- Message storage.
- RAG-backed answer generation.
- AI provider abstraction.
- Safe fallback responses when knowledge is missing.

### Lead capture

- Capture visitor name, contact details, job type, suburb/location, urgency, and notes where available.
- Use deterministic workflow logic for qualification.
- Store leads with tenant context.

### Lead qualification

- Define simple qualification states such as new, needs_more_info, qualified, contacted, closed, and spam where appropriate.
- Avoid relying only on LLM free-form classification.

### Email notification

- Notify business when a qualified lead is captured.
- Use SMTP provider abstraction.
- Log delivery attempts and failures.

### Usage logging

- Track widget loads, conversations, messages, AI calls, document ingestion, leads, and notification attempts.
- Include `tenant_id` for tenant-scoped events.

### Basic analytics dashboard

- Conversation count.
- Lead count.
- Lead conversion/qualification count.
- Recent activity.
- Document ingestion status.
- Basic AI usage where available.

### Docker-based local/dev deployment

- Docker Compose development environment.
- PostgreSQL with pgvector.
- Redis.
- Backend.
- Frontend.
- Worker.
- Nginx where useful.

## Out of scope for MVP

- Voice AI.
- WhatsApp.
- SMS.
- Stripe billing.
- Full marketplace.
- Mobile app.
- Advanced CRM.
- AI phone calling.
- Multi-region infrastructure.
- Complex automation with n8n.
- Advanced sales pipeline management.
- Native calendar booking unless explicitly approved later.

## MVP quality bar

- Tenant isolation must be tested.
- RAG retrieval must be tenant-scoped.
- Admin access must be restricted.
- No secrets committed.
- Local development setup must be documented.
- The system should be simple enough for future sessions to extend without heavy refactoring.

## MVP release candidate checklist

- Business can be onboarded by super admin.
- Business can upload knowledge documents.
- Widget can be embedded for that business.
- Visitor can chat with tenant-specific AI receptionist.
- Lead can be captured and qualified.
- Business receives email notification for qualified lead.
- Business can review leads and conversations.
- Super admin can review tenants and usage.
- Tests and lint/type checks pass where configured.
- Known issues are logged.
