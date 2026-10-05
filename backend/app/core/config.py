from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables prefixed with VOTELY_."""

    model_config = SettingsConfigDict(env_prefix="VOTELY_", env_file=".env", extra="ignore")

    app_name: str = "votely"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://votely:votely@localhost:5432/votely"

    # No default on purpose: the application refuses to start without a strong signing key
    # (HS256 needs at least 32 bytes, RFC 7518).
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_ttl_minutes: int = 60
    # Only disable for local development over plain HTTP.
    cookie_secure: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
