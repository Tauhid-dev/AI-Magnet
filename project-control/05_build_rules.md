# Build Rules

## Scope discipline

- Do not implement future-scope features early.
- Do not create application code during planning-only instructions.
- Keep MVP simple and focused on chat, RAG, lead capture, notifications, tenant management, business portal, super admin portal, analytics, and Docker-based local/dev deployment.
- Do not add Voice AI, WhatsApp, SMS, Stripe billing, marketplace, mobile app, advanced CRM, AI phone calling, or multi-region infrastructure unless explicitly instructed in a future phase.

## Git and phase workflow

- Start from latest `master` before each implementation instruction.
- Create a feature branch for each instruction or phase.
- Keep changes scoped to the requested task.
- Do not delete or overwrite existing files unless explicitly instructed.
- Every phase must update `09_phase_execution_log.md`.
- Every major design decision must update `10_decisions_log.md`.
- Before completing a phase, run available tests, lint checks, and type checks if the repo has them.
- After completing a phase, provide a git diff summary.

## Multi-tenant data rules

- Every table must include `tenant_id` where tenant isolation applies.
- No customer data should be shared across tenants.
- All tenant-scoped queries must require a tenant context.
- RAG retrieval must only retrieve data for the current tenant.
- Admin access to tenant data must be permission-checked and audit-logged.
- Tests should include cross-tenant denial cases for every sensitive data path.

## AI and RAG rules

- Use a provider abstraction for AI APIs.
- Initial AI provider should support an OpenAI-compatible API.
- Future local model/Ollama support must remain possible through the abstraction.
- Do not hardcode API keys.
- API keys, model names, endpoints, and provider settings must come from environment variables or safe configuration.
- LLM output should not directly perform unsafe actions.
- Prefer deterministic business logic for lead capture, qualification, and notification decisions.
- RAG prompts must not expose raw hidden instructions or unrelated tenant data.
- RAG retrieval must filter by `tenant_id` before or during vector search.

## Secret and configuration rules

- Use environment variables for secrets and deployment-specific configuration.
- Do not commit `.env` files containing real secrets.
- Provide `.env.example` with placeholder values when configuration is introduced.
- Keep local, staging, and production settings separate.
- Avoid logging secrets, API keys, passwords, tokens, or full customer PII.

## Backend rules

- Use FastAPI and Python unless a future decision explicitly changes this.
- Keep service logic testable outside HTTP route handlers.
- Validate inputs with typed schemas.
- Return safe error messages to clients.
- Use background jobs for slow ingestion and notification work.
- Keep provider integrations behind interfaces.

## Frontend rules

- Use Next.js, TypeScript, and TailwindCSS unless a future decision explicitly changes this.
- Keep business portal and admin portal authorization boundaries clear.
- Do not expose private tenant identifiers or secrets in browser code.
- The widget may use a public widget key, but not a private API key.
- Widget code must be lightweight and safe to embed on customer websites.

## Database rules

- Use PostgreSQL as the source of truth.
- Use pgvector for vector search.
- Use migrations for schema changes.
- Add indexes for tenant-scoped lookup paths.
- Prefer database constraints for critical integrity rules where practical.
- Avoid raw SQL string building for user-controlled input.

## Worker and queue rules

- Use Redis for queue/cache needs.
- Use a Python worker approach suitable for MVP: Celery, RQ, or a simple async worker.
- Document the worker choice in `10_decisions_log.md`.
- Ingestion and notifications should be retryable where practical.
- Failed jobs must be visible in logs or admin/support views.

## Deployment rules

- Use Docker Compose for local/dev deployment.
- Use Nginx for reverse proxying where needed.
- Target OCI VPS for initial deployment.
- Document environment variables and operational startup steps.
- Do not treat local development settings as production-safe defaults.

## Testing and validation rules

- Add tests in proportion to risk and blast radius.
- Tenant isolation, auth, RAG retrieval, admin access, and notification privacy require explicit tests.
- Use mocked AI and email providers for automated tests.
- Before completing a phase, run the tests/checks available in the repo.
- If tests cannot be run, explain why and record the gap.

## Documentation rules

- Keep `project-control` files aligned with implementation reality.
- Record major architecture, tooling, and product decisions.
- Keep setup and deployment documentation practical and command-oriented.
- Do not let future-scope notes become accidental implementation requirements.
