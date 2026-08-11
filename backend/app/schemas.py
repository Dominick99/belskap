import uuid
from datetime import datetime

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AvatarVisibility(StrEnum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class AvatarMediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"


class AvatarCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(
        min_length=1, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    bio: str | None = Field(default=None, max_length=2000)
    visibility: AvatarVisibility = AvatarVisibility.PRIVATE

    @field_validator("name", "bio", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value

class AvatarUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    bio: str | None = Field(default=None, max_length=2000)
    visibility: AvatarVisibility | None = None
    profile_media_id: uuid.UUID | None = None

    @field_validator("name", "bio", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("name", "slug", "visibility")
    @classmethod
    def prevent_null_required_fields(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null.")
        return value


class AvatarResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    bio: str | None
    visibility: AvatarVisibility
    profile_media_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AvatarMediaCreate(BaseModel):
    media_type: AvatarMediaType
    storage_key: str = Field(min_length=1, max_length=1024)
    thumbnail_key: str | None = Field(default=None, max_length=1024)
    mime_type: str | None = Field(default=None, max_length=100)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    duration_seconds: float | None = Field(default=None, gt=0)

    @field_validator("storage_key", "thumbnail_key", "mime_type", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if not isinstance(value, str):
            return value
        return value.strip() or None


class AvatarMediaUpdate(BaseModel):
    thumbnail_key: str | None = Field(default=None, max_length=1024)
    mime_type: str | None = Field(default=None, max_length=100)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    duration_seconds: float | None = Field(default=None, gt=0)

    @field_validator("thumbnail_key", "mime_type", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if not isinstance(value, str):
            return value
        return value.strip() or None


class AvatarMediaResponse(BaseModel):
    id: uuid.UUID
    avatar_id: uuid.UUID
    media_type: AvatarMediaType
    storage_key: str
    thumbnail_key: str | None
    mime_type: str | None
    width: int | None
    height: int | None
    duration_seconds: float | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
