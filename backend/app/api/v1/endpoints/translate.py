"""Translation API endpoint.

This module provides the POST /api/v1/translate endpoint for translating content blocks.
"""

import asyncio
import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.errors import LuminoteException
from app.core.logging import logger
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


@router.post("/stream")
async def stream_translation(
    request: Request, translation_request: TranslationRequest
) -> StreamingResponse:
    """Stream translation results block-by-block using Server-Sent Events.

    This endpoint accepts the same request format as the regular /translate endpoint,
    but streams results progressively as each block is translated. This provides
    better user experience for long documents by showing results immediately.

    Args:
        request: FastAPI request object (provides request_id)
        translation_request: Translation request with content blocks and parameters

    Returns:
        StreamingResponse with text/event-stream content type

    SSE Event Format:
        - Block translation: data: {"type": "block", "block_id": "1", ...}
        - Done event: data: {"type": "done", "total_tokens": 95, ...}
        - Error event: data: {"type": "error", "code": "...", "message": "..."}

    Raises:
        HTTPException: On validation or processing errors (handled by middleware)
    """
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = time.perf_counter()

    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events for translation progress.

        Yields:
            SSE-formatted strings (data: {...}\\n\\n)
        """
        total_tokens = 0
        translated_count = 0
        last_activity = time.perf_counter()
        timeout_seconds = 120  # 2 minute inactivity timeout

        try:
            for block in translation_request.content_blocks:
                # Check for inactivity timeout
                if time.perf_counter() - last_activity > timeout_seconds:
                    error_event = {
                        "type": "error",
                        "code": "TIMEOUT",
                        "message": "Translation timed out due to inactivity",
                        "block_id": block.id,
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
                    logger.warning(
                        f"Translation stream timed out after {timeout_seconds}s",
                        extra={"request_id": request_id, "block_id": block.id},
                    )
                    return

                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(
                        "Client disconnected during streaming translation",
                        extra={
                            "request_id": request_id,
                            "translated_blocks": translated_count,
                            "total_blocks": len(translation_request.content_blocks),
                        },
                    )
                    return

                try:
                    # Translate single block
                    translated_block = await translation_service.translate_block(
                        block=block,
                        target_language=translation_request.target_language,
                        provider=translation_request.provider,
                        model=translation_request.model,
                        api_key=translation_request.api_key,
                    )

                    # Extract tokens used from metadata
                    tokens_used = translated_block.metadata.get("tokens_used", 0)
                    total_tokens += tokens_used

                    # Create block event
                    block_event = {
                        "type": "block",
                        "block_id": translated_block.id,
                        "translation": translated_block.text,
                        "tokens_used": tokens_used,
                    }

                    yield f"data: {json.dumps(block_event)}\n\n"
                    translated_count += 1
                    last_activity = time.perf_counter()

                except LuminoteException as e:
                    # Send error event for this specific block
                    error_event = {
                        "type": "error",
                        "code": e.code,
                        "message": e.message,
                        "block_id": block.id,
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
                    logger.error(
                        f"Translation failed for block {block.id}",
                        extra={
                            "request_id": request_id,
                            "block_id": block.id,
                            "error_code": e.code,
                        },
                    )
                    return

            # All blocks processed successfully - send done event
            processing_time = time.perf_counter() - start_time
            done_event = {
                "type": "done",
                "total_tokens": total_tokens,
                "processing_time": round(processing_time, 2),
            }
            yield f"data: {json.dumps(done_event)}\n\n"

            logger.info(
                "Translation stream completed successfully",
                extra={
                    "request_id": request_id,
                    "blocks_translated": translated_count,
                    "total_tokens": total_tokens,
                    "processing_time": round(processing_time, 2),
                },
            )

        except asyncio.CancelledError:
            # Client disconnected or request cancelled
            logger.info(
                "Translation stream cancelled",
                extra={"request_id": request_id, "translated_blocks": translated_count},
            )
            raise

        except Exception:
            # Unexpected error - send error event
            error_event = {
                "type": "error",
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during translation",
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            logger.exception(
                "Unexpected error in translation stream",
                extra={"request_id": request_id, "translated_blocks": translated_count},
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for real-time delivery
            "Connection": "keep-alive",
            "X-Request-ID": request_id,
        },
    )
