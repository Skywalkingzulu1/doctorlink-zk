"""DoctorLink Health Services API package."""

from fastapi import APIRouter
from .v1.endpoints import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/api/v1")

__all__ = ["api_router"]