"""Create avatar media table and add profile media to avatars."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260811_01"
down_revision: str | None = "20260810_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "avatar_media",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("avatar_id", sa.Uuid(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("thumbnail_key", sa.String(length=1024), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
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
            "media_type IN ('image', 'video')", name="ck_avatar_media_type"
        ),
        sa.ForeignKeyConstraint(["avatar_id"], ["avatars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        op.f("ix_avatar_media_avatar_id"), "avatar_media", ["avatar_id"]
    )
    op.add_column("avatars", sa.Column("profile_media_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_avatars_profile_media_id_avatar_media",
        "avatars",
        "avatar_media",
        ["profile_media_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_avatars_profile_media_id_avatar_media", "avatars", type_="foreignkey"
    )
    op.drop_column("avatars", "profile_media_id")
    op.drop_index(op.f("ix_avatar_media_avatar_id"), table_name="avatar_media")
    op.drop_table("avatar_media")
