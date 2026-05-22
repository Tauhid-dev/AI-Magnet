import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.leads.workflow import LeadWorkflowService
from app.models import Lead
from app.tenants.service import TenantService


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    return session_factory()


def test_lead_workflow_qualifies_only_when_required_fields_are_present():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        lead = Lead(
            tenant_id=tenant.id,
            customer_name="Alex",
            customer_phone="0412 345 678",
            job_type="blocked drain",
            suburb="Bondi",
            urgency="today",
            status="new",
        )
        session.add(lead)

        result = LeadWorkflowService(session).evaluate_qualification(lead)

        assert result.missing_fields == []
        assert result.became_qualified is True
        assert lead.status == "qualified"
        assert lead.qualified_at is not None
        assert lead.notification_status == "not_queued"
        assert lead.qualification_reason == "Required lead fields captured."


def test_lead_workflow_keeps_incomplete_leads_out_of_notifications():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        lead = Lead(
            tenant_id=tenant.id,
            customer_name="Alex",
            customer_phone="0412 345 678",
            status="new",
        )
        session.add(lead)

        result = LeadWorkflowService(session).evaluate_qualification(lead)

        assert result.became_qualified is False
        assert result.missing_fields == ["job_type", "suburb", "urgency"]
        assert lead.status == "needs_info"
        assert "Missing required fields" in (lead.qualification_reason or "")


def test_business_managed_status_transitions_are_validated():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        lead = Lead(
            tenant_id=tenant.id,
            customer_name="Alex",
            customer_phone="0412 345 678",
            job_type="blocked drain",
            suburb="Bondi",
            urgency="today",
            status="qualified",
        )
        session.add(lead)
        workflow = LeadWorkflowService(session)

        workflow.update_business_status(lead, "contacted")
        assert lead.status == "contacted"

        workflow.update_business_status(lead, "closed")
        assert lead.status == "closed"
        with pytest.raises(ValueError, match="Cannot transition"):
            workflow.update_business_status(lead, "contacted")


def test_non_business_status_cannot_be_set_from_portal_workflow():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        lead = Lead(tenant_id=tenant.id, status="qualified")
        session.add(lead)

        with pytest.raises(ValueError, match="business-managed"):
            LeadWorkflowService(session).update_business_status(lead, "notified")
