from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def test_registers_user_and_hashes_password(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "New.User@Example.com",
            "username": "New_User",
            "password": "correct horse battery",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new.user@example.com"
    assert response.json()["username"] == "new_user"
    assert "password" not in response.json()

    user = db_session.scalar(select(User))
    assert user is not None
    assert user.email == "new.user@example.com"
    assert user.username == "new_user"
    assert user.password_hash != "correct horse battery"


def test_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "user@example.com",
        "username": "test_user",
        "password": "a secure password",
    }

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_rejects_invalid_email_and_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "username": "no", "password": "short"},
    )

    assert response.status_code == 422


def test_login_returns_token_that_can_fetch_current_user(client: TestClient) -> None:
    credentials = {"email": "user@example.com", "password": "a secure password"}
    client.post(
        "/api/v1/auth/register", json={**credentials, "username": "test_user"}
    )

    login_response = client.post("/api/v1/auth/login", json=credentials)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"
    assert me_response.json()["username"] == "test_user"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "test_user",
            "password": "a secure password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "the wrong password"},
    )

    assert response.status_code == 401


def test_rejects_duplicate_username(client: TestClient) -> None:
    first = {
        "email": "first@example.com",
        "username": "shared_name",
        "password": "a secure password",
    }
    second = {
        "email": "second@example.com",
        "username": "SHARED_NAME",
        "password": "a secure password",
    }

    assert client.post("/api/v1/auth/register", json=first).status_code == 201
    response = client.post("/api/v1/auth/register", json=second)

    assert response.status_code == 409
    assert response.json()["detail"] == "An account with this username already exists."


def test_requires_valid_username(client: TestClient) -> None:
    for username in ("ab", "has spaces", "punctuation!"):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": username,
                "password": "a secure password",
            },
        )
        assert response.status_code == 422

    missing_username = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "a secure password"},
    )
    assert missing_username.status_code == 422
