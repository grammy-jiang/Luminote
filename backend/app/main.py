"""
Luminote FastAPI application entry point.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app
from app.config import get_settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    # Startup
    setup_logging()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    fastapi_app = FastAPI(
        title="Luminote API",
        version=app.__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app


fastapi_application = create_app()


@fastapi_application.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": app.__version__}


def main() -> None:
    """Entry point for CLI command."""
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.main:fastapi_application",
        host=settings.DEV_HOST,
        port=settings.DEV_PORT,
        reload=settings.DEV_RELOAD,
        log_level="info",
    )


if __name__ == "__main__":
    main()
