from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Belskap API"
    database_url: str = Field(
        default="postgresql+psycopg://belskap:belskap@localhost:5432/belskap",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(
        default="development-only-secret-change-me",
        validation_alias="JWT_SECRET",
    )
    access_token_minutes: int = 60 * 24
    s3_endpoint_url: str | None = Field(default=None, validation_alias="S3_ENDPOINT_URL")
    s3_access_key: str = Field(default="minioadmin", validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", validation_alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="belskap-media", validation_alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", validation_alias="S3_REGION")
    frontend_url: str = Field(
        default="http://localhost:3000", validation_alias="FRONTEND_URL"
    )
    stripe_secret_key: str | None = Field(
        default=None, validation_alias="STRIPE_SECRET_KEY"
    )
    stripe_webhook_secret: str | None = Field(
        default=None, validation_alias="STRIPE_WEBHOOK_SECRET"
    )
    stripe_starter_price_id: str | None = Field(
        default=None, validation_alias="STRIPE_STARTER_PRICE_ID"
    )
    stripe_starter_credits: int = Field(
        default=1000, gt=0, validation_alias="STRIPE_STARTER_CREDITS"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
