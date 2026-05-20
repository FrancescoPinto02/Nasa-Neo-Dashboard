from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    app_name: str = "NASA NEO Dashboard API"
    app_version: str = "0.1.0"
    app_env: Literal["local", "test", "production"] = "local"
    app_debug: bool = True

    nasa_api_key: str = "DEMO_KEY"
    nasa_neows_base_url: str = "https://api.nasa.gov/neo/rest/v1"
    nasa_request_timeout_seconds: float = 10.0

    nasa_max_chunk_days: int = 7
    app_max_query_range_days: int = 90

    cache_backend: Literal["disk", "redis"] = "disk"
    cache_ttl_seconds: int = 21_600
    cache_disk_directory: str = ".cache/nasa-neo"

    log_level: str = "INFO"
    log_json: bool = False

    redis_url: str = "redis://localhost:6379/0"

    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: Any) -> list[str]:
        """Parse CORS origins from either a comma-separated string or a list."""

        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]

        if isinstance(value, list):
            return value

        return ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    Caching avoids reparsing environment variables on every request.
    """
    return Settings()