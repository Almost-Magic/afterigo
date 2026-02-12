"""Ripple CRM — Health check endpoint."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ripple-crm",
        "version": settings.app_version,
    }
