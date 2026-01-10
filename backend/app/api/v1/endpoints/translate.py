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
        - Block translation (no event field, default message):
          data: {"block_id": "1", "translation": "...", "tokens_used": 50}

        - Error event (uses event: error):
          event: error
          data: {"code": "...", "message": "...", "block_id": "..."}

        - Done event (uses event: done):
          event: done
          data: {"total_tokens": 95, "processing_time": 12.5, "blocks_translated": 2, "blocks_failed": 0}

    Error Handling:
        - Per-block errors are isolated - stream continues with remaining blocks
        - Each block has 120s timeout using asyncio.wait_for
        - Client disconnections are detected and handled gracefully

    Raises:
        HTTPException: On validation or processing errors (handled by middleware)
    """
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = time.perf_counter()

    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events for translation progress.

        Yields:
            SSE-formatted strings using proper SSE format with event: lines
        """
        total_tokens = 0
        translated_count = 0
        failed_count = 0
        timeout_seconds = 120  # 2 minute timeout per block

        try:
            for block in translation_request.content_blocks:
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
                    # Translate single block with timeout
                    translated_block = await asyncio.wait_for(
                        translation_service.translate_block(
                            block=block,
                            target_language=translation_request.target_language,
                            provider=translation_request.provider,
                            model=translation_request.model,
                            api_key=translation_request.api_key,
                        ),
                        timeout=timeout_seconds,
                    )

                    # Extract tokens used from metadata
                    tokens_used = translated_block.metadata.get("tokens_used", 0)
                    total_tokens += tokens_used

                    # Create block event (using data-only format)
                    block_event = {
                        "block_id": translated_block.id,
                        "translation": translated_block.text,
                        "tokens_used": tokens_used,
                    }

                    yield f"data: {json.dumps(block_event)}\n\n"
                    translated_count += 1

                except TimeoutError:
                    # Send error event for timeout (per-block error, continue with next)
                    error_data = {
                        "code": "TIMEOUT",
                        "message": f"Translation timed out after {timeout_seconds}s",
                        "block_id": block.id,
                    }
                    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                    failed_count += 1
                    logger.warning(
                        f"Translation timed out for block {block.id}",
                        extra={
                            "request_id": request_id,
                            "block_id": block.id,
                            "timeout_seconds": timeout_seconds,
                        },
                    )
                    # Continue with next block

                except LuminoteException as e:
                    # Send error event for this specific block, then continue
                    error_data = {
                        "code": e.code,
                        "message": e.message,
                        "block_id": block.id,
                    }
                    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                    failed_count += 1
                    logger.error(
                        f"Translation failed for block {block.id}",
                        extra={
                            "request_id": request_id,
                            "block_id": block.id,
                            "error_code": e.code,
                        },
                    )
                    # Continue with next block (per-block error isolation)

            # All blocks processed (some may have failed) - send done event
            processing_time = time.perf_counter() - start_time
            done_data = {
                "total_tokens": total_tokens,
                "processing_time": round(processing_time, 2),
                "blocks_translated": translated_count,
                "blocks_failed": failed_count,
            }
            yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

            logger.info(
                "Translation stream completed",
                extra={
                    "request_id": request_id,
                    "blocks_translated": translated_count,
                    "blocks_failed": failed_count,
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
            # Unexpected error - send error event and terminate
            error_data = {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during translation",
            }
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
            logger.exception(
                "Unexpected error in translation stream",
                extra={"request_id": request_id, "translated_blocks": translated_count},
            )
            return

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
