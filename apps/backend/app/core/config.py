from functools import lru_cache
from typing import Any, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NASA NEO Dashboard API"
    app_version: str = "0.1.0"
    app_env: Literal["local", "test", "production"] = "local"
    app_debug: bool = True

    nasa_api_key: str = "DEMO_KEY"
    nasa_neows_base_url: AnyHttpUrl = AnyHttpUrl("https://api.nasa.gov/neo/rest/v1")

    cache_backend: Literal["disk", "redis"] = "disk"
    cache_ttl_seconds: int = 21_600
    redis_url: str = "redis://localhost:6379/0"

    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: Any) -> list[str]:
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
    return Settings()