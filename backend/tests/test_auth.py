from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def test_registers_user_and_hashes_password(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "New.User@Example.com", "password": "correct horse battery"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new.user@example.com"
    assert "password" not in response.json()

    user = db_session.scalar(select(User))
    assert user is not None
    assert user.email == "new.user@example.com"
    assert user.password_hash != "correct horse battery"


def test_rejects_duplicate_email(client: TestClient) -> None:
    payload = {"email": "user@example.com", "password": "a secure password"}

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_rejects_invalid_email_and_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == 422
