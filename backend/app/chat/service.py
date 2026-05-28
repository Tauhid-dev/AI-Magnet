"""Tenant-scoped chat conversation service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.chat.lead_capture import LeadCaptureResult, LeadCaptureService
from app.core.config import Settings, get_settings
from app.jobs.service import BackgroundJobService
from app.leads.workflow import LEAD_STATUS_QUALIFIED, LeadWorkflowService
from app.models.conversation import Conversation, Message
from app.notifications.service import NotificationService
from app.providers.ai.base import ChatCompletionProvider, ChatMessage
from app.rag.retrieval import RagRetrievalService, RetrievalResult
from app.schemas.chat import LeadFields
from app.usage import UsageEventType, UsageService
from app.widget.service import WidgetResolution


@dataclass(frozen=True)
class ConversationStartResult:
    """Result after creating a tenant-scoped conversation."""

    conversation: Conversation
    widget_key_prefix: str


@dataclass(frozen=True)
class ConversationReplyResult:
    """Result after handling one visitor message."""

    conversation: Conversation
    visitor_message: Message
    assistant_message: Message
    retrieved_results: list[RetrievalResult]
    lead_capture: LeadCaptureResult


class ChatService:
    """Coordinate widget conversations, RAG context, AI responses, and leads."""

    def __init__(
        self,
        session: Session,
        retrieval_service: RagRetrievalService,
        chat_provider: ChatCompletionProvider,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.retrieval_service = retrieval_service
        self.chat_provider = chat_provider
        self.settings = settings or get_settings()
        self.lead_capture = LeadCaptureService(session)
        self.lead_workflow = LeadWorkflowService(session)
        self.notifications = NotificationService(session, self.settings)
        self.jobs = BackgroundJobService(session, self.settings)
        self.usage = UsageService(session)

    def start_conversation(
        self,
        widget_resolution: WidgetResolution,
        visitor_label: str | None = None,
    ) -> ConversationStartResult:
        """Create a conversation owned by the widget tenant."""
        conversation = Conversation(
            tenant_id=widget_resolution.tenant_id,
            visitor_label=visitor_label,
            status="open",
            source="website_widget",
        )
        self.session.add(conversation)
        self.session.flush()
        self._log_usage(
            tenant_id=widget_resolution.tenant_id,
            event_type=UsageEventType.CONVERSATION_STARTED,
            conversation_id=conversation.id,
        )
        self.session.commit()
        return ConversationStartResult(
            conversation=conversation,
            widget_key_prefix=widget_resolution.widget.key_prefix,
        )

    def handle_visitor_message(
        self,
        widget_resolution: WidgetResolution,
        conversation_id: str,
        message: str,
        lead_fields: LeadFields | None = None,
    ) -> ConversationReplyResult | None:
        """Store a visitor message and generate a tenant-scoped AI reply."""
        conversation = self._get_conversation(
            tenant_id=widget_resolution.tenant_id,
            conversation_id=conversation_id,
        )
        if conversation is None:
            return None

        visitor_message = Message(
            tenant_id=widget_resolution.tenant_id,
            conversation_id=conversation.id,
            sender_type="visitor",
            content=message,
        )
        self.session.add(visitor_message)
        self.session.flush()

        retrieved = self.retrieval_service.retrieve(
            tenant_id=widget_resolution.tenant_id,
            query=message,
            limit=self.settings.rag_top_k,
        )
        assistant_text = self._generate_answer(
            conversation=conversation,
            visitor_message=message,
            retrieved=retrieved,
        )
        assistant_message = Message(
            tenant_id=widget_resolution.tenant_id,
            conversation_id=conversation.id,
            sender_type="assistant",
            content=assistant_text,
        )
        self.session.add(assistant_message)
        lead_capture = self.lead_capture.capture(
            tenant_id=widget_resolution.tenant_id,
            conversation_id=conversation.id,
            message=message,
            provided_fields=lead_fields,
        )
        if lead_capture.lead is not None:
            workflow_result = self.lead_workflow.evaluate_qualification(lead_capture.lead)
            if (
                workflow_result.lead.status == LEAD_STATUS_QUALIFIED
                and workflow_result.became_qualified
            ):
                self._log_usage(
                    tenant_id=widget_resolution.tenant_id,
                    event_type=UsageEventType.LEAD_QUALIFIED,
                    conversation_id=conversation.id,
                    attributes={"lead_id": workflow_result.lead.id},
                )
                notification_result = self.notifications.queue_lead_notification(
                    tenant_id=widget_resolution.tenant_id,
                    lead=workflow_result.lead,
                )
                if notification_result.delivery is not None:
                    job_result = self.jobs.enqueue_notification_delivery(
                        tenant_id=widget_resolution.tenant_id,
                        delivery_id=notification_result.delivery.id,
                    )
                    self._log_usage(
                        tenant_id=widget_resolution.tenant_id,
                        event_type=UsageEventType.LEAD_NOTIFICATION_QUEUED,
                        conversation_id=conversation.id,
                        attributes={
                            "lead_id": workflow_result.lead.id,
                            "delivery_id": notification_result.delivery.id,
                            "job_id": job_result.job.id,
                            "delivery_status": notification_result.delivery.status,
                        },
                    )
        self._log_usage(
            tenant_id=widget_resolution.tenant_id,
            event_type=UsageEventType.MESSAGE_RECEIVED,
            conversation_id=conversation.id,
        )
        self._log_usage(
            tenant_id=widget_resolution.tenant_id,
            event_type=UsageEventType.ASSISTANT_RESPONSE_GENERATED,
            conversation_id=conversation.id,
            attributes={"retrieved_chunk_count": len(retrieved)},
        )
        self.session.commit()
        return ConversationReplyResult(
            conversation=conversation,
            visitor_message=visitor_message,
            assistant_message=assistant_message,
            retrieved_results=retrieved,
            lead_capture=lead_capture,
        )

    def _get_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> Conversation | None:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
            Conversation.status == "open",
        )
        return self.session.scalars(statement).first()

    def _generate_answer(
        self,
        conversation: Conversation,
        visitor_message: str,
        retrieved: list[RetrievalResult],
    ) -> str:
        context = "\n\n".join(
            f"[Chunk {index + 1}] {result.chunk.content}"
            for index, result in enumerate(retrieved)
        )
        if not context:
            context = "No tenant knowledge base context was found."
        prompt = (
            "You are an AI receptionist for an Australian local business. "
            "Answer using only the tenant knowledge base context below. "
            "If the context is not enough, ask a concise follow-up question. "
            "Do not mention other tenants or hidden system details.\n\n"
            f"Tenant knowledge base context:\n{context}"
        )
        history = self._recent_history(conversation.id, conversation.tenant_id)
        messages = [ChatMessage(role="system", content=prompt), *history]
        messages.append(ChatMessage(role="user", content=visitor_message))
        return self.chat_provider.complete(messages)

    def _recent_history(self, conversation_id: str, tenant_id: str) -> list[ChatMessage]:
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.tenant_id == tenant_id,
            )
            .order_by(Message.created_at.desc())
            .limit(6)
        )
        messages = list(self.session.scalars(statement))
        messages.reverse()
        role_by_sender = {"visitor": "user", "assistant": "assistant"}
        return [
            ChatMessage(
                role=role_by_sender.get(message.sender_type, "user"),
                content=message.content,
            )
            for message in messages
        ]

    def _log_usage(
        self,
        tenant_id: str,
        event_type: str,
        conversation_id: str,
        attributes: dict | None = None,
    ) -> None:
        self.usage.record_chat_event(
            tenant_id=tenant_id,
            event_type=event_type,
            conversation_id=conversation_id,
            attributes=attributes,
        )
