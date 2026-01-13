"""Storage schema definitions for IndexedDB.

This module defines TypedDict schemas for data structures stored in IndexedDB
on the frontend. These schemas ensure consistency between frontend storage and
backend understanding of the data model.

Related ADR: ADR-003 (Client-Side Storage Strategy)
"""

from typing import Any, Literal, TypedDict


class TranslationRecord(TypedDict):
    """Translation record stored in IndexedDB.

    Object Store: translations
    Primary Key: translation_id
    Indexes: document_url, created_at, block_id
    """

    translation_id: str  # UUID
    document_url: str  # URL of the document
    block_id: str  # ID of the content block
    source_text: str  # Original text
    translated_text: str  # Translated text
    source_language: str  # ISO 639-1 code (e.g., "en")
    target_language: str  # ISO 639-1 code (e.g., "es")
    provider: str  # AI provider (e.g., "openai")
    model: str  # Model identifier (e.g., "gpt-4")
    created_at: int  # Timestamp in milliseconds


class HistoryEntry(TypedDict):
    """History entry stored in IndexedDB.

    Object Store: history
    Primary Key: history_id
    Indexes: document_url, visited_at
    """

    history_id: str  # UUID
    document_url: str  # URL of the visited page
    title: str  # Page title
    visited_at: int  # Timestamp in milliseconds
    language_pair: str  # Format: "source|target" (e.g., "zh-CN|en")
    content_preview: str  # First 200 chars of content
    metadata: dict[str, Any]  # Additional metadata


class NoteRecord(TypedDict):
    """Note record stored in IndexedDB.

    Object Store: notes
    Primary Key: note_id
    Indexes: document_url, created_at, block_id
    """

    note_id: str  # UUID
    document_url: str  # URL of the document
    block_id: str  # ID of the content block
    note_type: Literal["explanation", "definition", "summary", "highlight"]
    content: str  # Note content
    created_at: int  # Timestamp in milliseconds
    updated_at: int  # Timestamp in milliseconds
    tags: list[str]  # User-defined tags


class ArtifactRecord(TypedDict):
    """Artifact record stored in IndexedDB.

    Object Store: artifacts
    Primary Key: artifact_id
    Indexes: document_url, job_id, created_at
    """

    artifact_id: str  # UUID
    document_url: str  # URL of the document
    job_id: str  # AI job ID that created this artifact
    artifact_type: str  # Type of artifact (e.g., "note", "link_card")
    content: dict[str, Any]  # Artifact content (structure varies by type)
    provider: str  # AI provider used
    model: str  # Model identifier
    prompt_version: str  # Version of prompt used
    created_at: int  # Timestamp in milliseconds


# IndexedDB database information
DATABASE_NAME = "luminote"
DATABASE_VERSION = 1

# Object store names
STORE_TRANSLATIONS = "translations"
STORE_HISTORY = "history"
STORE_NOTES = "notes"
STORE_ARTIFACTS = "artifacts"


def validate_translation_record(record: dict[str, Any]) -> bool:
    """Validate a translation record structure.

    Args:
        record: Dictionary to validate as TranslationRecord.

    Returns:
        True if valid, False otherwise.
    """
    required_fields = {
        "translation_id",
        "document_url",
        "block_id",
        "source_text",
        "translated_text",
        "source_language",
        "target_language",
        "provider",
        "model",
        "created_at",
    }
    return all(field in record for field in required_fields)


def validate_history_entry(entry: dict[str, Any]) -> bool:
    """Validate a history entry structure.

    Args:
        entry: Dictionary to validate as HistoryEntry.

    Returns:
        True if valid, False otherwise.
    """
    required_fields = {
        "history_id",
        "document_url",
        "title",
        "visited_at",
        "language_pair",
        "content_preview",
        "metadata",
    }
    return all(field in entry for field in required_fields)


def validate_note_record(record: dict[str, Any]) -> bool:
    """Validate a note record structure.

    Args:
        record: Dictionary to validate as NoteRecord.

    Returns:
        True if valid, False otherwise.
    """
    required_fields = {
        "note_id",
        "document_url",
        "block_id",
        "note_type",
        "content",
        "created_at",
        "updated_at",
        "tags",
    }
    if not all(field in record for field in required_fields):
        return False

    # Validate note_type
    valid_types = {"explanation", "definition", "summary", "highlight"}
    return record.get("note_type") in valid_types


def validate_artifact_record(record: dict[str, Any]) -> bool:
    """Validate an artifact record structure.

    Args:
        record: Dictionary to validate as ArtifactRecord.

    Returns:
        True if valid, False otherwise.
    """
    required_fields = {
        "artifact_id",
        "document_url",
        "job_id",
        "artifact_type",
        "content",
        "provider",
        "model",
        "prompt_version",
        "created_at",
    }
    return all(field in record for field in required_fields)
