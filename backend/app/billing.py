import uuid
from dataclasses import dataclass
from typing import Any

import stripe
from sqlalchemy.orm import Session

from app.config import Settings
from app.credits import credit_credits
from app.models import CreditPurchase


@dataclass(frozen=True)
class CreditPackage:
    id: str
    credits: int
    stripe_price_id: str


class BillingConfigurationError(Exception):
    pass


class InvalidStripeEventError(Exception):
    pass


def configured_packages(settings: Settings) -> dict[str, CreditPackage]:
    if not settings.stripe_starter_price_id:
        return {}
    package = CreditPackage(
        id="starter",
        credits=settings.stripe_starter_credits,
        stripe_price_id=settings.stripe_starter_price_id,
    )
    return {package.id: package}


def create_stripe_checkout(
    *, purchase: CreditPurchase, user_email: str, settings: Settings
) -> tuple[str, str]:
    if not settings.stripe_secret_key:
        raise BillingConfigurationError("Stripe is not configured.")

    client = stripe.StripeClient(settings.stripe_secret_key)
    session = client.v1.checkout.sessions.create(
        {
            "mode": "payment",
            "line_items": [{"price": purchase.stripe_price_id, "quantity": 1}],
            "client_reference_id": str(purchase.user_id),
            "customer_email": user_email,
            "success_url": (
                f"{settings.frontend_url}/dashboard/credits/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            "cancel_url": f"{settings.frontend_url}/dashboard/credits",
            "metadata": {
                "purchase_id": str(purchase.id),
                "user_id": str(purchase.user_id),
                "package_id": purchase.package_id,
                "credits": str(purchase.credits),
            },
        },
        options={"idempotency_key": f"credit-purchase:{purchase.id}"},
    )
    if not session.url:
        raise BillingConfigurationError("Stripe did not return a checkout URL.")
    return session.id, session.url


def verify_stripe_event(
    payload: bytes, signature: str, settings: Settings
) -> stripe.Event:
    if not settings.stripe_webhook_secret:
        raise BillingConfigurationError("Stripe webhooks are not configured.")
    return stripe.Webhook.construct_event(
        payload, signature, settings.stripe_webhook_secret
    )


def fulfill_checkout_session(db: Session, session: Any) -> CreditPurchase:
    metadata = session.get("metadata") or {}
    try:
        purchase_id = uuid.UUID(metadata["purchase_id"])
        metadata_user_id = uuid.UUID(metadata["user_id"])
        metadata_credits = int(metadata["credits"])
    except (KeyError, TypeError, ValueError) as error:
        raise InvalidStripeEventError("Invalid purchase metadata.") from error

    purchase = db.get(CreditPurchase, purchase_id)
    if purchase is None:
        raise InvalidStripeEventError("Purchase does not exist.")

    session_id = session.get("id")
    amount_total = session.get("amount_total")
    currency = session.get("currency")
    payment_status = session.get("payment_status")
    if (
        purchase.user_id != metadata_user_id
        or purchase.package_id != metadata.get("package_id")
        or purchase.credits != metadata_credits
        or purchase.stripe_checkout_session_id != session_id
        or payment_status != "paid"
        or not isinstance(amount_total, int)
        or amount_total < 0
        or not isinstance(currency, str)
    ):
        raise InvalidStripeEventError("Checkout details do not match the purchase.")

    if purchase.status == "paid":
        return purchase

    credit_credits(
        db,
        user_id=purchase.user_id,
        amount=purchase.credits,
        kind="purchase",
        idempotency_key=f"stripe-checkout:{session_id}",
        reference=session_id,
    )
    purchase.stripe_payment_intent_id = session.get("payment_intent")
    purchase.amount_total = amount_total
    purchase.currency = currency.lower()
    purchase.status = "paid"
    db.flush()
    return purchase
