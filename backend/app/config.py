from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Belskap API"
    database_url: str = Field(
        default="postgresql+psycopg://belskap:belskap@localhost:5432/belskap",
        validation_alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
