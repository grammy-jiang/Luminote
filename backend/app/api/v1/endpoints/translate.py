"""Translation API endpoint.

This module provides the POST /api/v1/translate endpoint for translating content blocks.
"""

import time

from fastapi import APIRouter, Request

from app.schemas.translation import (
    TranslatedBlock,
    TranslationMetadata,
    TranslationRequest,
    TranslationResponse,
)
from app.services.translation_service import TranslationService

router = APIRouter()
translation_service = TranslationService()


@router.post("/", response_model=TranslationResponse)
async def translate_content(
    request: Request, translation_request: TranslationRequest
) -> TranslationResponse:
    """Translate content blocks to target language.

    This endpoint accepts an array of content blocks and returns translated versions
    using the specified AI provider (OpenAI, Anthropic).

    Args:
        request: FastAPI request object (provides request_id)
        translation_request: Translation request with content blocks and parameters

    Returns:
        TranslationResponse with translated blocks and metadata

    Raises:
        HTTPException: On validation or processing errors (handled by middleware)
    """
    start_time = time.perf_counter()

    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")

    # Translate blocks using the translation service
    translated_blocks = await translation_service.translate_blocks(
        blocks=translation_request.content_blocks,
        target_language=translation_request.target_language,
        provider=translation_request.provider,
        model=translation_request.model,
        api_key=translation_request.api_key,
    )

    # Convert to TranslatedBlock schema
    response_blocks = [
        TranslatedBlock(
            id=block.id,
            type=block.type,
            text=block.text,
            metadata=block.metadata,
        )
        for block in translated_blocks
    ]

    processing_time = time.perf_counter() - start_time

    return TranslationResponse(
        success=True,
        data={"translated_blocks": response_blocks},
        metadata=TranslationMetadata(
            request_id=request_id,
            processing_time=processing_time,
        ),
    )
