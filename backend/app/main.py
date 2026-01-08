"""
Luminote FastAPI application entry point.
"""

import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app
from app.config import get_settings
from app.core.errors import LuminoteException
from app.core.logging import logger, setup_logging


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

    # Add request ID middleware
    @fastapi_app.middleware("http")
    async def add_request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Add unique request ID to each request."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Register exception handlers
    @fastapi_app.exception_handler(LuminoteException)
    async def luminote_exception_handler(
        request: Request, exc: LuminoteException
    ) -> JSONResponse:
        """Handle all Luminote custom exceptions."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        # Log error with context - only include stack trace for server errors (5xx)
        logger.error(
            f"Error handling request {request_id}",
            extra={
                "request_id": request_id,
                "error_code": exc.code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=exc.status_code >= 500,
        )

        # Prepare response headers
        headers = {"X-Request-ID": request_id}

        # Add Retry-After header for rate limit errors (RFC 7231)
        if exc.code == "RATE_LIMIT_EXCEEDED" and "retry_after" in exc.details:
            headers["Retry-After"] = str(exc.details["retry_after"])

        # Return user-friendly response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "code": exc.code,
                "details": exc.details,
                "request_id": request_id,
            },
            headers=headers,
        )

    @fastapi_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        # Format validation errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({"field": field, "message": error["msg"]})

        logger.warning(
            f"Validation error in request {request_id}",
            extra={
                "request_id": request_id,
                "errors": errors,
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": {"errors": errors},
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    @fastapi_app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        logger.exception(
            f"Unhandled exception in request {request_id}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "An unexpected error occurred",
                "code": "INTERNAL_ERROR",
                "details": {},
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
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
