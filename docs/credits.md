# Inference credits

Credits are an internal, non-transferable usage entitlement for AI inference. They
must not be described as cash, allowed to move between users, or redeemed for
money without a separate legal and accounting review.

## Foundation implemented

- Every user has one wallet whose balance is a non-negative integer.
- Every balance change has an append-only transaction record.
- Inference debits use a conditional database update, so concurrent requests
  cannot spend the same credits or produce a negative balance.
- An idempotency key scoped to the user prevents a retried inference request from
  being charged twice.
- The authenticated API exposes the balance but no public mint, adjustment, or
  purchase endpoint.

The wallet balance is the fast authorization value. The transaction table is the
audit trail and should be reconciled against wallet balances. Both are changed in
one database transaction.

## Recommended rollout

1. **Meter one fake inference job.** Define a fixed test price, reserve/debit it
   server-side, and use the request ID as the idempotency key. Decide explicitly
   whether a provider failure refunds the charge.
2. **Add internal grants.** Use a locked-down admin or migration path for test
   credits. Never accept a credit amount from an ordinary client.
3. **Add provider usage records.** Persist model, provider request ID, input/output
   units, quoted price, final price, and outcome. Keep pricing configuration
   versioned so old charges remain explainable.
4. **Integrate hosted checkout.** The initial Stripe test-mode integration now
   creates durable purchase records, sends users to hosted Checkout, and grants
   credits only from a verified, idempotent server-side webhook after confirmed
   payment. The browser redirect is never treated as proof of payment.
5. **Reconcile and operate.** Add ledger/balance reconciliation, webhook replay,
   alerts, refund/chargeback handling, rate limits, support tooling, and audit-log
   retention before production sales.

## Rules to preserve

- Use integers only; never floating point for credits or money.
- The server calculates charges from a versioned price table.
- Every external event and inference request has a unique idempotency key.
- A credit grant and its payment-event record commit atomically.
- Corrections are compensating transactions; ledger rows are not edited.
- Secrets and payment details never enter frontend code or application logs.

## Stripe test-mode setup

1. In Stripe test mode, create a one-time Product and Price for the starter
   package. Decide the actual price and credit quantity before presenting it to
   users.
2. Set `STRIPE_SECRET_KEY`, `STRIPE_STARTER_PRICE_ID`, and
   `STRIPE_STARTER_CREDITS` in the backend environment.
3. Forward Stripe test events to
   `POST /api/v1/billing/stripe/webhook` and set the resulting signing secret as
   `STRIPE_WEBHOOK_SECRET`.
4. Apply migrations through `20260822_02`, then use
   `POST /api/v1/billing/checkout` with `{ "package_id": "starter" }` as an
   authenticated user.

This is not ready for live money until refund/chargeback reversal, tax settings,
reconciliation, monitoring, and production deployment controls are implemented.
