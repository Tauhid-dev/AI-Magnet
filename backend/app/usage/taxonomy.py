"""Usage event taxonomy for tenant analytics."""

from __future__ import annotations


class UsageEventType:
    """Canonical tenant-scoped usage event names."""

    CONVERSATION_STARTED = "conversation_started"
    MESSAGE_RECEIVED = "message_received"
    ASSISTANT_RESPONSE_GENERATED = "assistant_response_generated"
    LEAD_QUALIFIED = "lead_qualified"
    LEAD_NOTIFICATION_QUEUED = "lead_notification_queued"
    LEAD_NOTIFICATION_SENT = "lead_notification_sent"
    DOCUMENT_INGESTED = "document_ingested"
    DOCUMENT_INGESTION_FAILED = "document_ingestion_failed"
    WIDGET_KEY_CREATED = "widget_key_created"
    WIDGET_KEY_ROTATED = "widget_key_rotated"
    WIDGET_KEY_DISABLED = "widget_key_disabled"
    WIDGET_KEY_REVOKED = "widget_key_revoked"
    WIDGET_ORIGINS_UPDATED = "widget_origins_updated"
    WIDGET_BRANDING_UPDATED = "widget_branding_updated"
    LEAD_STATUS_UPDATED = "lead_status_updated"
    BUSINESS_PROFILE_UPDATED = "business_profile_updated"
    AGENT_SANDBOX_TESTED = "agent_sandbox_tested"


class UsageEventSource:
    """Canonical usage event sources."""

    CHAT_WIDGET = "chat_widget"
    BUSINESS_PORTAL = "business_portal"
    RAG_INGESTION = "rag_ingestion"
    NOTIFICATION_WORKFLOW = "notification_workflow"


TENANT_USAGE_EVENTS = frozenset(
    {
        UsageEventType.CONVERSATION_STARTED,
        UsageEventType.MESSAGE_RECEIVED,
        UsageEventType.ASSISTANT_RESPONSE_GENERATED,
        UsageEventType.LEAD_QUALIFIED,
        UsageEventType.LEAD_NOTIFICATION_QUEUED,
        UsageEventType.LEAD_NOTIFICATION_SENT,
        UsageEventType.DOCUMENT_INGESTED,
        UsageEventType.DOCUMENT_INGESTION_FAILED,
        UsageEventType.WIDGET_KEY_CREATED,
        UsageEventType.WIDGET_KEY_ROTATED,
        UsageEventType.WIDGET_KEY_DISABLED,
        UsageEventType.WIDGET_KEY_REVOKED,
        UsageEventType.WIDGET_ORIGINS_UPDATED,
        UsageEventType.WIDGET_BRANDING_UPDATED,
        UsageEventType.LEAD_STATUS_UPDATED,
        UsageEventType.BUSINESS_PROFILE_UPDATED,
        UsageEventType.AGENT_SANDBOX_TESTED,
    }
)

ADMIN_USAGE_BACKED_BY_AUDIT_LOGS = frozenset(
    {
        "tenant_created",
        "tenant_detail_viewed",
        "tenant_status_updated",
        "tenant_support_context_viewed",
    }
)
