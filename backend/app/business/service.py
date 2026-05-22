"""Tenant-scoped business portal data service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.service import AnalyticsService, TenantAnalyticsSnapshot
from app.leads.workflow import LeadWorkflowService
from app.models.conversation import Conversation, Message
from app.models.knowledge import KnowledgeDocument
from app.models.lead import Lead
from app.models.usage import UsageLog
from app.models.widget import WidgetConfig


class BusinessPortalService:
    """Read tenant-owned portal data with explicit tenant context."""

    def __init__(self, session: Session, tenant_id: str) -> None:
        self.session = session
        self.tenant_id = tenant_id

    def list_documents(self) -> list[KnowledgeDocument]:
        statement = (
            select(KnowledgeDocument)
            .where(KnowledgeDocument.tenant_id == self.tenant_id)
            .order_by(KnowledgeDocument.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def list_leads(self) -> list[Lead]:
        statement = (
            select(Lead)
            .where(Lead.tenant_id == self.tenant_id)
            .order_by(Lead.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_lead(self, lead_id: str) -> Lead | None:
        statement = select(Lead).where(
            Lead.id == lead_id,
            Lead.tenant_id == self.tenant_id,
        )
        return self.session.scalars(statement).first()

    def update_lead_status(self, lead_id: str, status: str) -> Lead | None:
        lead = self.get_lead(lead_id)
        if lead is None:
            return None
        return LeadWorkflowService(self.session).update_business_status(lead, status)

    def list_conversations(self) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.tenant_id == self.tenant_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == self.tenant_id,
        )
        return self.session.scalars(statement).first()

    def list_messages(self, conversation_id: str) -> list[Message]:
        statement = (
            select(Message)
            .where(
                Message.tenant_id == self.tenant_id,
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at)
        )
        return list(self.session.scalars(statement))

    def active_widget(self) -> WidgetConfig | None:
        statement = (
            select(WidgetConfig)
            .where(
                WidgetConfig.tenant_id == self.tenant_id,
                WidgetConfig.status == "active",
            )
            .order_by(WidgetConfig.created_at.desc())
        )
        return self.session.scalars(statement).first()

    def analytics(self) -> TenantAnalyticsSnapshot:
        return AnalyticsService(self.session).tenant_snapshot(self.tenant_id)

    def recent_usage(self, limit: int = 10) -> list[UsageLog]:
        statement = (
            select(UsageLog)
            .where(UsageLog.tenant_id == self.tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))
