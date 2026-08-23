import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.credits import InsufficientCreditsError, debit_credits
from app.models import CreditTransaction, CreditWallet, User
from app.security import create_access_token, hash_password


def create_user_with_credits(db: Session, balance: int) -> User:
    user = User(
        email=f"{uuid.uuid4()}@example.com",
        username=f"user_{uuid.uuid4().hex[:12]}",
        password_hash=hash_password("a secure password"),
    )
    db.add(user)
    db.flush()
    db.add(CreditWallet(user_id=user.id, balance=balance))
    db.commit()
    return user


def test_registration_creates_an_empty_wallet(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "wallet@example.com",
            "username": "wallet_user",
            "password": "a secure password",
        },
    )

    assert response.status_code == 201
    user = db_session.scalar(select(User).where(User.email == "wallet@example.com"))
    assert user is not None
    assert db_session.get(CreditWallet, user.id).balance == 0


def test_balance_endpoint_is_authenticated(
    client: TestClient, db_session: Session
) -> None:
    user = create_user_with_credits(db_session, 125)

    unauthenticated = client.get("/api/v1/credits/balance")
    response = client.get(
        "/api/v1/credits/balance",
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )

    assert unauthenticated.status_code == 401
    assert response.status_code == 200
    assert response.json() == {"balance": 125, "unit": "credit"}


def test_debit_is_atomic_and_records_ledger_entry(db_session: Session) -> None:
    user = create_user_with_credits(db_session, 100)

    transaction = debit_credits(
        db_session,
        user_id=user.id,
        amount=35,
        idempotency_key="generation-request-1",
        reference="image-model-v1",
    )
    db_session.commit()

    assert db_session.get(CreditWallet, user.id).balance == 65
    assert transaction.amount == -35
    assert transaction.balance_after == 65
    assert transaction.kind == "inference_charge"


def test_retry_does_not_charge_twice(db_session: Session) -> None:
    user = create_user_with_credits(db_session, 100)

    first = debit_credits(
        db_session,
        user_id=user.id,
        amount=25,
        idempotency_key="same-request",
    )
    db_session.commit()
    second = debit_credits(
        db_session,
        user_id=user.id,
        amount=25,
        idempotency_key="same-request",
    )

    assert second.id == first.id
    assert db_session.get(CreditWallet, user.id).balance == 75
    assert len(list(db_session.scalars(select(CreditTransaction)))) == 1


def test_insufficient_balance_cannot_go_negative(db_session: Session) -> None:
    user = create_user_with_credits(db_session, 10)

    with pytest.raises(InsufficientCreditsError):
        debit_credits(
            db_session,
            user_id=user.id,
            amount=11,
            idempotency_key="too-expensive",
        )

    assert db_session.get(CreditWallet, user.id).balance == 10
    assert list(db_session.scalars(select(CreditTransaction))) == []
