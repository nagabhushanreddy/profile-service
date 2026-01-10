"""Health check routes."""

from datetime import datetime

from fastapi import APIRouter

from app.config import config
from app.models.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=config.service.name,
        version=config.service.version
    )


@router.get("/healthz", response_model=HealthResponse)
async def healthz():
    """Kubernetes liveness probe."""
    return HealthResponse(
        status="healthy",
        service=config.service.name,
        version=config.service.version
    )
