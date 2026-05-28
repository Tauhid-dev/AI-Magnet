from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.chat import (
    get_chat_completion_provider_dependency,
    get_embedding_provider_dependency,
)
from app.db.base import Base
from app.db.session import get_db_session
from app.models import Lead, Message, UsageLog
from app.providers.ai.base import ChatMessage
from app.providers.ai.deterministic import DeterministicEmbeddingProvider
from app.rag.ingestion import RagIngestionService
from app.tenants.service import TenantService
from app.widget.service import WidgetService
from app.main import create_app
from app.core.config import Settings, get_settings
from app.core.rate_limit import rate_limiter
from fastapi.testclient import TestClient


class RecordingChatProvider:
    def __init__(self) -> None:
        self.messages: list[ChatMessage] = []

    def complete(self, messages: list[ChatMessage]) -> str:
        self.messages = messages
        return "Mocked tenant answer"


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


def create_client(session, embedding_provider, chat_provider):
    rate_limiter.reset()
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_embedding_provider_dependency] = lambda: embedding_provider
    app.dependency_overrides[get_chat_completion_provider_dependency] = lambda: chat_provider
    return TestClient(app)


def seed_tenant_with_widget(session, name: str, slug: str, widget_key: str):
    tenant = TenantService(session).create_tenant(name, slug)
    widget = WidgetService(session).create_widget_config(
        tenant_id=tenant.id,
        widget_key=widget_key,
        name=f"{name} widget",
    )
    return tenant, widget


def seed_tenant_with_origin_widget(
    session,
    name: str,
    slug: str,
    widget_key: str,
    allowed_origins: list[str],
):
    tenant = TenantService(session).create_tenant(name, slug)
    widget = WidgetService(session).create_widget_config(
        tenant_id=tenant.id,
        widget_key=widget_key,
        name=f"{name} widget",
        allowed_origins=allowed_origins,
    )
    return tenant, widget


def ingest_knowledge(session, tenant_id: str, text: bytes, embedding_provider):
    settings = Settings(
        ai_provider="test",
        ai_embedding_dimensions=16,
        rag_chunk_size=20,
        rag_chunk_overlap=0,
    )
    return RagIngestionService(
        session=session,
        embedding_provider=embedding_provider,
        settings=settings,
    ).ingest_bytes(
        tenant_id=tenant_id,
        filename="services.md",
        content=text,
        content_type="text/markdown",
    )


def test_widget_init_accepts_active_key_without_exposing_tenant_id():
    with create_test_session() as session:
        widget_key = "wm_live_test_widget_a"
        seed_tenant_with_widget(session, "Tenant A Plumbing", "tenant-a", widget_key)
        session.commit()
        client = create_client(
            session,
            DeterministicEmbeddingProvider(16),
            RecordingChatProvider(),
        )

        response = client.post("/widget/init", json={"widget_key": widget_key})

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "active"
        assert payload["widget_name"] == "Tenant A Plumbing widget"
        assert "tenant_id" not in payload


def test_widget_init_rejects_revoked_key():
    with create_test_session() as session:
        widget_key = "wm_live_test_widget_a"
        tenant, widget = seed_tenant_with_widget(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            widget_key,
        )
        WidgetService(session).revoke_widget(widget.id, tenant.id)
        session.commit()
        client = create_client(
            session,
            DeterministicEmbeddingProvider(16),
            RecordingChatProvider(),
        )

        response = client.post("/widget/init", json={"widget_key": widget_key})

        assert response.status_code == 401


def test_widget_init_enforces_allowed_origin():
    with create_test_session() as session:
        widget_key = "wm_live_origin_widget_a"
        seed_tenant_with_origin_widget(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            widget_key,
            ["https://allowed.example"],
        )
        session.commit()
        client = create_client(
            session,
            DeterministicEmbeddingProvider(16),
            RecordingChatProvider(),
        )

        allowed_response = client.post(
            "/widget/init",
            json={"widget_key": widget_key, "origin": "https://allowed.example"},
        )
        missing_origin_response = client.post(
            "/widget/init",
            json={"widget_key": widget_key},
        )
        wrong_origin_response = client.post(
            "/widget/init",
            json={"widget_key": widget_key, "origin": "https://evil.example"},
        )

        assert allowed_response.status_code == 200
        assert missing_origin_response.status_code == 401
        assert wrong_origin_response.status_code == 401


def test_widget_init_rate_limit_blocks_repeated_requests(monkeypatch):
    with create_test_session() as session:
        widget_key = "wm_live_rate_widget_a"
        seed_tenant_with_widget(session, "Tenant A Plumbing", "tenant-a", widget_key)
        session.commit()
        monkeypatch.setenv("RATE_LIMIT_WIDGET_INIT_PER_MINUTE", "1")
        client = create_client(
            session,
            DeterministicEmbeddingProvider(16),
            RecordingChatProvider(),
        )

        first_response = client.post("/widget/init", json={"widget_key": widget_key})
        limited_response = client.post("/widget/init", json={"widget_key": widget_key})

        assert first_response.status_code == 200
        assert limited_response.status_code == 429


def test_conversation_message_uses_only_current_tenant_rag_context_and_captures_lead():
    with create_test_session() as session:
        widget_key = "wm_live_test_widget_a"
        tenant_a, _widget_a = seed_tenant_with_widget(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            widget_key,
        )
        tenant_b, _widget_b = seed_tenant_with_widget(
            session,
            "Tenant B Electrical",
            "tenant-b",
            "wm_live_test_widget_b",
        )
        embedding_provider = DeterministicEmbeddingProvider(16)
        ingest_knowledge(
            session,
            tenant_a.id,
            b"Tenant A handles blocked drains and hot water repairs in Bondi.",
            embedding_provider,
        )
        ingest_knowledge(
            session,
            tenant_b.id,
            b"Tenant B handles switchboard upgrades and lighting in Perth.",
            embedding_provider,
        )
        session.commit()
        chat_provider = RecordingChatProvider()
        client = create_client(session, embedding_provider, chat_provider)

        start_response = client.post(
            "/chat/conversations",
            json={"widget_key": widget_key, "visitor_label": "Website visitor"},
        )
        conversation_id = start_response.json()["conversation_id"]
        message_response = client.post(
            f"/chat/conversations/{conversation_id}/messages",
            json={
                "widget_key": widget_key,
                "message": (
                    "My name is Alex, phone 0412 345 678. "
                    "I have a blocked drain in Bondi today."
                ),
            },
        )

        assert start_response.status_code == 200
        assert message_response.status_code == 200
        payload = message_response.json()
        assert payload["assistant_message"] == "Mocked tenant answer"
        assert payload["retrieved_chunk_count"] == 1
        assert payload["lead_capture"]["lead_id"] is not None
        assert "customer_phone" in payload["lead_capture"]["captured_fields"]
        assert "job_type" in payload["lead_capture"]["captured_fields"]

        system_prompt = chat_provider.messages[0].content
        assert "Tenant A handles blocked drains" in system_prompt
        assert "Tenant B handles switchboard" not in system_prompt

        messages = list(session.scalars(select(Message)))
        assert {message.tenant_id for message in messages} == {tenant_a.id}
        lead = session.scalars(select(Lead).where(Lead.tenant_id == tenant_a.id)).one()
        assert lead.conversation_id == conversation_id
        assert lead.job_type == "blocked drain"
        usage_events = list(
            session.scalars(select(UsageLog).where(UsageLog.tenant_id == tenant_a.id))
        )
        assert {event.event_type for event in usage_events} == {
            "conversation_started",
            "lead_qualified",
            "message_received",
            "assistant_response_generated",
        }


def test_conversation_message_rejects_cross_tenant_widget_key():
    with create_test_session() as session:
        tenant_a, _widget_a = seed_tenant_with_widget(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            "wm_live_test_widget_a",
        )
        seed_tenant_with_widget(
            session,
            "Tenant B Electrical",
            "tenant-b",
            "wm_live_test_widget_b",
        )
        session.commit()
        client = create_client(
            session,
            DeterministicEmbeddingProvider(16),
            RecordingChatProvider(),
        )

        start_response = client.post(
            "/chat/conversations",
            json={"widget_key": "wm_live_test_widget_a"},
        )
        conversation_id = start_response.json()["conversation_id"]
        cross_tenant_response = client.post(
            f"/chat/conversations/{conversation_id}/messages",
            json={
                "widget_key": "wm_live_test_widget_b",
                "message": "Can you help with a blocked drain?",
            },
        )

        assert cross_tenant_response.status_code == 404
        messages = list(
            session.scalars(
                select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.tenant_id == tenant_a.id,
                )
            )
        )
        assert messages == []
