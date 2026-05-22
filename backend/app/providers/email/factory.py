"""Email provider factory."""

from __future__ import annotations

from app.core.config import Settings
from app.providers.email.base import EmailProvider
from app.providers.email.console import ConsoleEmailProvider
from app.providers.email.smtp import SmtpEmailProvider


def get_email_provider(settings: Settings) -> EmailProvider:
    """Return the configured email provider."""
    provider = settings.email_provider.strip().lower()
    if provider == "smtp":
        return SmtpEmailProvider(settings)
    return ConsoleEmailProvider()
