import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    avatars: Mapped[list["Avatar"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Avatar(Base):
    __tablename__ = "avatars"
    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_avatars_user_id_slug"),
        CheckConstraint(
            "visibility IN ('private', 'unlisted', 'public')",
            name="ck_avatars_visibility",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    profile_media_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "avatar_media.id",
            name="fk_avatars_profile_media_id_avatar_media",
            ondelete="SET NULL",
            use_alter=True,
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped[User] = relationship(back_populates="avatars")
    media: Mapped[list["AvatarMedia"]] = relationship(
        back_populates="avatar",
        cascade="all, delete-orphan",
        foreign_keys="AvatarMedia.avatar_id",
    )
    profile_media: Mapped["AvatarMedia | None"] = relationship(
        foreign_keys=[profile_media_id], post_update=True
    )


class AvatarMedia(Base):
    __tablename__ = "avatar_media"
    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video')", name="ck_avatar_media_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    avatar_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("avatars.id", ondelete="CASCADE"), index=True
    )
    media_type: Mapped[str] = mapped_column(String(20))
    storage_key: Mapped[str] = mapped_column(String(1024), unique=True)
    thumbnail_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    avatar: Mapped[Avatar] = relationship(
        back_populates="media", foreign_keys=[avatar_id]
    )
