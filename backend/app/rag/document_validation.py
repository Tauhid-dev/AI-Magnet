"""Secure tenant document upload validation."""

from __future__ import annotations

import hashlib
import re
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePath

from pypdf import PdfReader

from app.core.config import Settings


CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_MARKDOWN = "text/markdown"
CONTENT_TYPE_PDF = "application/pdf"
CONTENT_TYPE_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

SUPPORTED_DOCUMENT_TYPES = {
    CONTENT_TYPE_TEXT,
    CONTENT_TYPE_MARKDOWN,
    "application/x-markdown",
    CONTENT_TYPE_PDF,
    CONTENT_TYPE_DOCX,
}

EXTENSION_CONTENT_TYPES = {
    ".txt": CONTENT_TYPE_TEXT,
    ".md": CONTENT_TYPE_MARKDOWN,
    ".markdown": CONTENT_TYPE_MARKDOWN,
    ".pdf": CONTENT_TYPE_PDF,
    ".docx": CONTENT_TYPE_DOCX,
}

EICAR_TEST_STRING = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR"


@dataclass(frozen=True)
class ValidatedDocumentUpload:
    """Validated metadata for a tenant-owned document file."""

    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    malware_scan_status: str


class DocumentValidationError(ValueError):
    """Raised when an uploaded document is unsafe or unsupported."""


def validate_document_upload(
    *,
    filename: str,
    content: bytes,
    content_type: str | None,
    settings: Settings,
) -> ValidatedDocumentUpload:
    """Validate size, name, type, signature, and basic malware marker."""
    safe_filename = sanitize_filename(filename)
    size_bytes = len(content)
    if size_bytes == 0:
        raise DocumentValidationError("Uploaded document is empty")
    if size_bytes > settings.document_upload_max_bytes:
        raise DocumentValidationError("Uploaded document exceeds the configured size limit")

    detected_type = detect_content_type(safe_filename, content, content_type)
    if detected_type not in SUPPORTED_DOCUMENT_TYPES:
        raise DocumentValidationError("Unsupported document type")

    normalized_type = normalize_content_type(detected_type)
    validate_signature(normalized_type, content)
    if normalized_type == CONTENT_TYPE_PDF:
        validate_pdf_shape(content, settings.document_upload_max_pages)
    malware_scan_status = scan_document_bytes(content, settings.document_malware_scan_mode)

    return ValidatedDocumentUpload(
        filename=safe_filename,
        content_type=normalized_type,
        size_bytes=size_bytes,
        sha256=hashlib.sha256(content).hexdigest(),
        malware_scan_status=malware_scan_status,
    )


def sanitize_filename(filename: str) -> str:
    """Return a storage-safe filename without path components."""
    name = PurePath(filename or "").name.strip()
    if not name or name in {".", ".."}:
        raise DocumentValidationError("Uploaded document filename is invalid")
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if not name:
        raise DocumentValidationError("Uploaded document filename is invalid")
    return name[:180]


def detect_content_type(filename: str, content: bytes, content_type: str | None) -> str:
    """Detect supported document type using extension plus signature hints."""
    extension = PurePath(filename).suffix.lower()
    claimed = normalize_content_type(content_type)
    extension_type = EXTENSION_CONTENT_TYPES.get(extension)
    if extension_type is None and claimed in SUPPORTED_DOCUMENT_TYPES:
        extension_type = claimed

    if extension_type is None:
        raise DocumentValidationError("Unsupported document extension")
    if claimed and claimed != "application/octet-stream" and not content_types_compatible(
        claimed,
        extension_type,
    ):
        raise DocumentValidationError("Uploaded document content type does not match filename")
    return extension_type


def normalize_content_type(content_type: str | None) -> str:
    """Normalize content type aliases."""
    normalized = (content_type or "").split(";")[0].strip().lower()
    if normalized == "application/x-markdown":
        return CONTENT_TYPE_MARKDOWN
    return normalized


def content_types_compatible(claimed: str, detected: str) -> bool:
    """Return true when safe text aliases are equivalent for upload purposes."""
    if claimed == detected:
        return True
    text_aliases = {CONTENT_TYPE_TEXT, CONTENT_TYPE_MARKDOWN}
    return claimed in text_aliases and detected in text_aliases


def validate_signature(content_type: str, content: bytes) -> None:
    """Reject files whose bytes do not match their allowed type."""
    if content_type == CONTENT_TYPE_PDF:
        if not content.startswith(b"%PDF-"):
            raise DocumentValidationError("PDF upload is malformed or has the wrong signature")
        return
    if content_type == CONTENT_TYPE_DOCX:
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile as exc:
            raise DocumentValidationError("DOCX upload is malformed") from exc
        if "[Content_Types].xml" not in names or "word/document.xml" not in names:
            raise DocumentValidationError("DOCX upload is missing required document parts")
        return
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentValidationError("Text document must be UTF-8 encoded") from exc


def validate_pdf_shape(content: bytes, max_pages: int) -> None:
    """Reject malformed or oversized PDFs before storing bytes."""
    try:
        reader = PdfReader(BytesIO(content))
        page_count = len(reader.pages)
    except Exception as exc:
        raise DocumentValidationError("PDF upload is malformed") from exc
    if page_count <= 0:
        raise DocumentValidationError("PDF upload does not contain pages")
    if page_count > max_pages:
        raise DocumentValidationError("PDF upload exceeds the configured page limit")


def scan_document_bytes(content: bytes, scan_mode: str) -> str:
    """Perform deterministic local upload screening before storage."""
    mode = scan_mode.strip().lower()
    if mode == "disabled":
        return "not_scanned"
    if EICAR_TEST_STRING in content:
        raise DocumentValidationError("Uploaded document failed malware screening")
    if mode == "external":
        return "passed_basic_external_required"
    return "passed_basic"
