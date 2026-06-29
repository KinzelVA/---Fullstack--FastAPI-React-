from fastapi.testclient import TestClient


def test_admin_login_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "admin",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_admin_login_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


def test_get_current_admin_success(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["username"] == "admin"
    assert data["is_admin"] is True


def test_get_current_admin_without_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate authentication credentials."
    }
