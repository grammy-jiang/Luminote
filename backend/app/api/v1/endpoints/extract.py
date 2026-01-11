"""Content extraction API endpoint.

This module provides the POST /api/v1/extract endpoint for extracting content from URLs.
"""

import time

from fastapi import APIRouter, Request

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
from app.core.logging import get_logger
from app.schemas.extraction import (
    ExtractionMetadata,
    ExtractionRequest,
    ExtractionResponse,
    ExtractionResponseData,
)
from app.services.caching_service import CachingService
from app.services.extraction_service import ExtractionService

logger = get_logger(__name__)

router = APIRouter()
extraction_service = ExtractionService()
caching_service = CachingService()


@router.post("/", response_model=ExtractionResponse)
async def extract_content(
    request: Request, extraction_request: ExtractionRequest
) -> ExtractionResponse:
    """Extract structured content from a URL.

    This endpoint accepts a URL and returns the extracted, structured content
    using Mozilla Readability and BeautifulSoup for content parsing.

    Content is cached for 24 hours to reduce extraction API calls and improve
    performance.

    Args:
        request: FastAPI request object (provides request_id)
        extraction_request: Extraction request with URL

    Returns:
        ExtractionResponse with extracted content blocks and metadata

    Raises:
        LuminoteException subclasses (handled by exception middleware), including:
            - InvalidURLError: URL format is invalid
            - URLFetchError: Network error, unreachable host, or non-200 response
            - ExtractionError: Content extraction failed
    """
    start_time = time.perf_counter()

    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")

    # Check cache first
    cached_content = caching_service.get(extraction_request.url)

    if cached_content is not None:
        logger.info(
            "Cache hit for extraction",
            extra={"url": extraction_request.url, "request_id": request_id},
        )
        extracted_content = cached_content
        cache_hit = True
    else:
        logger.info(
            "Cache miss for extraction - fetching content",
            extra={"url": extraction_request.url, "request_id": request_id},
        )
        # Extract content using the extraction service
        try:
            extracted_content = await extraction_service.extract(extraction_request.url)
            # Cache the extracted content
            caching_service.set(extraction_request.url, extracted_content)
            cache_hit = False
        except (InvalidURLError, URLFetchError, ExtractionError):
            # Re-raise service exceptions as-is - they have proper status codes
            raise

    processing_time = time.perf_counter() - start_time

    # Build response data
    response_data = ExtractionResponseData(
        url=extracted_content.url,
        title=extracted_content.title,
        author=extracted_content.author,
        date_published=extracted_content.date_published,
        content_blocks=extracted_content.content_blocks,
        metadata={
            **extracted_content.metadata,
            "extraction_method": "readability",
            "block_count": len(extracted_content.content_blocks),
            "cache_hit": cache_hit,
        },
    )

    return ExtractionResponse(
        success=True,
        data=response_data,
        metadata=ExtractionMetadata(
            request_id=request_id,
            processing_time=processing_time,
        ),
    )
