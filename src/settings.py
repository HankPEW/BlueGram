from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.database.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER
)


class Settings(BaseSettings):
    """Конфигурация приложения и окружения."""

    app_name: str = "BlueGram"

    database_url: str = Field(
        default=(
            f"postgresql+asyncpg://"
            f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
            f"{POSTGRES_PORT}/{POSTGRES_DB}"
        ),
        alias="DATABASE_URL"
    )

    jwt_secret_key: str = Field(
        default="super-duper-secret",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = "HS256"

    access_token_expires_minutes: int = 15
    refresh_token_expires_minutes: int = 60 * 24 * 30

    session_cookie_secure: bool = False
    session_cookie_domain: str | None = None

    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()