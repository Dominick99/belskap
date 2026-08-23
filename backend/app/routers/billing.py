from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from stripe import SignatureVerificationError, StripeError

from app.billing import (
    BillingConfigurationError,
    InvalidStripeEventError,
    configured_packages,
    create_stripe_checkout,
    fulfill_checkout_session,
    verify_stripe_event,
)
from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import CreditPurchase, User
from app.schemas import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    CreditPackageResponse,
)


router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.get("/packages", response_model=list[CreditPackageResponse])
def list_credit_packages() -> list[CreditPackageResponse]:
    packages = configured_packages(get_settings())
    return [
        CreditPackageResponse(id=package.id, credits=package.credits)
        for package in packages.values()
    ]


@router.post("/checkout", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckoutSessionResponse:
    settings = get_settings()
    package = configured_packages(settings).get(payload.package_id)
    if package is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="That credit package is not available.",
        )

    purchase = CreditPurchase(
        user_id=user.id,
        package_id=package.id,
        credits=package.credits,
        stripe_price_id=package.stripe_price_id,
        status="creating",
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    try:
        session_id, checkout_url = create_stripe_checkout(
            purchase=purchase, user_email=user.email, settings=settings
        )
    except (BillingConfigurationError, StripeError):
        purchase.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Checkout is temporarily unavailable.",
        ) from None

    purchase.stripe_checkout_session_id = session_id
    purchase.status = "open"
    db.commit()
    return CheckoutSessionResponse(checkout_url=checkout_url)


@router.post("/stripe/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def receive_stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> None:
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature.")

    try:
        event = verify_stripe_event(
            await request.body(), stripe_signature, get_settings()
        )
    except (ValueError, SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.") from None
    except BillingConfigurationError:
        raise HTTPException(
            status_code=503, detail="Stripe webhooks are not configured."
        ) from None

    if event.type in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        if event.data.object.get("payment_status") != "paid":
            return
        try:
            fulfill_checkout_session(db, event.data.object)
            db.commit()
        except InvalidStripeEventError:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Invalid checkout session."
            ) from None
