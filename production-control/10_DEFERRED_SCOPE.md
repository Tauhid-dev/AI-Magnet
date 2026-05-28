# Deferred And Conditional Scope

Last updated: 2026-05-28

## Deferred Unless Separately Requested

- Voice AI.
- SMS and WhatsApp.
- Marketplace.
- Mobile app.
- Advanced CRM.
- AI phone calling.
- Enterprise/multi-region infrastructure.
- n8n runtime.
- Local Ollama provider runtime.
- Full public marketplace.

These features must not be implemented during PR-00 through PR-12 unless the user explicitly changes scope.

## Conditional, Not Mandatory Launch Blockers

| Item | Classification | Rule |
|---|---|---|
| Browser/Playwright crawling | Conditional | Implement only if ordinary crawler cannot support required customer sites. |
| Streaming chat | Conditional UX enhancement | Implement only if chosen for beta or needed by UX acceptance criteria. |
| Public SEO/marketing pages | Growth-track work | Not a production-security blocker; can be scheduled separately. |

## Notes

Billing and entitlements are not deferred for paid beta. PR-11 must provide either a real billing integration or a deliberate manual paid-beta entitlement process with enforceable controls.
