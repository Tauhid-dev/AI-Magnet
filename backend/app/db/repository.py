"""Tenant-scoped repository helpers."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class TenantScopedRepository(Generic[ModelT]):
    """Repository that always filters reads by tenant_id."""

    def __init__(self, session: Session, model: type[ModelT], tenant_id: str) -> None:
        self.session = session
        self.model = model
        self.tenant_id = tenant_id

    def add(self, instance: ModelT) -> ModelT:
        """Add a tenant-owned model after verifying tenant ownership."""
        instance_tenant_id = getattr(instance, "tenant_id", None)
        if instance_tenant_id != self.tenant_id:
            raise ValueError("Cannot add record for a different tenant")
        self.session.add(instance)
        return instance

    def list(self) -> list[ModelT]:
        """Return only records for this repository's tenant."""
        statement = select(self.model).where(self.model.tenant_id == self.tenant_id)
        return list(self.session.scalars(statement))

    def get(self, record_id: str) -> ModelT | None:
        """Return one tenant-owned record by id or None."""
        statement = select(self.model).where(
            self.model.id == record_id,
            self.model.tenant_id == self.tenant_id,
        )
        return self.session.scalars(statement).first()
