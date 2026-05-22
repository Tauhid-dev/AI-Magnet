# Product Vision

## Product

AI Tradie Receptionist Platform for Australian local businesses and tradies.

## One-line vision

Give small trade businesses a reliable AI receptionist that answers website enquiries, captures qualified leads, and routes useful job details to the business without requiring the owner to manage a full CRM or call centre.

## Target customers

- Australian local businesses and tradies such as plumbers, electricians, landscapers, painters, cleaners, builders, roofers, mechanics, and similar service providers.
- Small teams where the owner or admin person handles customer enquiries manually.
- Businesses that already have a website or landing page but lose leads because they cannot answer every enquiry quickly.

## Core problem

Tradies often miss enquiries while on jobs, driving, quoting, or working after hours. Website visitors want fast answers about service areas, availability, job types, pricing guidance, and next steps. Generic chatbots are not enough because they do not understand each business, do not qualify leads consistently, and do not isolate customer data across businesses.

## Core solution

A hosted multi-tenant SaaS platform where each business receives:

- A business portal for managing profile, knowledge base, leads, conversations, and analytics.
- An embeddable website chat widget.
- Tenant-isolated customer conversations, documents, leads, and usage logs.
- RAG-backed AI answers using that business's uploaded knowledge base.
- Deterministic lead capture and qualification workflows.
- Email notifications when a qualified lead is captured.

The platform also includes a master admin portal for managing tenants, usage, support, subscriptions, operational health, and system configuration.

## Primary users

- Visitor: A potential customer using the website chat widget.
- Business user: Owner, admin, or receptionist for one business tenant.
- Super admin: Platform operator managing all tenants and system health.
- Support/admin operator: Future role for support workflows with restricted access.

## MVP promise

For the MVP, a business can be onboarded, upload knowledge documents, embed a chat widget, receive AI-assisted customer enquiries, capture and qualify leads, receive email notifications, and review basic usage and analytics.

## Non-goals for MVP

- Voice AI and AI phone calling.
- WhatsApp, SMS, and other messaging-channel automation.
- Stripe billing and subscription automation.
- Marketplace or app ecosystem.
- Mobile app.
- Advanced CRM.
- Multi-region infrastructure.

## Product principles

- Tenant isolation first: no business should be able to access another business's data.
- Practical over flashy: capture useful leads, notify the business, and keep setup simple.
- AI assists, deterministic logic decides: lead capture and routing should not depend only on free-form LLM judgement.
- Provider flexibility: use an OpenAI-compatible AI provider first, but keep model provider details behind an abstraction.
- Australian SMB fit: use plain language, local business workflows, and privacy-aware defaults.
- Keep the MVP narrow: build the smallest reliable path from website enquiry to qualified lead notification.

## Success indicators

- A tenant can go from setup to embedded widget without developer help after initial deployment.
- The AI only retrieves knowledge for the current tenant.
- Leads contain enough structured information for the business to follow up.
- Businesses receive timely email notifications for qualified leads.
- Super admins can see tenant health, usage, and support context.
- The system can run locally with Docker Compose for development.

## Strategic direction

The platform starts as a web chat and lead capture product. After the MVP is stable, it can expand into premium modules such as voice AI, SMS, WhatsApp, billing, advanced CRM integrations, self-hosted n8n automation, and local model support.
