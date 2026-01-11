"""Config validation API endpoint.

This module provides the POST /api/v1/config/validate endpoint for validating
API keys and retrieving model capabilities.
"""

from fastapi import APIRouter, Request

from app.core.errors import LuminoteException
from app.core.logging import logger
from app.schemas.config import (
    ConfigValidationRequest,
    ConfigValidationResponse,
    ModelCapabilities,
)
from app.services.translation_service import ProviderFactory

router = APIRouter()


@router.post("/validate", response_model=ConfigValidationResponse)
async def validate_config(
    request: Request, config_request: ConfigValidationRequest
) -> ConfigValidationResponse:
    """Validate API configuration and retrieve model capabilities.

    This endpoint makes a minimal test API call to verify the API key is valid
    and retrieves the model's capabilities (streaming support, max tokens).
    Uses a minimal prompt to avoid charging the user significant costs.

    Args:
        request: FastAPI request object (provides request_id)
        config_request: Configuration validation request with provider, model, and API key

    Returns:
        ConfigValidationResponse with validation result and model capabilities

    Raises:
        HTTPException: On validation or processing errors (handled by middleware)
            - 401: Invalid or expired API key
            - 429: Rate limit exceeded
            - 504: Timeout after 10 seconds
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.info(
        "Validating API configuration",
        extra={
            "request_id": request_id,
            "provider": config_request.provider,
            "model": config_request.model,
        },
    )

    try:
        # Get the provider instance
        provider = ProviderFactory.get_provider(config_request.provider)

        # Validate configuration (makes minimal test API call)
        validation_result = await provider.validate(
            model=config_request.model,
            api_key=config_request.api_key,
        )

        # Convert to response format
        response = ConfigValidationResponse(
            valid=validation_result.valid,
            provider=validation_result.provider,
            model=validation_result.model,
            capabilities=ModelCapabilities(
                streaming=validation_result.capabilities.streaming,
                max_tokens=validation_result.capabilities.max_tokens,
            ),
            details={},
        )

        logger.info(
            "API configuration validated successfully",
            extra={
                "request_id": request_id,
                "provider": config_request.provider,
                "model": config_request.model,
                "valid": response.valid,
            },
        )

        return response

    except LuminoteException as e:
        # Log the validation failure
        logger.warning(
            "API configuration validation failed",
            extra={
                "request_id": request_id,
                "provider": config_request.provider,
                "model": config_request.model,
                "error_code": e.code,
                "error_message": e.message,
            },
        )
        # Re-raise to be handled by exception middleware
        raise
