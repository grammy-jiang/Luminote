"""Tests for translation API endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_translate_success(client: TestClient) -> None:
    """Test successful translation request."""
    # Arrange
    request_data = {
        "content_blocks": [
            {
                "id": "block-1",
                "type": "paragraph",
                "text": "Hello, world!",
                "metadata": {},
            },
            {
                "id": "block-2",
                "type": "heading",
                "text": "Welcome",
                "metadata": {"level": 1},
            },
        ],
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key-12345",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data

    # Check translated blocks
    translated_blocks = data["data"]["translated_blocks"]
    assert len(translated_blocks) == 2

    # Check first block
    assert translated_blocks[0]["id"] == "block-1"
    assert translated_blocks[0]["type"] == "paragraph"
    assert translated_blocks[0]["text"] == "[TRANSLATED] Hello, world!"
    assert translated_blocks[0]["metadata"]["provider"] == "openai"
    assert translated_blocks[0]["metadata"]["model"] == "gpt-4"

    # Check second block
    assert translated_blocks[1]["id"] == "block-2"
    assert translated_blocks[1]["type"] == "heading"
    assert translated_blocks[1]["text"] == "[TRANSLATED] Welcome"

    # Check metadata
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]
    assert "processing_time" in data["metadata"]
    assert data["metadata"]["processing_time"] >= 0

    # Check headers
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time" in response.headers


@pytest.mark.unit
def test_translate_missing_content_blocks(client: TestClient) -> None:
    """Test translation request with missing content_blocks field."""
    # Arrange
    request_data = {
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "content_blocks" in str(data)


@pytest.mark.unit
def test_translate_empty_content_blocks(client: TestClient) -> None:
    """Test translation request with empty content_blocks array."""
    # Arrange
    request_data = {
        "content_blocks": [],  # Empty array
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "request_id" in data


@pytest.mark.unit
def test_translate_invalid_provider(client: TestClient) -> None:
    """Test translation request with invalid provider name."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "invalid_provider",  # Invalid provider
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    errors = data["details"]["errors"]
    assert any("provider" in error["field"] for error in errors)


@pytest.mark.unit
def test_translate_invalid_block_type(client: TestClient) -> None:
    """Test translation request with invalid block type."""
    # Arrange
    request_data = {
        "content_blocks": [
            {
                "id": "1",
                "type": "invalid_type",  # Invalid type
                "text": "Hello",
                "metadata": {},
            }
        ],
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_translate_missing_target_language(client: TestClient) -> None:
    """Test translation request with missing target_language."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_translate_invalid_language_code(client: TestClient) -> None:
    """Test translation request with invalid language code format."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "eng",  # 3 letters - invalid
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_translate_language_code_with_non_alphabetic(client: TestClient) -> None:
    """Test translation request with non-alphabetic characters in language code."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "e1",  # Contains digit - invalid
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    errors = data["details"]["errors"]
    assert any("target_language" in error["field"] for error in errors)
    assert any("only letters" in error["message"] for error in errors)


@pytest.mark.unit
def test_translate_empty_text(client: TestClient) -> None:
    """Test translation request with empty text in block."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "", "metadata": {}}  # Empty text
        ],
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test-key",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_translate_missing_api_key(client: TestClient) -> None:
    """Test translation request with missing api_key."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_translate_multiple_blocks_preserves_order(client: TestClient) -> None:
    """Test that translation preserves the order of blocks."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "block-1", "type": "paragraph", "text": "First", "metadata": {}},
            {"id": "block-2", "type": "heading", "text": "Second", "metadata": {}},
            {"id": "block-3", "type": "quote", "text": "Third", "metadata": {}},
            {"id": "block-4", "type": "list", "text": "Fourth", "metadata": {}},
            {"id": "block-5", "type": "code", "text": "Fifth", "metadata": {}},
        ],
        "target_language": "fr",
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "api_key": "sk-ant-test",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    translated_blocks = data["data"]["translated_blocks"]

    assert len(translated_blocks) == 5
    assert translated_blocks[0]["id"] == "block-1"
    assert translated_blocks[1]["id"] == "block-2"
    assert translated_blocks[2]["id"] == "block-3"
    assert translated_blocks[3]["id"] == "block-4"
    assert translated_blocks[4]["id"] == "block-5"


@pytest.mark.unit
def test_translate_anthropic_provider(client: TestClient) -> None:
    """Test translation request with Anthropic provider."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Test", "metadata": {}}
        ],
        "target_language": "de",
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "api_key": "sk-ant-test",
    }

    # Act
    response = client.post("/api/v1/translate", json=request_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["translated_blocks"][0]["metadata"]["provider"] == "anthropic"
