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
        HTTPException: On validation or processing errors (handled by middleware)
            - 400 (INVALID_URL): URL format is invalid
            - 404 (URL_NOT_FOUND): URL returns 404
            - 422 (EXTRACTION_FAILED): Content extraction failed
            - 502 (URL_UNREACHABLE): Network error or unreachable host
            - 504 (REQUEST_TIMEOUT): Request timed out
    """
    start_time = time.perf_counter()

    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")

    # Extract content using the extraction service
    try:
        extracted_content = await extraction_service.extract(extraction_request.url)
    except InvalidURLError as e:
        # Re-raise with proper error code - will be caught by exception handler
        raise e
    except URLFetchError as e:
        # Check if it's a 404 error
        if "404" in e.details.get("reason", ""):
            # Create a new URLFetchError with 404 status
            raise URLFetchError(
                url=e.details.get("url", extraction_request.url),
                reason="URL not found",
                status_code=404,
            ) from e
        # Re-raise other fetch errors as-is (502/504)
        raise e
    except ExtractionError as e:
        # Re-raise extraction errors as-is (422)
        raise e

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
