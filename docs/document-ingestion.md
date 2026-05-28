# Secure Document Ingestion

PR-07 adds the beta document upload path for tenant-owned knowledge files.

## Supported Types

- Plain text: `.txt`, `text/plain`
- Markdown: `.md`, `.markdown`, `text/markdown`
- PDF: `.pdf`, `application/pdf`
- DOCX: `.docx`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

Uploads are accepted only through authenticated business portal sessions. Every document row is stored with `tenant_id`, source metadata, file size, SHA-256 hash, malware scan status, extraction status, OCR status, and a private storage path.

## Validation Controls

The upload API validates:

- Filename sanitisation with path components removed.
- Configured maximum size via `DOCUMENT_UPLOAD_MAX_BYTES`.
- Supported extension and content type alignment.
- PDF signature check.
- DOCX ZIP/package structure check.
- UTF-8 validation for text and Markdown.
- Basic deterministic malware screening, including EICAR test string rejection.

Production must not run with `DOCUMENT_MALWARE_SCAN_MODE=disabled`.

## Private Storage

Uploaded files are written under `DOCUMENT_STORAGE_ROOT` through `LocalDocumentStorage`. The storage layer resolves every path under the configured root and rejects traversal outside it.

`docker-compose.yml` and `docker-compose.prod.yml` mount a private `document_storage` volume for backend and worker containers. The volume is not served by Nginx or the frontend.

## Worker Processing

File uploads enqueue `rag.document_file_ingestion`. The job payload contains only `document_id`; raw bytes are read by the worker from private storage. This avoids storing customer documents in background job payloads.

The worker extracts text, chunks it, creates embeddings, records usage, and updates document state. Failed extraction leaves a visible `failed` document with `error_message`, `extraction_status`, and `ocr_status`.

## Extraction and OCR

- PDF text extraction uses selectable text through `pypdf`.
- DOCX extraction reads paragraphs and tables through `python-docx`.
- Scanned PDFs without selectable text fail closed with `ocr_status=required` unless OCR is explicitly enabled later.
- OCR runtime remains gated; no production OCR engine is claimed in PR-07.

## Lifecycle Controls

Business portal users can:

- Upload supported files.
- Refresh/re-index stored uploaded files.
- Delete tenant-owned documents and private stored files.

All refresh and delete operations filter by the authenticated tenant before touching database rows or storage.

## Environment

```env
DOCUMENT_STORAGE_ROOT=storage/documents
DOCUMENT_UPLOAD_MAX_BYTES=10485760
DOCUMENT_UPLOAD_MAX_PAGES=50
DOCUMENT_OCR_ENABLED=false
DOCUMENT_MALWARE_SCAN_MODE=basic
```

Production validation rejects missing storage roots, non-positive limits, unknown scan modes, and disabled malware scanning.
