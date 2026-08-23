import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CreditTransaction, CreditWallet


class InsufficientCreditsError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


def credit_credits(
    db: Session,
    *,
    user_id: uuid.UUID,
    amount: int,
    idempotency_key: str,
    kind: str,
    reference: str | None = None,
) -> CreditTransaction:
    """Atomically add credits and append a matching ledger transaction."""
    if amount <= 0:
        raise ValueError("Credit amount must be positive.")
    if kind not in {"grant", "purchase", "refund", "adjustment"}:
        raise ValueError("Invalid credit transaction kind.")

    existing = db.scalar(
        select(CreditTransaction).where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if (
            existing.kind == kind
            and existing.amount == amount
            and existing.reference == reference
        ):
            return existing
        raise IdempotencyConflictError

    new_balance = db.scalar(
        update(CreditWallet)
        .where(CreditWallet.user_id == user_id)
        .values(balance=CreditWallet.balance + amount)
        .returning(CreditWallet.balance)
    )
    if new_balance is None:
        raise ValueError("Credit wallet does not exist.")

    transaction = CreditTransaction(
        user_id=user_id,
        amount=amount,
        balance_after=new_balance,
        kind=kind,
        idempotency_key=idempotency_key,
        reference=reference,
    )
    db.add(transaction)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise IdempotencyConflictError from None
    return transaction


def debit_credits(
    db: Session,
    *,
    user_id: uuid.UUID,
    amount: int,
    idempotency_key: str,
    reference: str | None = None,
) -> CreditTransaction:
    """Atomically debit a wallet and record the charge in the same transaction.

    Callers own the transaction boundary: this function flushes but does not commit.
    Reusing a key with the same charge returns the original transaction; reusing it
    for a different charge is rejected.
    """
    if amount <= 0:
        raise ValueError("Debit amount must be positive.")

    existing = db.scalar(
        select(CreditTransaction).where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if (
            existing.kind == "inference_charge"
            and existing.amount == -amount
            and existing.reference == reference
        ):
            return existing
        raise IdempotencyConflictError

    new_balance = db.scalar(
        update(CreditWallet)
        .where(CreditWallet.user_id == user_id, CreditWallet.balance >= amount)
        .values(balance=CreditWallet.balance - amount)
        .returning(CreditWallet.balance)
    )
    if new_balance is None:
        raise InsufficientCreditsError

    transaction = CreditTransaction(
        user_id=user_id,
        amount=-amount,
        balance_after=new_balance,
        kind="inference_charge",
        idempotency_key=idempotency_key,
        reference=reference,
    )
    db.add(transaction)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise IdempotencyConflictError from None
    return transaction
