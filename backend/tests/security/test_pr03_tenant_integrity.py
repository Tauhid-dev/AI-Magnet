import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.passwords import hash_password
from app.db.base import Base, utc_now
from app.models import (
    BusinessNotificationSetting,
    BusinessUser,
    Conversation,
    DocumentChunk,
    KnowledgeDocument,
    Lead,
    Message,
    NotificationDelivery,
)
from app.tenants.service import TenantService


def create_fk_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    return session_factory()


def expect_integrity_error(session, instance) -> None:
    session.add(instance)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_same_tenant_constraints_block_cross_tenant_parent_child_links():
    with create_fk_test_session() as session:
        tenant_service = TenantService(session)
        tenant_a = tenant_service.create_tenant("Tenant A", "tenant-a")
        tenant_b = tenant_service.create_tenant("Tenant B", "tenant-b")
        business_a = tenant_service.create_business(
            tenant_id=tenant_a.id,
            name="Tenant A Business",
        )
        document_a = KnowledgeDocument(
            tenant_id=tenant_a.id,
            filename="a.md",
            status="ingested",
        )
        conversation_a = Conversation(
            tenant_id=tenant_a.id,
            visitor_label="Tenant A visitor",
            status="open",
        )
        lead_a = Lead(
            tenant_id=tenant_a.id,
            conversation_id=None,
            customer_name="Private Person",
            status="qualified",
        )
        session.add_all([document_a, conversation_a, lead_a])
        session.commit()

        expect_integrity_error(
            session,
            BusinessUser(
                tenant_id=tenant_b.id,
                business_id=business_a.id,
                email="wrong-tenant@example.test",
                status="active",
                password_hash=hash_password("correct-password"),
                password_updated_at=utc_now(),
            ),
        )
        expect_integrity_error(
            session,
            DocumentChunk(
                tenant_id=tenant_b.id,
                document_id=document_a.id,
                chunk_index=0,
                content="Wrong tenant chunk",
                token_count=3,
                embedding=[0.0] * 1536,
            ),
        )
        expect_integrity_error(
            session,
            Message(
                tenant_id=tenant_b.id,
                conversation_id=conversation_a.id,
                sender_type="visitor",
                content="Wrong tenant message",
            ),
        )
        expect_integrity_error(
            session,
            Lead(
                tenant_id=tenant_b.id,
                conversation_id=conversation_a.id,
                customer_name="Wrong Tenant",
                status="new",
            ),
        )
        expect_integrity_error(
            session,
            BusinessNotificationSetting(
                tenant_id=tenant_b.id,
                business_id=business_a.id,
                notification_email="owner@example.test",
            ),
        )
        expect_integrity_error(
            session,
            NotificationDelivery(
                tenant_id=tenant_b.id,
                lead_id=lead_a.id,
                notification_type="lead_qualified",
                recipient_email="owner@example.test",
                subject="Lead",
                body_text="Lead body",
                status="queued",
            ),
        )
