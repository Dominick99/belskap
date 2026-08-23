import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.billing import InvalidStripeEventError, fulfill_checkout_session
from app.config import get_settings
from app.models import CreditPurchase, CreditTransaction, CreditWallet, User
from app.security import create_access_token, hash_password


def create_user(db: Session) -> User:
    user = User(
        email=f"{uuid.uuid4()}@example.com",
        username=f"user_{uuid.uuid4().hex[:12]}",
        password_hash=hash_password("a secure password"),
    )
    db.add(user)
    db.flush()
    db.add(CreditWallet(user_id=user.id))
    db.commit()
    return user


def stripe_settings():
    return get_settings().model_copy(
        update={
            "stripe_secret_key": "sk_test_example",
            "stripe_webhook_secret": "whsec_example",
            "stripe_starter_price_id": "price_starter",
            "stripe_starter_credits": 1000,
        }
    )


def test_checkout_uses_server_configured_package(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = create_user(db_session)
    captured_purchase: CreditPurchase | None = None

    def fake_checkout(*, purchase, user_email, settings):
        nonlocal captured_purchase
        captured_purchase = purchase
        return "cs_test_123", "https://checkout.stripe.test/session"

    monkeypatch.setattr("app.routers.billing.get_settings", stripe_settings)
    monkeypatch.setattr("app.routers.billing.create_stripe_checkout", fake_checkout)

    response = client.post(
        "/api/v1/billing/checkout",
        json={"package_id": "starter", "credits": 999999999},
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "checkout_url": "https://checkout.stripe.test/session"
    }
    assert captured_purchase is not None
    assert captured_purchase.credits == 1000
    assert captured_purchase.stripe_price_id == "price_starter"
    assert captured_purchase.stripe_checkout_session_id == "cs_test_123"


def test_checkout_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/billing/checkout", json={"package_id": "starter"}
    )
    assert response.status_code == 401


def test_successful_checkout_grants_credits_once(db_session: Session) -> None:
    user = create_user(db_session)
    purchase = CreditPurchase(
        user_id=user.id,
        package_id="starter",
        credits=1000,
        stripe_price_id="price_starter",
        stripe_checkout_session_id="cs_paid",
        status="open",
    )
    db_session.add(purchase)
    db_session.commit()
    session = {
        "id": "cs_paid",
        "payment_status": "paid",
        "amount_total": 1000,
        "currency": "usd",
        "payment_intent": "pi_123",
        "metadata": {
            "purchase_id": str(purchase.id),
            "user_id": str(user.id),
            "package_id": "starter",
            "credits": "1000",
        },
    }

    fulfill_checkout_session(db_session, session)
    db_session.commit()
    fulfill_checkout_session(db_session, session)
    db_session.commit()

    assert db_session.get(CreditWallet, user.id).balance == 1000
    assert purchase.status == "paid"
    transactions = list(db_session.scalars(select(CreditTransaction)))
    assert len(transactions) == 1
    assert transactions[0].amount == 1000
    assert transactions[0].kind == "purchase"


@pytest.mark.parametrize(
    ("changed_field", "changed_value"),
    [
        ("payment_status", "unpaid"),
        ("id", "cs_different"),
    ],
)
def test_invalid_checkout_grants_nothing(
    db_session: Session, changed_field: str, changed_value: str
) -> None:
    user = create_user(db_session)
    purchase = CreditPurchase(
        user_id=user.id,
        package_id="starter",
        credits=1000,
        stripe_price_id="price_starter",
        stripe_checkout_session_id="cs_expected",
        status="open",
    )
    db_session.add(purchase)
    db_session.commit()
    session = {
        "id": "cs_expected",
        "payment_status": "paid",
        "amount_total": 1000,
        "currency": "usd",
        "metadata": {
            "purchase_id": str(purchase.id),
            "user_id": str(user.id),
            "package_id": "starter",
            "credits": "1000",
        },
    }
    session[changed_field] = changed_value

    with pytest.raises(InvalidStripeEventError):
        fulfill_checkout_session(db_session, session)

    assert db_session.get(CreditWallet, user.id).balance == 0
    assert list(db_session.scalars(select(CreditTransaction))) == []
