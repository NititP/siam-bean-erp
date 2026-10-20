from fastapi.testclient import TestClient

from app.main import app


def test_health_answers_without_login():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
