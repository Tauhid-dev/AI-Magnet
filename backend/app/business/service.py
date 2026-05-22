"""Tenant-scoped business portal data service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.leads.workflow import LeadWorkflowService
from app.models.conversation import Conversation, Message
from app.models.knowledge import KnowledgeDocument
from app.models.lead import Lead
from app.models.usage import UsageLog
from app.models.widget import WidgetConfig


@dataclass(frozen=True)
class PortalAnalytics:
    """Compact tenant analytics for the business portal."""

    documents_total: int
    documents_ingested: int
    leads_total: int
    conversations_total: int
    open_conversations: int
    messages_total: int
    widget_status: str


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

    def analytics(self) -> PortalAnalytics:
        documents_total = self._count(KnowledgeDocument)
        documents_ingested = self._count(
            KnowledgeDocument,
            KnowledgeDocument.status == "ingested",
        )
        leads_total = self._count(Lead)
        conversations_total = self._count(Conversation)
        open_conversations = self._count(Conversation, Conversation.status == "open")
        messages_total = self._count(Message)
        widget = self.active_widget()
        return PortalAnalytics(
            documents_total=documents_total,
            documents_ingested=documents_ingested,
            leads_total=leads_total,
            conversations_total=conversations_total,
            open_conversations=open_conversations,
            messages_total=messages_total,
            widget_status=widget.status if widget else "not_configured",
        )

    def recent_usage(self, limit: int = 10) -> list[UsageLog]:
        statement = (
            select(UsageLog)
            .where(UsageLog.tenant_id == self.tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def _count(self, model: type, *criteria) -> int:
        statement = select(func.count()).select_from(model).where(model.tenant_id == self.tenant_id)
        if criteria:
            statement = statement.where(*criteria)
        return int(self.session.scalar(statement) or 0)
