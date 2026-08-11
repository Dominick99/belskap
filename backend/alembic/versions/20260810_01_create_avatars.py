"""Create avatars table."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260810_01"
down_revision: str | None = "20260809_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "avatars",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "visibility", sa.String(length=20), nullable=False, server_default="private"
        ),
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
            "visibility IN ('private', 'unlisted', 'public')",
            name="ck_avatars_visibility",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "slug", name="uq_avatars_user_id_slug"),
    )
    op.create_index(op.f("ix_avatars_user_id"), "avatars", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_avatars_user_id"), table_name="avatars")
    op.drop_table("avatars")
