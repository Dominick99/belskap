"""Create durable Stripe credit purchase records."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260822_02"
down_revision: str | None = "20260822_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credit_purchases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("package_id", sa.String(length=50), nullable=False),
        sa.Column("credits", sa.BigInteger(), nullable=False),
        sa.Column("stripe_price_id", sa.String(length=255), nullable=False),
        sa.Column(
            "stripe_checkout_session_id", sa.String(length=255), nullable=True
        ),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("amount_total", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "credits > 0", name="ck_credit_purchases_credits_positive"
        ),
        sa.CheckConstraint(
            "amount_total IS NULL OR amount_total >= 0",
            name="ck_credit_purchases_amount_nonnegative",
        ),
        sa.CheckConstraint(
            "status IN ('creating', 'open', 'paid', 'failed', 'expired', 'refunded')",
            name="ck_credit_purchases_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_checkout_session_id"),
    )
    op.create_index(
        op.f("ix_credit_purchases_user_id"), "credit_purchases", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_credit_purchases_user_id"), table_name="credit_purchases")
    op.drop_table("credit_purchases")
