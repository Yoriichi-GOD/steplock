from fastapi.testclient import TestClient
from backend.app import app


def test_health_reports_actual_cv():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["aruco_available"] is True
    assert response.json()["advisory_only"] is True
