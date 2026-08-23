"""Create credit wallets and append-only credit transactions."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260822_01"
down_revision: str | None = "20260811_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credit_wallets",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("balance", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "balance >= 0", name="ck_credit_wallets_balance_nonnegative"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.execute(
        sa.text("INSERT INTO credit_wallets (user_id) SELECT id FROM users")
    )
    op.create_table(
        "credit_transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("balance_after", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount != 0", name="ck_credit_transactions_amount_nonzero"
        ),
        sa.CheckConstraint(
            "kind IN ('grant', 'purchase', 'refund', 'inference_charge', 'adjustment')",
            name="ck_credit_transactions_kind",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["credit_wallets.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name="uq_credit_transactions_user_id_key"
        ),
    )
    op.create_index(
        op.f("ix_credit_transactions_user_id"),
        "credit_transactions",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_credit_transactions_user_id"), table_name="credit_transactions"
    )
    op.drop_table("credit_transactions")
    op.drop_table("credit_wallets")
