# Automation, CRM, Local Model, and Multi-Region Scope

## Status

Research and scoping only. No n8n workflow execution, CRM integration, local model runtime, Ollama deployment, or multi-region infrastructure code is implemented in Phase 10.

## Product intent

This module group covers advanced capabilities that may become premium or enterprise offerings after the core AI receptionist MVP proves stable:

- Self-hosted n8n automation for follow-up workflows.
- CRM integrations for job and lead handoff.
- Local model or Ollama support for privacy-sensitive deployments.
- Multi-region architecture for larger scale or data residency needs.

These capabilities should be treated as separate tracks, even if they share integration and provider-abstraction patterns.

## n8n automation

### Candidate use cases

- Send qualified leads to external systems.
- Trigger tenant-specific follow-up workflows.
- Create calendar tasks or internal notifications.
- Route urgent leads differently from non-urgent leads.

### Recommended boundary

n8n should not become the source of truth for tenant data. The platform should emit safe, tenant-scoped events or webhooks and keep canonical lead, conversation, and usage records in PostgreSQL.

### Security requirements

- Tenant-specific workflow configuration.
- Server-side entitlement checks.
- Signed outbound webhooks.
- No secrets stored in browser code.
- Audit logs for workflow creation, update, and execution failures.
- PII minimization in automation payloads.

## CRM integrations

### Candidate integrations

- ServiceM8.
- Tradify.
- HubSpot.
- Zoho CRM.
- Jobber or similar field-service systems.

### Recommended first scope

Start with one integration chosen from actual customer demand. The first version should create or update leads/jobs from qualified tenant-scoped leads, not attempt full bidirectional CRM sync.

### Data flow

1. Tenant enables one CRM integration.
2. Tenant authorizes provider access through a secure OAuth or API-key flow.
3. Qualified lead triggers an integration job.
4. Integration service maps safe lead fields to provider fields.
5. Result is recorded in a tenant-scoped integration delivery log.

### Risks

- Provider tokens are sensitive secrets.
- External systems may not support clean tenant deletion or retention behavior.
- Field mapping errors can leak wrong details or create duplicate jobs.
- Bidirectional sync can overwrite business data unexpectedly.

## Local model and Ollama support

### Candidate use cases

- Privacy-sensitive tenants that prefer local inference.
- Lower-cost testing environments.
- Private deployments where external AI provider use is restricted.
- Resilience when external provider access is unavailable.

### Recommended architecture

The existing AI provider abstraction should remain the integration point. A future local provider should implement the same embedding and chat-completion protocols as the OpenAI-compatible provider.

Potential modes:

- Local chat model only, while embeddings remain provider-backed.
- Local embeddings and local chat.
- Tenant-specific provider configuration for enterprise/private deployments.

### Operational considerations

- Local models require CPU/GPU planning.
- Model quality and latency may vary heavily.
- Embedding dimensions must match the database vector schema or require migration.
- Prompt safety and tenant filtering still apply.
- Model downloads and updates need operational controls.

## Multi-region architecture

### When to consider

Do not start multi-region work for the MVP. Consider it only when one or more are true:

- Customer contracts require a specific region.
- Uptime requirements exceed single-host design.
- Usage volume outgrows one region.
- Disaster recovery needs justify added complexity.

### Candidate future shape

- Region-aware application deployments.
- Managed PostgreSQL or replicated database strategy.
- Object storage for documents and artifacts.
- Central control plane for tenants, billing, and routing.
- Clear data residency policy.

### Risks

- Cross-region tenant routing mistakes.
- Increased operational cost.
- More complex backups and restores.
- Harder debugging and incident response.
- RAG/vector data consistency problems.

## Shared implementation principles

- Keep each capability behind feature flags or tenant entitlements.
- Use provider abstractions for external systems.
- Use background jobs for slow or unreliable external calls.
- Store integration state with `tenant_id`.
- Avoid sending unnecessary conversation history or document content to third parties.
- Keep LLM output advisory; deterministic services should decide actions.
- Audit admin/support access to integration configuration and execution logs.

## Recommended packaging

- Automation add-on: n8n or webhook workflows.
- CRM add-on: priced per enabled integration or higher plan.
- Private AI add-on: enterprise/private deployment pricing.
- Multi-region: enterprise-only architecture, not self-serve.

## Implementation gates

Do not implement these tracks until:

- Customer demand identifies the first integration or deployment model.
- Entitlement and billing rules exist.
- Secrets storage and rotation model is approved.
- Data-flow review is complete.
- Background worker queue decision is made.
- Support and failure handling process is documented.

## Suggested later phases

1. Choose one customer-validated track.
2. Design entitlement and configuration model.
3. Add provider abstraction and tenant-scoped config.
4. Add background delivery jobs and delivery logs.
5. Add portal/admin management screens.
6. Add security, tenant isolation, and failure-mode tests.

## Acceptance checklist

- Operational cost, deployment complexity, and security boundaries are documented.
- No automation, CRM, local model, or multi-region implementation exists from Phase 10.
- Future work is constrained by provider abstractions, tenant scoping, and explicit entitlement checks.
