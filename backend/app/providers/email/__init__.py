"""Email provider package exports."""

from app.providers.email.base import EmailMessagePayload, EmailProvider, EmailSendResult
from app.providers.email.factory import get_email_provider

__all__ = [
    "EmailMessagePayload",
    "EmailProvider",
    "EmailSendResult",
    "get_email_provider",
]
