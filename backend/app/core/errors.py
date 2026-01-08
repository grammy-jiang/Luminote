"""
Custom exception classes for Luminote.

This module defines the exception hierarchy following ADR-004.
"""

from typing import Any


class LuminoteException(Exception):
    """Base exception for all Luminote errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a Luminote exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ClientError(LuminoteException):
    """Base class for client errors (4xx)."""

    def __init__(
        self, message: str, code: str, details: dict[str, Any] | None = None
    ) -> None:
        """Initialize a client error."""
        super().__init__(message, code, status_code=400, details=details)


class InvalidURLError(ClientError):
    """Invalid URL format."""

    def __init__(self, url: str) -> None:
        """Initialize an invalid URL error."""
        super().__init__(
            message=f"Invalid URL format: {url}",
            code="INVALID_URL",
            details={"url": url},
        )


class ValidationError(ClientError):
    """Request validation failed."""

    def __init__(self, field: str, reason: str) -> None:
        """Initialize a validation error."""
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            code="VALIDATION_ERROR",
            details={"field": field, "reason": reason},
        )


class ServerError(LuminoteException):
    """Base class for server errors (5xx)."""

    def __init__(
        self, message: str, code: str, details: dict[str, Any] | None = None
    ) -> None:
        """Initialize a server error."""
        super().__init__(message, code, status_code=500, details=details)


class ExternalServiceError(ServerError):
    """External service error."""

    def __init__(self, service: str, reason: str) -> None:
        """Initialize an external service error."""
        super().__init__(
            message=f"External service '{service}' error: {reason}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "reason": reason},
        )


class ExtractionError(ClientError):
    """Content extraction failed."""

    def __init__(self, url: str, reason: str) -> None:
        """Initialize an extraction error."""
        super().__init__(
            message=f"Failed to extract content from {url}: {reason}",
            code="EXTRACTION_ERROR",
            details={"url": url, "reason": reason},
        )
        self.status_code = 422  # Override default 400 status


class APIKeyError(ClientError):
    """API key validation or authentication error."""

    def __init__(
        self, provider: str, reason: str = "Invalid or missing API key"
    ) -> None:
        """Initialize an API key error."""
        super().__init__(
            message=f"API key error for {provider}: {reason}",
            code="API_KEY_ERROR",
            details={"provider": provider, "reason": reason},
        )
        self.status_code = 401  # Override default 400 status


class RateLimitError(ClientError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int, provider: str | None = None) -> None:
        """Initialize a rate limit error."""
        message = f"Rate limit exceeded. Retry after {retry_after} seconds."
        if provider:
            message += f" (Provider: {provider})"
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after, "provider": provider},
        )
        self.status_code = 429  # Override default 400 status


class TranslationError(ServerError):
    """Translation failed."""

    def __init__(self, provider: str, model: str, reason: str) -> None:
        """Initialize a translation error."""
        super().__init__(
            message=f"Translation failed using {provider}/{model}: {reason}",
            code="TRANSLATION_ERROR",
            details={"provider": provider, "model": model, "reason": reason},
        )
