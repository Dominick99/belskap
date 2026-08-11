import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Avatar, User
from app.schemas import AvatarCreate, AvatarResponse, AvatarUpdate


router = APIRouter(prefix="/api/v1/avatars", tags=["avatars"])


def get_owned_avatar(avatar_id: uuid.UUID, user: User, db: Session) -> Avatar:
    avatar = db.scalar(
        select(Avatar).where(Avatar.id == avatar_id, Avatar.user_id == user.id)
    )
    if avatar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found.",
        )
    return avatar


@router.post("", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
def create_avatar(
    payload: AvatarCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Avatar:
    avatar = Avatar(user_id=user.id, **payload.model_dump())
    db.add(avatar)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an avatar with this slug.",
        ) from None
    db.refresh(avatar)
    return avatar


@router.get("", response_model=list[AvatarResponse])
def list_avatars(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Avatar]:
    return list(
        db.scalars(
            select(Avatar)
            .where(Avatar.user_id == user.id)
            .order_by(Avatar.created_at.desc())
        )
    )


@router.get("/{avatar_id}", response_model=AvatarResponse)
def read_avatar(
    avatar_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Avatar:
    return get_owned_avatar(avatar_id, user, db)


@router.patch("/{avatar_id}", response_model=AvatarResponse)
def update_avatar(
    avatar_id: uuid.UUID,
    payload: AvatarUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Avatar:
    avatar = get_owned_avatar(avatar_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(avatar, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an avatar with this slug.",
        ) from None
    db.refresh(avatar)
    return avatar


@router.delete("/{avatar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(
    avatar_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    avatar = get_owned_avatar(avatar_id, user, db)
    db.delete(avatar)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
