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

router = APIRouter()


@router.post("/", response_model=TranslationResponse)
async def translate_content(
    request: Request, translation_request: TranslationRequest
) -> TranslationResponse:
    """Translate content blocks to target language.

    This endpoint accepts an array of content blocks and returns translated versions.
    Currently returns mock translations (prefixed with [TRANSLATED]) until Issue 1.2
    implements the actual TranslationService.

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

    # Mock translation service - Issue 1.2 will implement actual translation
    translated_blocks = []
    for block in translation_request.content_blocks:
        translated_blocks.append(
            TranslatedBlock(
                id=block.id,
                type=block.type,
                text=f"[TRANSLATED] {block.text}",
                metadata={
                    "provider": translation_request.provider,
                    "model": translation_request.model,
                },
            )
        )

    processing_time = time.perf_counter() - start_time

    return TranslationResponse(
        success=True,
        data={"translated_blocks": translated_blocks},
        metadata=TranslationMetadata(
            request_id=request_id,
            processing_time=processing_time,
        ),
    )
