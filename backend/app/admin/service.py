"""Super admin data access services."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.knowledge import KnowledgeDocument
from app.models.lead import Lead
from app.models.tenant import Business, BusinessUser, Tenant
from app.models.usage import AuditLog, UsageLog


@dataclass(frozen=True)
class TenantMetrics:
    """Compact tenant metrics for admin views."""

    businesses_total: int
    users_total: int
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int


@dataclass(frozen=True)
class UsageOverview:
    """Platform-wide usage totals."""

    tenants_total: int
    active_tenants: int
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int


class AdminService:
    """Read and manage platform data through super admin workflows."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_tenants(self) -> list[Tenant]:
        statement = select(Tenant).order_by(Tenant.created_at.desc())
        return list(self.session.scalars(statement))

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self.session.get(Tenant, tenant_id)

    def create_tenant(
        self,
        *,
        name: str,
        slug: str,
        status: str = "active",
        business_name: str | None = None,
        business_email: str | None = None,
        owner_email: str | None = None,
    ) -> Tenant:
        tenant = Tenant(name=name, slug=slug, status=status)
        self.session.add(tenant)
        self.session.flush()
        business = Business(
            tenant_id=tenant.id,
            name=business_name or name,
            email=business_email,
        )
        self.session.add(business)
        self.session.flush()
        if owner_email:
            self.session.add(
                BusinessUser(
                    tenant_id=tenant.id,
                    business_id=business.id,
                    email=owner_email,
                    full_name=f"{name} Owner",
                    role="owner",
                    status="active",
                )
            )
            self.session.flush()
        return tenant

    def update_tenant_status(self, tenant_id: str, status: str) -> Tenant | None:
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            return None
        tenant.status = status
        self.session.flush()
        return tenant

    def list_businesses(self, tenant_id: str) -> list[Business]:
        statement = (
            select(Business)
            .where(Business.tenant_id == tenant_id)
            .order_by(Business.created_at)
        )
        return list(self.session.scalars(statement))

    def list_business_users(self, tenant_id: str) -> list[BusinessUser]:
        statement = (
            select(BusinessUser)
            .where(BusinessUser.tenant_id == tenant_id)
            .order_by(BusinessUser.created_at)
        )
        return list(self.session.scalars(statement))

    def tenant_metrics(self, tenant_id: str) -> TenantMetrics:
        return TenantMetrics(
            businesses_total=self._tenant_count(Business, tenant_id),
            users_total=self._tenant_count(BusinessUser, tenant_id),
            documents_total=self._tenant_count(KnowledgeDocument, tenant_id),
            leads_total=self._tenant_count(Lead, tenant_id),
            conversations_total=self._tenant_count(Conversation, tenant_id),
            messages_total=self._tenant_count(Message, tenant_id),
            usage_events_total=self._tenant_count(UsageLog, tenant_id),
        )

    def usage_overview(self) -> UsageOverview:
        return UsageOverview(
            tenants_total=self._count(Tenant),
            active_tenants=self._count(Tenant, Tenant.status == "active"),
            documents_total=self._count(KnowledgeDocument),
            leads_total=self._count(Lead),
            conversations_total=self._count(Conversation),
            messages_total=self._count(Message),
            usage_events_total=self._count(UsageLog),
        )

    def recent_leads(self, tenant_id: str, limit: int = 10) -> list[Lead]:
        statement = (
            select(Lead)
            .where(Lead.tenant_id == tenant_id)
            .order_by(Lead.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_conversations(self, tenant_id: str, limit: int = 10) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.tenant_id == tenant_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_usage(self, tenant_id: str, limit: int = 10) -> list[UsageLog]:
        statement = (
            select(UsageLog)
            .where(UsageLog.tenant_id == tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_audit_logs(self, limit: int = 25) -> list[AuditLog]:
        statement = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.session.scalars(statement))

    def message_count(self, conversation_id: str, tenant_id: str) -> int:
        statement = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id,
        )
        return int(self.session.scalar(statement) or 0)

    def _count(self, model: type, *criteria) -> int:
        statement = select(func.count()).select_from(model)
        if criteria:
            statement = statement.where(*criteria)
        return int(self.session.scalar(statement) or 0)

    def _tenant_count(self, model: type, tenant_id: str) -> int:
        statement = select(func.count()).select_from(model).where(model.tenant_id == tenant_id)
        return int(self.session.scalar(statement) or 0)
