"""Tests for streaming translation API endpoint."""

import json

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_stream_translation_success(client: TestClient) -> None:
    """Test successful streaming translation request."""
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
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        # Assert response headers
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert "X-Request-ID" in response.headers
        assert response.headers["Cache-Control"] == "no-cache"
        assert response.headers["X-Accel-Buffering"] == "no"

        # Parse SSE events
        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                data = line_str[6:]  # Remove "data: " prefix
                events.append(json.loads(data))

        # Should have 2 block events + 1 done event
        assert len(events) == 3

        # Check first block event
        assert events[0]["type"] == "block"
        assert events[0]["block_id"] == "block-1"
        assert events[0]["translation"] == "[ES] Hello, world!"
        assert "tokens_used" in events[0]
        assert events[0]["tokens_used"] > 0

        # Check second block event
        assert events[1]["type"] == "block"
        assert events[1]["block_id"] == "block-2"
        assert events[1]["translation"] == "[ES] Welcome"
        assert "tokens_used" in events[1]

        # Check done event
        assert events[2]["type"] == "done"
        assert "total_tokens" in events[2]
        assert events[2]["total_tokens"] > 0
        assert "processing_time" in events[2]
        assert events[2]["processing_time"] >= 0


@pytest.mark.unit
def test_stream_translation_single_block(client: TestClient) -> None:
    """Test streaming translation with a single block."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "solo", "type": "paragraph", "text": "Single block", "metadata": {}}
        ],
        "target_language": "fr",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        assert response.status_code == 200

        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                events.append(json.loads(line_str[6:]))

        # Should have 1 block event + 1 done event
        assert len(events) == 2
        assert events[0]["type"] == "block"
        assert events[0]["block_id"] == "solo"
        assert events[1]["type"] == "done"


@pytest.mark.unit
def test_stream_translation_multiple_blocks(client: TestClient) -> None:
    """Test streaming translation preserves order with multiple blocks."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "block-1", "type": "paragraph", "text": "First", "metadata": {}},
            {"id": "block-2", "type": "heading", "text": "Second", "metadata": {}},
            {"id": "block-3", "type": "quote", "text": "Third", "metadata": {}},
            {"id": "block-4", "type": "list", "text": "Fourth", "metadata": {}},
            {"id": "block-5", "type": "code", "text": "Fifth", "metadata": {}},
        ],
        "target_language": "de",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        assert response.status_code == 200

        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                events.append(json.loads(line_str[6:]))

        # Should have 5 block events + 1 done event
        assert len(events) == 6

        # Check order is preserved
        block_events = [e for e in events if e["type"] == "block"]
        assert len(block_events) == 5
        assert block_events[0]["block_id"] == "block-1"
        assert block_events[1]["block_id"] == "block-2"
        assert block_events[2]["block_id"] == "block-3"
        assert block_events[3]["block_id"] == "block-4"
        assert block_events[4]["block_id"] == "block-5"

        # Check done event is last
        assert events[-1]["type"] == "done"


@pytest.mark.unit
def test_stream_translation_missing_content_blocks(client: TestClient) -> None:
    """Test streaming translation with missing content_blocks field."""
    # Arrange
    request_data = {
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_empty_content_blocks(client: TestClient) -> None:
    """Test streaming translation with empty content_blocks array."""
    # Arrange
    request_data = {
        "content_blocks": [],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_invalid_provider(client: TestClient) -> None:
    """Test streaming translation with invalid provider name."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "invalid_provider",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_invalid_language_code(client: TestClient) -> None:
    """Test streaming translation with invalid language code format."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "eng",  # 3 letters - invalid
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_empty_text(client: TestClient) -> None:
    """Test streaming translation with empty text in block."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_missing_api_key(client: TestClient) -> None:
    """Test streaming translation with missing api_key."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Hello", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
    }

    # Act
    response = client.post("/api/v1/translate/stream", json=request_data)

    # Assert - validation error before streaming starts
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.unit
def test_stream_translation_sse_format(client: TestClient) -> None:
    """Test that SSE format is correct (data: {...}\\n\\n)."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Test", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        # Read raw response
        content = b""
        for chunk in response.iter_bytes():
            content += chunk

        text = content.decode("utf-8")

        # Should contain properly formatted SSE events
        assert "data: " in text

        # Each event should end with double newline
        lines = text.split("\n")
        data_lines = [line for line in lines if line.startswith("data: ")]
        assert len(data_lines) >= 2  # At least one block + done event

        # Each data line should be followed by an empty line (SSE format)
        for i, line in enumerate(lines):
            if line.startswith("data: "):
                # Next line should be empty (SSE event separator)
                if i + 1 < len(lines):
                    assert lines[i + 1] == ""


@pytest.mark.unit
def test_stream_translation_token_counting(client: TestClient) -> None:
    """Test that token counts are accumulated correctly."""
    # Arrange
    request_data = {
        "content_blocks": [
            {
                "id": "1",
                "type": "paragraph",
                "text": "Short text",
                "metadata": {},
            },
            {
                "id": "2",
                "type": "paragraph",
                "text": "This is a much longer text that should use more tokens",
                "metadata": {},
            },
        ],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                events.append(json.loads(line_str[6:]))

        # Extract block events and done event
        block_events = [e for e in events if e["type"] == "block"]
        done_events = [e for e in events if e["type"] == "done"]

        assert len(block_events) == 2
        assert len(done_events) == 1

        # Calculate total tokens from blocks
        total_from_blocks = sum(e["tokens_used"] for e in block_events)

        # Should match total in done event
        assert done_events[0]["total_tokens"] == total_from_blocks
        assert done_events[0]["total_tokens"] > 0


@pytest.mark.unit
def test_stream_translation_processing_time(client: TestClient) -> None:
    """Test that processing time is included in done event."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Test", "metadata": {}}
        ],
        "target_language": "es",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                events.append(json.loads(line_str[6:]))

        done_event = [e for e in events if e["type"] == "done"][0]

        # Processing time should be a positive number
        assert "processing_time" in done_event
        assert isinstance(done_event["processing_time"], int | float)
        assert done_event["processing_time"] >= 0


@pytest.mark.unit
def test_stream_translation_all_block_types(client: TestClient) -> None:
    """Test streaming translation with all supported block types."""
    # Arrange
    request_data = {
        "content_blocks": [
            {"id": "1", "type": "paragraph", "text": "Paragraph", "metadata": {}},
            {"id": "2", "type": "heading", "text": "Heading", "metadata": {}},
            {"id": "3", "type": "list", "text": "List item", "metadata": {}},
            {"id": "4", "type": "quote", "text": "Quote", "metadata": {}},
            {"id": "5", "type": "code", "text": "Code", "metadata": {}},
        ],
        "target_language": "fr",
        "provider": "mock",
        "model": "test-model",
        "api_key": "test-key",
    }

    # Act
    with client.stream(
        "POST", "/api/v1/translate/stream", json=request_data
    ) as response:
        assert response.status_code == 200

        events = []
        for line in response.iter_lines():
            line_str = line.decode("utf-8") if isinstance(line, bytes) else line
            if line_str.startswith("data: "):
                events.append(json.loads(line_str[6:]))

        # All blocks should be translated
        block_events = [e for e in events if e["type"] == "block"]
        assert len(block_events) == 5

        # Check all translations are prefixed correctly
        for event in block_events:
            assert event["translation"].startswith("[FR]")
