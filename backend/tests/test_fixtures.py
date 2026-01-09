"""Example tests demonstrating fixture usage.

These tests demonstrate how to use the mock_openai_response and sample_content fixtures.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.utils import validate_request_id


@pytest.mark.unit
def test_mock_openai_response_fixture(mock_openai_response: dict[str, Any]) -> None:
    """Test that mock_openai_response fixture provides valid OpenAI response format."""
    assert "id" in mock_openai_response
    assert "object" in mock_openai_response
    assert mock_openai_response["object"] == "chat.completion"
    assert "choices" in mock_openai_response
    assert len(mock_openai_response["choices"]) > 0
    assert "message" in mock_openai_response["choices"][0]
    assert mock_openai_response["choices"][0]["message"]["role"] == "assistant"
    assert (
        mock_openai_response["choices"][0]["message"]["content"]
        == "This is a test translation."
    )


@pytest.mark.unit
def test_sample_content_fixture(sample_content: dict[str, Any]) -> None:
    """Test that sample_content fixture provides valid content structure."""
    assert "title" in sample_content
    assert sample_content["title"] == "Test Article"
    assert "content" in sample_content
    assert "url" in sample_content
    assert sample_content["url"] == "https://example.com/test-article"
    assert "language" in sample_content
    assert sample_content["language"] == "en"
    assert "word_count" in sample_content
    assert sample_content["word_count"] > 0


@pytest.mark.unit
def test_validate_request_id_with_real_response(client: TestClient) -> None:
    """Test that validate_request_id utility works with actual API responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers

    request_id = response.headers["x-request-id"]
    # Should be a valid UUID v4
    assert validate_request_id(request_id)


@pytest.mark.unit
def test_fixtures_integration(
    client: TestClient,
    sample_content: dict[str, Any],
    mock_openai_response: dict[str, Any],
) -> None:
    """Test using multiple fixtures together in a single test."""
    # Verify client works
    response = client.get("/health")
    assert response.status_code == 200

    # Verify sample content has required fields
    assert "content" in sample_content
    assert len(sample_content["content"]) > 0

    # Verify mock response has expected structure
    assert "choices" in mock_openai_response
    assert len(mock_openai_response["choices"]) > 0

    # Validate request ID from response
    request_id = response.headers["x-request-id"]
    assert validate_request_id(request_id)
