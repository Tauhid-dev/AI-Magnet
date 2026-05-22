"""Conversation and message models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Conversation(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Website widget conversation scoped to one tenant."""

    __tablename__ = "conversations"

    visitor_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open", index=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="website_widget")

    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Single message inside a tenant-scoped conversation."""

    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
