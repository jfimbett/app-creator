from fastapi.testclient import TestClient

from app.main import APP_NAME, app

client = TestClient(app)


def test_health_reports_ok_and_app_name() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": APP_NAME}


def test_unknown_api_route_is_404() -> None:
    assert client.get("/api/does-not-exist").status_code == 404
