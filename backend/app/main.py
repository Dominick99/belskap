from fastapi import FastAPI

from app.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.avatar_media import router as avatar_media_router
from app.routers.avatars import router as avatars_router


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.include_router(avatars_router)
app.include_router(avatar_media_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
