"""Local no-network email provider."""

from __future__ import annotations

import hashlib

from app.providers.email.base import EmailMessagePayload, EmailSendResult


class ConsoleEmailProvider:
    """Treat email as delivered for local development and automated tests."""

    def send(self, message: EmailMessagePayload) -> EmailSendResult:
        """Return a deterministic success without exposing customer data in logs."""
        digest = hashlib.sha256(f"{message.to_email}:{message.subject}".encode()).hexdigest()
        return EmailSendResult(
            success=True,
            provider_message_id=f"console:{digest[:12]}",
        )
