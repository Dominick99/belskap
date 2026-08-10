"""Add usernames to users."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260809_01"
down_revision: str | None = "20260808_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=30), nullable=True))
    op.execute("UPDATE users SET username = 'user_' || substring(id::text, 1, 8)")
    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
