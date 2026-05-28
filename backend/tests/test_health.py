from fastapi.testclient import TestClient

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
