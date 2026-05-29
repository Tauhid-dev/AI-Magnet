from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app


def test_health_check_returns_runtime_context():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "AI Tradie Receptionist API",
        "environment": "local",
        "version": "0.1.0",
    }


def test_health_check_returns_request_correlation_header():
    client = TestClient(create_app())

    response = client.get("/health", headers={"X-Request-ID": "test-request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"
    assert response.headers["X-Correlation-ID"] == "test-request-123"


def test_readiness_check_reports_database_and_config_state():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    app = create_app()

    def override_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
    assert response.json()["checks"]["database_connectivity"] == "pass"
