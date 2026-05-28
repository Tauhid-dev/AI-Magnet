"""Private local storage for tenant-owned uploaded documents."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.core.config import Settings, get_settings


class DocumentStorageError(RuntimeError):
    """Raised when document storage cannot safely access a path."""


class LocalDocumentStorage:
    """Store uploaded documents outside public web paths."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.root = Path(self.settings.document_storage_root).expanduser().resolve()

    def save(self, *, tenant_id: str, document_id: str, filename: str, content: bytes) -> str:
        """Persist content and return a root-relative storage path."""
        relative_path = Path(tenant_id) / document_id / filename
        absolute_path = self._resolve(relative_path)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return relative_path.as_posix()

    def read(self, storage_path: str) -> bytes:
        """Read a previously stored private document."""
        return self._resolve(Path(storage_path)).read_bytes()

    def delete(self, storage_path: str | None) -> bool:
        """Delete one stored file if it exists."""
        if not storage_path:
            return False
        absolute_path = self._resolve(Path(storage_path))
        if absolute_path.exists():
            absolute_path.unlink()
            self._prune_empty_parents(absolute_path.parent)
            return True
        return False

    def delete_document_dir(self, *, tenant_id: str, document_id: str) -> bool:
        """Delete a tenant/document storage directory."""
        absolute_path = self._resolve(Path(tenant_id) / document_id)
        if absolute_path.exists() and absolute_path.is_dir():
            shutil.rmtree(absolute_path)
            self._prune_empty_parents(absolute_path.parent)
            return True
        return False

    def _resolve(self, relative_path: Path) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise DocumentStorageError("Document storage path escapes configured root")
        return candidate

    def _prune_empty_parents(self, path: Path) -> None:
        while path != self.root and self.root in path.parents:
            try:
                path.rmdir()
            except OSError:
                return
            path = path.parent
