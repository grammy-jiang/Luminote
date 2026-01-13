"""Tests for IndexedDB storage schema definitions.

These tests validate the schema structures and validation functions that define the data
model for client-side IndexedDB storage.
"""

import pytest

from app.core.storage_schema import (
    DATABASE_NAME,
    DATABASE_VERSION,
    STORE_ARTIFACTS,
    STORE_HISTORY,
    STORE_NOTES,
    STORE_TRANSLATIONS,
    validate_artifact_record,
    validate_history_entry,
    validate_note_record,
    validate_translation_record,
)


@pytest.mark.unit
def test_database_constants():
    """Test that database constants are correctly defined."""
    assert DATABASE_NAME == "luminote"
    assert DATABASE_VERSION == 1
    assert STORE_TRANSLATIONS == "translations"
    assert STORE_HISTORY == "history"
    assert STORE_NOTES == "notes"
    assert STORE_ARTIFACTS == "artifacts"


@pytest.mark.unit
def test_validate_translation_record_valid():
    """Test validation of a valid translation record."""
    record = {
        "translation_id": "test-id-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "source_text": "Hello",
        "translated_text": "Hola",
        "source_language": "en",
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "created_at": 1234567890000,
    }

    assert validate_translation_record(record) is True


@pytest.mark.unit
def test_validate_translation_record_missing_fields():
    """Test validation fails for translation record with missing fields."""
    # Missing translated_text
    record = {
        "translation_id": "test-id-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "source_text": "Hello",
        "source_language": "en",
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "created_at": 1234567890000,
    }

    assert validate_translation_record(record) is False


@pytest.mark.unit
def test_validate_translation_record_extra_fields():
    """Test validation succeeds with extra fields (flexible schema)."""
    record = {
        "translation_id": "test-id-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "source_text": "Hello",
        "translated_text": "Hola",
        "source_language": "en",
        "target_language": "es",
        "provider": "openai",
        "model": "gpt-4",
        "created_at": 1234567890000,
        "extra_field": "extra_value",  # Extra field should be allowed
    }

    assert validate_translation_record(record) is True


@pytest.mark.unit
def test_validate_history_entry_valid():
    """Test validation of a valid history entry."""
    entry = {
        "history_id": "history-123",
        "document_url": "https://example.com",
        "title": "Example Page",
        "visited_at": 1234567890000,
        "language_pair": "en|es",
        "content_preview": "This is a preview...",
        "metadata": {"key": "value"},
    }

    assert validate_history_entry(entry) is True


@pytest.mark.unit
def test_validate_history_entry_missing_fields():
    """Test validation fails for history entry with missing fields."""
    # Missing title
    entry = {
        "history_id": "history-123",
        "document_url": "https://example.com",
        "visited_at": 1234567890000,
        "language_pair": "en|es",
        "content_preview": "This is a preview...",
        "metadata": {"key": "value"},
    }

    assert validate_history_entry(entry) is False


@pytest.mark.unit
def test_validate_note_record_valid():
    """Test validation of a valid note record."""
    record = {
        "note_id": "note-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "note_type": "explanation",
        "content": "This is an explanation",
        "created_at": 1234567890000,
        "updated_at": 1234567890000,
        "tags": ["important", "reference"],
    }

    assert validate_note_record(record) is True


@pytest.mark.unit
def test_validate_note_record_all_types():
    """Test validation of all valid note types."""
    valid_types = ["explanation", "definition", "summary", "highlight"]

    for note_type in valid_types:
        record = {
            "note_id": "note-123",
            "document_url": "https://example.com",
            "block_id": "block-1",
            "note_type": note_type,
            "content": "Note content",
            "created_at": 1234567890000,
            "updated_at": 1234567890000,
            "tags": [],
        }

        assert validate_note_record(record) is True, f"Failed for type: {note_type}"


@pytest.mark.unit
def test_validate_note_record_invalid_type():
    """Test validation fails for invalid note type."""
    record = {
        "note_id": "note-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "note_type": "invalid_type",  # Invalid type
        "content": "Note content",
        "created_at": 1234567890000,
        "updated_at": 1234567890000,
        "tags": [],
    }

    assert validate_note_record(record) is False


@pytest.mark.unit
def test_validate_note_record_missing_fields():
    """Test validation fails for note record with missing fields."""
    # Missing content
    record = {
        "note_id": "note-123",
        "document_url": "https://example.com",
        "block_id": "block-1",
        "note_type": "explanation",
        "created_at": 1234567890000,
        "updated_at": 1234567890000,
        "tags": [],
    }

    assert validate_note_record(record) is False


@pytest.mark.unit
def test_validate_artifact_record_valid():
    """Test validation of a valid artifact record."""
    record = {
        "artifact_id": "artifact-123",
        "document_url": "https://example.com",
        "job_id": "job-456",
        "artifact_type": "note",
        "content": {"text": "Artifact content"},
        "provider": "openai",
        "model": "gpt-4",
        "prompt_version": "v1.0",
        "created_at": 1234567890000,
    }

    assert validate_artifact_record(record) is True


@pytest.mark.unit
def test_validate_artifact_record_missing_fields():
    """Test validation fails for artifact record with missing fields."""
    # Missing prompt_version
    record = {
        "artifact_id": "artifact-123",
        "document_url": "https://example.com",
        "job_id": "job-456",
        "artifact_type": "note",
        "content": {"text": "Artifact content"},
        "provider": "openai",
        "model": "gpt-4",
        "created_at": 1234567890000,
    }

    assert validate_artifact_record(record) is False


@pytest.mark.unit
def test_validate_artifact_record_complex_content():
    """Test validation with complex artifact content structure."""
    record = {
        "artifact_id": "artifact-123",
        "document_url": "https://example.com",
        "job_id": "job-456",
        "artifact_type": "link_card",
        "content": {
            "title": "Example Link",
            "url": "https://example.com",
            "description": "A description",
            "metadata": {"key": "value"},
        },
        "provider": "openai",
        "model": "gpt-4",
        "prompt_version": "v1.0",
        "created_at": 1234567890000,
    }

    assert validate_artifact_record(record) is True


@pytest.mark.unit
def test_all_validators_with_empty_dict():
    """Test all validators return False for empty dictionary."""
    empty = {}

    assert validate_translation_record(empty) is False
    assert validate_history_entry(empty) is False
    assert validate_note_record(empty) is False
    assert validate_artifact_record(empty) is False
