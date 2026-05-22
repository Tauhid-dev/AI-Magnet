"""Email provider contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmailMessagePayload:
    """Provider-neutral email message payload."""

    to_email: str
    subject: str
    body_text: str
    from_email: str | None = None


@dataclass(frozen=True)
class EmailSendResult:
    """Result returned by an email provider."""

    success: bool
    provider_message_id: str | None = None
    error_message: str | None = None


class EmailProvider(Protocol):
    """Send email through a concrete provider implementation."""

    def send(self, message: EmailMessagePayload) -> EmailSendResult:
        """Send an email payload."""
