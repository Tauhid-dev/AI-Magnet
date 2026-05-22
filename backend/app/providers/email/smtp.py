"""SMTP email provider."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import Settings
from app.providers.email.base import EmailMessagePayload, EmailSendResult


class SmtpEmailProvider:
    """Send plain-text notification emails via SMTP settings."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, message: EmailMessagePayload) -> EmailSendResult:
        """Send the message through the configured SMTP server."""
        if not self.settings.smtp_host:
            return EmailSendResult(success=False, error_message="SMTP_HOST is not configured")

        from_email = message.from_email or self.settings.smtp_from_email
        if not from_email:
            return EmailSendResult(success=False, error_message="SMTP_FROM_EMAIL is not configured")

        email = EmailMessage()
        email["From"] = from_email
        email["To"] = message.to_email
        email["Subject"] = message.subject
        email.set_content(message.body_text)

        try:
            if self.settings.smtp_use_tls:
                with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port) as client:
                    self._login(client)
                    client.send_message(email)
            else:
                with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as client:
                    if self.settings.smtp_starttls:
                        client.starttls()
                    self._login(client)
                    client.send_message(email)
        except Exception as exc:
            return EmailSendResult(success=False, error_message=str(exc))
        return EmailSendResult(success=True)

    def _login(self, client: smtplib.SMTP) -> None:
        if self.settings.smtp_username and self.settings.smtp_password:
            client.login(self.settings.smtp_username, self.settings.smtp_password)
