from pydantic import BaseModel
from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        version=settings.app_version,
    )