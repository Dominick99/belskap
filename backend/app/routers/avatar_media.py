import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Avatar, AvatarMedia, User
from app.schemas import AvatarMediaCreate, AvatarMediaResponse, AvatarMediaUpdate


router = APIRouter(prefix="/api/v1/avatars/{avatar_id}/media", tags=["avatar media"])


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
    db.delete(media)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
