"""Content extraction API endpoint.

This module provides the POST /api/v1/extract endpoint for extracting content from URLs.
"""

import time

from fastapi import APIRouter, Request

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
from app.schemas.extraction import (
    ExtractionMetadata,
    ExtractionRequest,
    ExtractionResponse,
    ExtractionResponseData,
)
from app.services.extraction_service import ExtractionService

router = APIRouter()
extraction_service = ExtractionService()


@router.post("/", response_model=ExtractionResponse)
async def extract_content(
    request: Request, extraction_request: ExtractionRequest
) -> ExtractionResponse:
    """Extract structured content from a URL.

    This endpoint accepts a URL and returns the extracted, structured content
    using Mozilla Readability and BeautifulSoup for content parsing.

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

    # Extract content using the extraction service
    try:
        extracted_content = await extraction_service.extract(extraction_request.url)
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
