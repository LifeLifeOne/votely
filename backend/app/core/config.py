from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables prefixed with VOTELY_."""

    model_config = SettingsConfigDict(env_prefix="VOTELY_", env_file=".env", extra="ignore")

    app_name: str = "votely"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://votely:votely@localhost:5432/votely"


@lru_cache
def get_settings() -> Settings:
    return Settings()
