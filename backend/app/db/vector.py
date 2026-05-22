"""Portable SQLAlchemy vector type for pgvector-backed embeddings."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TEXT, TypeDecorator


class VectorType(TypeDecorator[list[float]]):
    """Store vectors as pgvector in PostgreSQL and text JSON in tests."""

    impl = TEXT
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        super().__init__()
        self.dimensions = dimensions

    def process_bind_param(
        self,
        value: list[float] | None,
        dialect: Any,
    ) -> str | None:
        if value is None:
            return None
        normalized = [float(item) for item in value]
        if dialect.name == "postgresql":
            return "[" + ",".join(str(item) for item in normalized) + "]"
        return json.dumps(normalized)

    def process_result_value(
        self,
        value: Any,
        dialect: Any,
    ) -> list[float] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return [float(item) for item in value]
        raw = str(value).strip()
        if raw.startswith("[") and raw.endswith("]"):
            return [float(item) for item in json.loads(raw)]
        return [float(item) for item in raw.split(",") if item]


@compiles(VectorType, "postgresql")
def compile_vector_postgresql(type_: VectorType, compiler: Any, **kw: Any) -> str:
    """Compile to pgvector's native vector type in PostgreSQL."""
    return f"vector({type_.dimensions})"


@compiles(VectorType, "sqlite")
def compile_vector_sqlite(type_: VectorType, compiler: Any, **kw: Any) -> str:
    """Compile to text for lightweight SQLite validation."""
    return "TEXT"
