"""Tests for VersioningService."""

import json
import time
from pathlib import Path

import pytest

from app.schemas.versioning import TranslatedBlock, VersionMetadata
from app.services.versioning_service import VersioningService


@pytest.fixture
def temp_storage(tmp_path: Path) -> Path:
    """Create temporary storage directory for testing.

    Args:
        tmp_path: Pytest's temporary directory fixture

    Returns:
        Path to temporary storage directory
    """
    storage = tmp_path / "versions"
    storage.mkdir(exist_ok=True)
    return storage


@pytest.fixture
def versioning_service(temp_storage: Path) -> VersioningService:
    """Create VersioningService with temporary storage.

    Args:
        temp_storage: Temporary storage directory

    Returns:
        VersioningService instance
    """
    return VersioningService(storage_path=temp_storage)


@pytest.fixture
def sample_metadata() -> VersionMetadata:
    """Create sample version metadata for testing.

    Returns:
        VersionMetadata instance
    """
    return VersionMetadata(
        provider="openai",
        model="gpt-4",
        target_language="es",
        source_language="en",
        prompt="Translate this text",
        custom_instructions="Be formal",
    )


@pytest.fixture
def sample_blocks() -> list[TranslatedBlock]:
    """Create sample translated blocks for testing.

    Returns:
        List of TranslatedBlock instances
    """
    return [
        TranslatedBlock(
            id="block-1",
            type="paragraph",
            original_text="Hello world",
            translated_text="Hola mundo",
            metadata={"tokens": 10},
        ),
        TranslatedBlock(
            id="block-2",
            type="heading",
            original_text="Welcome",
            translated_text="Bienvenido",
            metadata={"tokens": 5},
        ),
    ]


@pytest.mark.unit
def test_versioning_service_initialization(temp_storage: Path) -> None:
    """Test VersioningService initializes with correct storage path."""
    service = VersioningService(storage_path=temp_storage)

    assert service.storage_path == temp_storage
    assert temp_storage.exists()
    assert temp_storage.is_dir()


@pytest.mark.unit
def test_versioning_service_creates_storage_directory() -> None:
    """Test VersioningService creates storage directory if it doesn't exist."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "new_versions"
        assert not storage_path.exists()

        _ = VersioningService(storage_path=storage_path)

        assert storage_path.exists()
        assert storage_path.is_dir()


@pytest.mark.unit
def test_url_hash_stable(versioning_service: VersioningService) -> None:
    """Test that URL hash is stable (same URL produces same hash)."""
    url = "https://example.com/article"

    hash1 = versioning_service._get_url_hash(url)
    hash2 = versioning_service._get_url_hash(url)

    assert hash1 == hash2
    assert len(hash1) == 16
    assert isinstance(hash1, str)


@pytest.mark.unit
def test_url_hash_different_urls(versioning_service: VersioningService) -> None:
    """Test that different URLs produce different hashes."""
    url1 = "https://example.com/article1"
    url2 = "https://example.com/article2"

    hash1 = versioning_service._get_url_hash(url1)
    hash2 = versioning_service._get_url_hash(url2)

    assert hash1 != hash2


@pytest.mark.unit
def test_save_version_creates_file(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
    temp_storage: Path,
) -> None:
    """Test that save_version creates a version file on disk."""
    document_url = "https://example.com/article"

    version = versioning_service.save_version(
        document_url=document_url,
        blocks=sample_blocks,
        metadata=sample_metadata,
    )

    # Check that version was created with valid fields
    assert version.version_id is not None
    assert version.document_url == document_url
    assert version.created_at is not None
    assert len(version.blocks) == 2
    assert version.metadata == sample_metadata

    # Check that file was created
    version_file = temp_storage / f"{version.version_id}.json"
    assert version_file.exists()

    # Verify file content
    file_data = json.loads(version_file.read_text())
    assert file_data["version_id"] == version.version_id
    assert file_data["document_url"] == document_url


@pytest.mark.unit
def test_get_version_by_id(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test retrieving a specific version by ID."""
    document_url = "https://example.com/article"

    # Save a version
    saved_version = versioning_service.save_version(
        document_url=document_url,
        blocks=sample_blocks,
        metadata=sample_metadata,
    )

    # Retrieve it by ID
    retrieved_version = versioning_service.get_version(saved_version.version_id)

    assert retrieved_version is not None
    assert retrieved_version.version_id == saved_version.version_id
    assert retrieved_version.document_url == document_url
    assert len(retrieved_version.blocks) == 2


@pytest.mark.unit
def test_get_version_invalid_id_returns_none(
    versioning_service: VersioningService,
) -> None:
    """Test that invalid version_id returns None gracefully."""
    result = versioning_service.get_version("nonexistent-id")
    assert result is None


@pytest.mark.unit
def test_get_versions_returns_sorted(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that get_versions returns versions sorted newest first."""
    document_url = "https://example.com/article"

    # Save multiple versions with small delays
    versions = []
    for _ in range(3):
        version = versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )
        versions.append(version)
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Retrieve versions
    retrieved_versions = versioning_service.get_versions(document_url)

    # Check sorting (newest first)
    assert len(retrieved_versions) == 3
    for i in range(len(retrieved_versions) - 1):
        assert retrieved_versions[i].created_at >= retrieved_versions[i + 1].created_at


@pytest.mark.unit
def test_get_versions_filters_by_url(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that get_versions only returns versions for the specified URL."""
    url1 = "https://example.com/article1"
    url2 = "https://example.com/article2"

    # Save versions for two different URLs
    versioning_service.save_version(url1, sample_blocks, sample_metadata)
    versioning_service.save_version(url1, sample_blocks, sample_metadata)
    versioning_service.save_version(url2, sample_blocks, sample_metadata)

    # Get versions for url1
    versions_url1 = versioning_service.get_versions(url1)
    assert len(versions_url1) == 2

    # Get versions for url2
    versions_url2 = versioning_service.get_versions(url2)
    assert len(versions_url2) == 1


@pytest.mark.unit
def test_get_versions_empty_list_for_unknown_url(
    versioning_service: VersioningService,
) -> None:
    """Test that get_versions returns empty list for unknown URL."""
    versions = versioning_service.get_versions("https://example.com/nonexistent")
    assert versions == []


@pytest.mark.unit
def test_prune_old_versions_keeps_n_most_recent(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that prune_old_versions keeps only N most recent versions."""
    document_url = "https://example.com/article"
    keep_count = 3

    # Save 5 versions
    for _ in range(5):
        versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )
        time.sleep(0.01)  # Ensure different timestamps

    # Get all versions before pruning
    versions_before = versioning_service.get_versions(document_url)
    assert len(versions_before) == 5

    # Prune to keep only 3
    deleted_count = versioning_service.prune_old_versions(
        document_url, keep_count=keep_count
    )

    # Check that 2 versions were deleted
    assert deleted_count == 2

    # Get versions after pruning
    versions_after = versioning_service.get_versions(document_url)
    assert len(versions_after) == keep_count

    # Verify that the kept versions are the newest ones
    assert versions_after == versions_before[:keep_count]


@pytest.mark.unit
def test_prune_old_versions_no_deletion_when_under_limit(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that prune does not delete when version count is under limit."""
    document_url = "https://example.com/article"

    # Save 3 versions
    for _ in range(3):
        versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )

    # Prune with keep_count=5 (more than we have)
    deleted_count = versioning_service.prune_old_versions(document_url, keep_count=5)

    # No versions should be deleted
    assert deleted_count == 0
    assert len(versioning_service.get_versions(document_url)) == 3


@pytest.mark.unit
def test_get_version_count(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that get_version_count returns correct count."""
    document_url = "https://example.com/article"

    # Initially no versions
    assert versioning_service.get_version_count(document_url) == 0

    # Save 3 versions
    for _ in range(3):
        versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )

    # Check count
    assert versioning_service.get_version_count(document_url) == 3


@pytest.mark.unit
def test_save_version_auto_prunes(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that save_version automatically prunes old versions (default keep_count=5)."""
    document_url = "https://example.com/article"

    # Save 10 versions
    for _ in range(10):
        versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )
        time.sleep(0.01)

    # Check that only 5 remain (auto-pruned)
    versions = versioning_service.get_versions(document_url)
    assert len(versions) == 5


@pytest.mark.unit
def test_full_versioning_workflow(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Integration test: save 10 versions, prune to 5, verify kept versions are newest.

    This is the comprehensive workflow test as specified in the acceptance criteria.
    """
    document_url = "https://example.com/article"

    # Step 1: Save 10 versions
    saved_versions = []
    for _ in range(10):
        version = versioning_service.save_version(
            document_url=document_url,
            blocks=sample_blocks,
            metadata=sample_metadata,
        )
        saved_versions.append(version)
        time.sleep(0.01)  # Ensure different timestamps

    # Step 2: Verify 10 versions exist (but auto-prune keeps only 5)
    versions_after_save = versioning_service.get_versions(document_url)
    assert len(versions_after_save) == 5  # Auto-pruned to 5

    # Step 3: Manually prune again (should do nothing since already at 5)
    deleted = versioning_service.prune_old_versions(document_url, keep_count=5)
    assert deleted == 0

    # Step 4: Verify only 5 remain
    versions_after_prune = versioning_service.get_versions(document_url)
    assert len(versions_after_prune) == 5

    # Step 5: Verify kept versions are the newest 5 (last 5 saved)
    # The newest versions should be the last 5 we saved
    newest_version_ids = [v.version_id for v in versions_after_prune]
    last_5_saved_ids = [v.version_id for v in saved_versions[-5:]]

    # All version IDs from the last 5 saved should be in the kept versions
    for version_id in last_5_saved_ids:
        assert version_id in newest_version_ids


@pytest.mark.unit
def test_version_metadata_serialization(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
    sample_metadata: VersionMetadata,
) -> None:
    """Test that version metadata is correctly serialized and deserialized."""
    document_url = "https://example.com/article"

    # Save version with metadata
    saved_version = versioning_service.save_version(
        document_url=document_url,
        blocks=sample_blocks,
        metadata=sample_metadata,
    )

    # Retrieve and verify metadata
    retrieved_version = versioning_service.get_version(saved_version.version_id)

    assert retrieved_version is not None
    assert retrieved_version.metadata.provider == "openai"
    assert retrieved_version.metadata.model == "gpt-4"
    assert retrieved_version.metadata.target_language == "es"
    assert retrieved_version.metadata.source_language == "en"
    assert retrieved_version.metadata.prompt == "Translate this text"
    assert retrieved_version.metadata.custom_instructions == "Be formal"


@pytest.mark.unit
def test_corrupted_file_handling(
    versioning_service: VersioningService,
    temp_storage: Path,
) -> None:
    """Test that service handles corrupted version files gracefully."""
    # Create a corrupted JSON file
    corrupted_file = temp_storage / "corrupted.json"
    corrupted_file.write_text("not valid json{{{")

    # Should not crash, just skip the corrupted file
    versions = versioning_service.get_versions("https://example.com/any")
    assert versions == []

    # get_version on corrupted file should return None
    result = versioning_service.get_version("corrupted")
    assert result is None


@pytest.mark.unit
def test_version_with_minimal_metadata(
    versioning_service: VersioningService,
    sample_blocks: list[TranslatedBlock],
) -> None:
    """Test saving version with minimal metadata (only required fields)."""
    document_url = "https://example.com/article"

    # Minimal metadata (only required fields)
    minimal_metadata = VersionMetadata(
        provider="anthropic",
        model="claude-3",
        target_language="fr",
    )

    version = versioning_service.save_version(
        document_url=document_url,
        blocks=sample_blocks,
        metadata=minimal_metadata,
    )

    # Verify it was saved correctly
    retrieved = versioning_service.get_version(version.version_id)
    assert retrieved is not None
    assert retrieved.metadata.provider == "anthropic"
    assert retrieved.metadata.model == "claude-3"
    assert retrieved.metadata.target_language == "fr"
    assert retrieved.metadata.source_language is None
    assert retrieved.metadata.prompt is None
    assert retrieved.metadata.custom_instructions is None
