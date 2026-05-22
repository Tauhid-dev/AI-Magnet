# Embeddable Chat Widget

Phase 4 adds a lightweight browser widget that talks to the backend chat API.

Use it on a test page with:

```html
<script
  src="./chat-widget.js"
  data-api-base-url="http://127.0.0.1:8000"
  data-widget-key="wm_live_replace_with_tenant_widget_key"
  data-title="Ask our AI receptionist"
></script>
```

The widget key is public and resolves to one tenant on the backend. It must not
be used as a private API key. Revoked or unknown widget keys are rejected by the
backend before a conversation can start.
