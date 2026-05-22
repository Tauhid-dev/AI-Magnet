from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import create_app  # noqa: E402


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
