from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Avatar, AvatarMedia, User
from app.storage import get_object


router = APIRouter(prefix="/api/v1/media", tags=["avatar media"])


@router.get("/content")
def read_media_content(
    key: str = Query(min_length=1, max_length=1024),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    media = db.scalar(
        select(AvatarMedia)
        .join(Avatar, AvatarMedia.avatar_id == Avatar.id)
        .where(AvatarMedia.storage_key == key, Avatar.user_id == user.id)
    )
    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found.")
    stored = get_object(key)
    return StreamingResponse(
        stored["Body"].iter_chunks(chunk_size=64 * 1024),
        media_type=media.mime_type or "application/octet-stream",
        headers={"Cache-Control": "private, max-age=3600"},
    )
