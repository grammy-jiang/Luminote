"""Tests for extraction API endpoint."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
from app.schemas.extraction import ContentBlock, ExtractedContent


@pytest.mark.unit
def test_extract_success(client: TestClient) -> None:
    """Test successful content extraction request."""
    # Arrange
    request_data = {"url": "https://example.com/article"}

    # Mock the extraction service
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.return_value = ExtractedContent(
            url="https://example.com/article",
            title="Test Article",
            author="John Doe",
            date_published="2026-01-08",
            content_blocks=[
                ContentBlock(
                    id="block-1",
                    type="heading",
                    text="Main Heading",
                    metadata={"level": 1},
                ),
                ContentBlock(
                    id="block-2",
                    type="paragraph",
                    text="This is a test paragraph.",
                    metadata={},
                ),
            ],
            metadata={"extraction_method": "readability"},
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data

    # Check extracted data
    extracted_data = data["data"]
    assert extracted_data["url"] == "https://example.com/article"
    assert extracted_data["title"] == "Test Article"
    assert extracted_data["author"] == "John Doe"
    assert extracted_data["date_published"] == "2026-01-08"

    # Check content blocks
    content_blocks = extracted_data["content_blocks"]
    assert len(content_blocks) == 2
    assert content_blocks[0]["id"] == "block-1"
    assert content_blocks[0]["type"] == "heading"
    assert content_blocks[0]["text"] == "Main Heading"
    assert content_blocks[0]["metadata"]["level"] == 1

    assert content_blocks[1]["id"] == "block-2"
    assert content_blocks[1]["type"] == "paragraph"
    assert content_blocks[1]["text"] == "This is a test paragraph."

    # Check metadata
    assert extracted_data["metadata"]["extraction_method"] == "readability"
    assert extracted_data["metadata"]["block_count"] == 2

    # Check response metadata
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]
    assert "processing_time" in data["metadata"]
    assert data["metadata"]["processing_time"] >= 0

    # Check headers
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time" in response.headers


@pytest.mark.unit
def test_extract_missing_url(client: TestClient) -> None:
    """Test extraction request with missing url field."""
    # Arrange
    request_data = {}

    # Act
    response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "url" in str(data).lower()


@pytest.mark.unit
def test_extract_empty_url(client: TestClient) -> None:
    """Test extraction request with empty url."""
    # Arrange
    request_data = {"url": ""}

    # Act
    response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_extract_invalid_url_format(client: TestClient) -> None:
    """Test extraction with invalid URL format."""
    # Arrange
    request_data = {"url": "not-a-valid-url"}

    # Mock the extraction service to raise InvalidURLError
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.side_effect = InvalidURLError(url="not-a-valid-url")

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_URL"
    assert "request_id" in data
    assert "not-a-valid-url" in data["error"]


@pytest.mark.unit
def test_extract_url_not_found(client: TestClient) -> None:
    """Test extraction with URL that returns 404."""
    # Arrange
    request_data = {"url": "https://example.com/nonexistent"}

    # Mock the extraction service to raise URLFetchError with 404
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.side_effect = URLFetchError(
            url="https://example.com/nonexistent",
            reason="HTTP 404",
            status_code=404,
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "URL_FETCH_ERROR"
    assert "request_id" in data


@pytest.mark.unit
def test_extract_url_timeout(client: TestClient) -> None:
    """Test extraction with URL that times out."""
    # Arrange
    request_data = {"url": "https://example.com/slow"}

    # Mock the extraction service to raise URLFetchError with timeout
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.side_effect = URLFetchError(
            url="https://example.com/slow",
            reason="Request timeout",
            status_code=504,
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 504
    data = response.json()
    assert data["code"] == "URL_FETCH_ERROR"
    assert "request_id" in data
    assert "timeout" in data["error"].lower()


@pytest.mark.unit
def test_extract_url_unreachable(client: TestClient) -> None:
    """Test extraction with unreachable URL."""
    # Arrange
    request_data = {"url": "https://unreachable.example.com"}

    # Mock the extraction service to raise URLFetchError for unreachable host
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.side_effect = URLFetchError(
            url="https://unreachable.example.com",
            reason="Network error (unreachable host)",
            status_code=502,
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 502
    data = response.json()
    assert data["code"] == "URL_FETCH_ERROR"
    assert "request_id" in data
    assert "unreachable" in data["error"].lower() or "network" in data["error"].lower()


@pytest.mark.unit
def test_extract_extraction_failed(client: TestClient) -> None:
    """Test extraction failure during content parsing."""
    # Arrange
    request_data = {"url": "https://example.com/unparseable"}

    # Mock the extraction service to raise ExtractionError
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.side_effect = ExtractionError(
            url="https://example.com/unparseable",
            reason="No content blocks extracted",
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "EXTRACTION_ERROR"
    assert "request_id" in data
    assert "extraction" in data["error"].lower() or "content" in data["error"].lower()


@pytest.mark.unit
def test_extract_no_author_or_date(client: TestClient) -> None:
    """Test successful extraction without author or date."""
    # Arrange
    request_data = {"url": "https://example.com/article"}

    # Mock the extraction service with no author/date
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.return_value = ExtractedContent(
            url="https://example.com/article",
            title="Article Without Metadata",
            author=None,
            date_published=None,
            content_blocks=[
                ContentBlock(
                    id="block-1",
                    type="paragraph",
                    text="Content without metadata.",
                    metadata={},
                )
            ],
            metadata={},
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["author"] is None
    assert data["data"]["date_published"] is None
    assert len(data["data"]["content_blocks"]) == 1


@pytest.mark.unit
def test_extract_multiple_block_types(client: TestClient) -> None:
    """Test extraction with various content block types."""
    # Arrange
    request_data = {"url": "https://example.com/article"}

    # Mock the extraction service with multiple block types
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.return_value = ExtractedContent(
            url="https://example.com/article",
            title="Comprehensive Article",
            author="Jane Smith",
            date_published="2026-01-09",
            content_blocks=[
                ContentBlock(
                    id="block-1", type="heading", text="Title", metadata={"level": 1}
                ),
                ContentBlock(
                    id="block-2", type="paragraph", text="Intro paragraph", metadata={}
                ),
                ContentBlock(
                    id="block-3", type="list", text="Item 1\nItem 2", metadata={}
                ),
                ContentBlock(
                    id="block-4", type="quote", text="A famous quote", metadata={}
                ),
                ContentBlock(
                    id="block-5",
                    type="code",
                    text="print('hello')",
                    metadata={"language": "python"},
                ),
                ContentBlock(
                    id="block-6",
                    type="image",
                    text="Image alt text",
                    metadata={"src": "https://example.com/image.jpg"},
                ),
            ],
            metadata={},
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    content_blocks = data["data"]["content_blocks"]
    assert len(content_blocks) == 6
    assert content_blocks[0]["type"] == "heading"
    assert content_blocks[1]["type"] == "paragraph"
    assert content_blocks[2]["type"] == "list"
    assert content_blocks[3]["type"] == "quote"
    assert content_blocks[4]["type"] == "code"
    assert content_blocks[5]["type"] == "image"

    # Verify block_count in metadata
    assert data["data"]["metadata"]["block_count"] == 6


@pytest.mark.unit
def test_extract_preserves_metadata(client: TestClient) -> None:
    """Test that extraction preserves metadata from service."""
    # Arrange
    request_data = {"url": "https://example.com/article"}

    # Mock the extraction service with custom metadata
    with patch(
        "app.api.v1.endpoints.extract.extraction_service.extract"
    ) as mock_extract:
        mock_extract.return_value = ExtractedContent(
            url="https://example.com/article",
            title="Article",
            content_blocks=[
                ContentBlock(id="block-1", type="paragraph", text="Text", metadata={})
            ],
            metadata={"custom_field": "custom_value", "word_count": 100},
        )

        # Act
        response = client.post("/api/v1/extract", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["metadata"]["custom_field"] == "custom_value"
    assert data["data"]["metadata"]["word_count"] == 100
    assert data["data"]["metadata"]["extraction_method"] == "readability"
    assert data["data"]["metadata"]["block_count"] == 1
