"""API v1 router configuration.

This module aggregates all v1 endpoints and provides the main APIRouter for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import extract, translate

api_router = APIRouter()

# Include extract endpoint
api_router.include_router(
    extract.router,
    prefix="/extract",
    tags=["extraction"],
)

# Include translate endpoint
api_router.include_router(
    translate.router,
    prefix="/translate",
    tags=["translation"],
)
