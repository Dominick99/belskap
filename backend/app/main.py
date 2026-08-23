from fastapi import FastAPI

from app.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.avatar_media import router as avatar_media_router
from app.routers.avatars import profile_router, router as avatars_router
from app.routers.media_files import router as media_files_router
from app.routers.credits import router as credits_router
from app.routers.billing import router as billing_router


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.include_router(avatars_router)
app.include_router(profile_router)
app.include_router(avatar_media_router)
app.include_router(media_files_router)
app.include_router(credits_router)
app.include_router(billing_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
