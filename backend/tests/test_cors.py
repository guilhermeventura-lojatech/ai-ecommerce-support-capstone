from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_local_vite_origin_is_allowed() -> None:
    response = client.options(
        "/support/messages",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_non_local_origin_is_not_allowed() -> None:
    response = client.options(
        "/support/messages",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in response.headers
