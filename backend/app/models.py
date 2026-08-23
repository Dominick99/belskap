import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    BigInteger,
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
    credit_wallet: Mapped["CreditWallet | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class CreditWallet(Base):
    __tablename__ = "credit_wallets"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_credit_wallets_balance_nonnegative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    balance: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="credit_wallet")
    transactions: Mapped[list["CreditTransaction"]] = relationship(
        back_populates="wallet", cascade="all, delete-orphan"
    )


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    __table_args__ = (
        CheckConstraint("amount != 0", name="ck_credit_transactions_amount_nonzero"),
        CheckConstraint(
            "kind IN ('grant', 'purchase', 'refund', 'inference_charge', 'adjustment')",
            name="ck_credit_transactions_kind",
        ),
        UniqueConstraint(
            "user_id", "idempotency_key", name="uq_credit_transactions_user_id_key"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credit_wallets.user_id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int] = mapped_column(BigInteger)
    balance_after: Mapped[int] = mapped_column(BigInteger)
    kind: Mapped[str] = mapped_column(String(30))
    idempotency_key: Mapped[str] = mapped_column(String(255))
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    wallet: Mapped[CreditWallet] = relationship(back_populates="transactions")


class CreditPurchase(Base):
    __tablename__ = "credit_purchases"
    __table_args__ = (
        CheckConstraint("credits > 0", name="ck_credit_purchases_credits_positive"),
        CheckConstraint(
            "amount_total IS NULL OR amount_total >= 0",
            name="ck_credit_purchases_amount_nonnegative",
        ),
        CheckConstraint(
            "status IN ('creating', 'open', 'paid', 'failed', 'expired', 'refunded')",
            name="ck_credit_purchases_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    package_id: Mapped[str] = mapped_column(String(50))
    credits: Mapped[int] = mapped_column(BigInteger)
    stripe_price_id: Mapped[str] = mapped_column(String(255))
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    amount_total: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="creating")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
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
