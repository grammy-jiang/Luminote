"""Translation versioning service.

This module provides version management for translations with automatic pruning.
"""

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.versioning import TranslatedBlock, TranslationVersion, VersionMetadata


class VersioningService:
    """Manage translation versions with automatic pruning.

    This service provides file-based storage for translation versions with
    automatic pruning to keep only the N most recent versions per document.
    """

    def __init__(self, storage_path: Path | str = Path("./data/versions")) -> None:
        """Initialize the versioning service.

        Args:
            storage_path: Path to directory for storing version files.
                         Creates directory if it doesn't exist.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_url_hash(self, url: str) -> str:
        """Generate stable hash for URL.

        Args:
            url: Document URL to hash

        Returns:
            16-character hex hash of the URL
        """
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def save_version(
        self,
        document_url: str,
        blocks: list[TranslatedBlock],
        metadata: VersionMetadata,
    ) -> TranslationVersion:
        """Save new translation version and auto-prune old versions.

        Args:
            document_url: URL of the original document
            blocks: List of translated content blocks
            metadata: Translation metadata (provider, model, etc.)

        Returns:
            The saved TranslationVersion with generated version_id and timestamp
        """
        # Create version with UUID and timestamp
        version = TranslationVersion(
            version_id=str(uuid.uuid4()),
            document_url=document_url,
            created_at=datetime.now(UTC),
            blocks=blocks,
            metadata=metadata,
        )

        # Save to file
        version_file = self.storage_path / f"{version.version_id}.json"
        version_data = version.model_dump(mode="json")
        version_file.write_text(json.dumps(version_data, indent=2))

        # Auto-prune old versions
        self.prune_old_versions(document_url)

        return version

    def get_versions(self, document_url: str) -> list[TranslationVersion]:
        """Get all versions for a document, sorted newest first.

        Args:
            document_url: URL of the document

        Returns:
            List of TranslationVersion objects sorted by created_at descending
        """
        url_hash = self._get_url_hash(document_url)
        versions: list[TranslationVersion] = []

        # Scan all version files
        for version_file in self.storage_path.glob("*.json"):
            try:
                data = json.loads(version_file.read_text())
                version = TranslationVersion(**data)

                # Check if this version belongs to the requested document
                if self._get_url_hash(version.document_url) == url_hash:
                    versions.append(version)
            except Exception:
                # Skip corrupted or invalid files
                continue

        # Sort by created_at descending (newest first)
        return sorted(versions, key=lambda v: v.created_at, reverse=True)

    def get_version(self, version_id: str) -> TranslationVersion | None:
        """Get a specific version by ID.

        Args:
            version_id: UUID of the version to retrieve

        Returns:
            TranslationVersion if found, None otherwise
        """
        version_file = self.storage_path / f"{version_id}.json"

        if not version_file.exists():
            return None

        try:
            data = json.loads(version_file.read_text())
            return TranslationVersion(**data)
        except Exception:
            # Return None for corrupted files
            return None

    def prune_old_versions(self, document_url: str, keep_count: int = 5) -> int:
        """Delete old versions beyond keep_count.

        Args:
            document_url: URL of the document
            keep_count: Number of most recent versions to keep (default: 5)

        Returns:
            Number of versions deleted
        """
        versions = self.get_versions(document_url)

        if len(versions) <= keep_count:
            return 0

        # Get versions to delete (oldest ones)
        to_delete = versions[keep_count:]
        deleted_count = 0

        for version in to_delete:
            version_file = self.storage_path / f"{version.version_id}.json"
            try:
                version_file.unlink(missing_ok=True)
                deleted_count += 1
            except Exception:
                # Continue deleting even if one fails
                continue

        return deleted_count

    def get_version_count(self, document_url: str) -> int:
        """Get total version count for a document.

        Args:
            document_url: URL of the document

        Returns:
            Total number of versions for the document
        """
        return len(self.get_versions(document_url))
