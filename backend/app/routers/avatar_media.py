import uuid
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Avatar, AvatarMedia, User
from app.schemas import AvatarMediaCreate, AvatarMediaResponse, AvatarMediaUpdate
from app.storage import delete_object, upload_object


router = APIRouter(prefix="/api/v1/avatars/{avatar_id}/media", tags=["avatar media"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024
IMAGE_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}


def get_owned_avatar(avatar_id: uuid.UUID, user: User, db: Session) -> Avatar:
    avatar = db.scalar(
        select(Avatar).where(Avatar.id == avatar_id, Avatar.user_id == user.id)
    )
    if avatar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found."
        )
    return avatar


def get_owned_media(
    avatar_id: uuid.UUID, media_id: uuid.UUID, user: User, db: Session
) -> AvatarMedia:
    media = db.scalar(
        select(AvatarMedia)
        .join(Avatar, AvatarMedia.avatar_id == Avatar.id)
        .where(
            AvatarMedia.id == media_id,
            AvatarMedia.avatar_id == avatar_id,
            Avatar.user_id == user.id,
        )
    )
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Avatar media not found."
        )
    return media


@router.post("", response_model=AvatarMediaResponse, status_code=status.HTTP_201_CREATED)
def create_avatar_media(
    avatar_id: uuid.UUID,
    payload: AvatarMediaCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarMedia:
    get_owned_avatar(avatar_id, user, db)
    media = AvatarMedia(avatar_id=avatar_id, **payload.model_dump())
    db.add(media)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This storage key is already in use.",
        ) from None
    db.refresh(media)
    return media


@router.post(
    "/upload-image",
    response_model=AvatarMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_avatar_image(
    avatar_id: uuid.UUID,
    image: Annotated[UploadFile, File(description="JPEG, PNG, or WebP image")],
    set_as_profile: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarMedia:
    avatar = get_owned_avatar(avatar_id, user, db)
    contents = await image.read(MAX_IMAGE_BYTES + 1)
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")

    try:
        with Image.open(BytesIO(contents)) as decoded:
            decoded.verify()
        with Image.open(BytesIO(contents)) as decoded:
            image_format = decoded.format or ""
            width, height = decoded.size
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=422, detail="File is not a valid image.") from None

    format_details = IMAGE_FORMATS.get(image_format)
    if format_details is None:
        raise HTTPException(status_code=422, detail="Image must be JPEG, PNG, or WebP.")
    extension, mime_type = format_details
    storage_key = f"avatars/{avatar.id}/images/{uuid.uuid4()}.{extension}"

    try:
        upload_object(BytesIO(contents), storage_key, mime_type)
        media = AvatarMedia(
            avatar_id=avatar.id,
            media_type="image",
            storage_key=storage_key,
            mime_type=mime_type,
            width=width,
            height=height,
        )
        db.add(media)
        db.flush()
        if set_as_profile:
            avatar.profile_media_id = media.id
        db.commit()
    except Exception:
        db.rollback()
        try:
            delete_object(storage_key)
        except Exception:
            pass
        raise
    db.refresh(media)
    return media


@router.get("", response_model=list[AvatarMediaResponse])
def list_avatar_media(
    avatar_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AvatarMedia]:
    get_owned_avatar(avatar_id, user, db)
    return list(
        db.scalars(
            select(AvatarMedia)
            .where(AvatarMedia.avatar_id == avatar_id)
            .order_by(AvatarMedia.created_at.desc())
        )
    )


@router.get("/{media_id}", response_model=AvatarMediaResponse)
def read_avatar_media(
    avatar_id: uuid.UUID,
    media_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarMedia:
    return get_owned_media(avatar_id, media_id, user, db)


@router.patch("/{media_id}", response_model=AvatarMediaResponse)
def update_avatar_media(
    avatar_id: uuid.UUID,
    media_id: uuid.UUID,
    payload: AvatarMediaUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarMedia:
    media = get_owned_media(avatar_id, media_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(media, field, value)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar_media(
    avatar_id: uuid.UUID,
    media_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    avatar = get_owned_avatar(avatar_id, user, db)
    media = get_owned_media(avatar_id, media_id, user, db)
    if avatar.profile_media_id == media.id:
        avatar.profile_media_id = None
        db.flush()
    storage_key = media.storage_key
    db.delete(media)
    db.commit()
    delete_object(storage_key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
