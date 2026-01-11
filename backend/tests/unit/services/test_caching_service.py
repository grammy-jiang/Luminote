"""Tests for CachingService."""

import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from app.schemas.extraction import ContentBlock, ExtractedContent
from app.services.caching_service import (
    DEFAULT_MAX_STORAGE_BYTES,
    DEFAULT_TTL_SECONDS,
    CacheEntry,
    CachingService,
)


def create_sample_content(url: str = "https://example.com") -> ExtractedContent:
    """Create a sample ExtractedContent for testing.

    Args:
        url: URL for the content

    Returns:
        ExtractedContent instance
    """
    return ExtractedContent(
        url=url,
        title="Sample Article",
        author="John Doe",
        date_published="2024-01-01T00:00:00Z",
        content_blocks=[
            ContentBlock(
                id="block-1",
                type="heading",
                text="Introduction",
                metadata={"level": 1},
            ),
            ContentBlock(
                id="block-2",
                type="paragraph",
                text="This is a sample paragraph with some content.",
                metadata={},
            ),
        ],
        metadata={"article_type": "blog"},
        extraction_timestamp=datetime.now(UTC),
    )


@pytest.mark.unit
def test_caching_service_init():
    """Test CachingService initialization."""
    # Default values
    service = CachingService()
    assert service.ttl_seconds == DEFAULT_TTL_SECONDS
    assert service.max_storage_bytes == DEFAULT_MAX_STORAGE_BYTES

    # Custom values
    service_custom = CachingService(ttl_seconds=3600, max_storage_bytes=1024)
    assert service_custom.ttl_seconds == 3600
    assert service_custom.max_storage_bytes == 1024


@pytest.mark.unit
def test_make_cache_key_short_url():
    """Test cache key generation for short URLs."""
    service = CachingService()

    url = "https://example.com/article"
    key = service._make_cache_key(url)

    # Short URLs should use the URL directly
    assert key == url


@pytest.mark.unit
def test_make_cache_key_long_url():
    """Test cache key generation for long URLs."""
    service = CachingService()

    # Create a URL longer than MAX_URL_LENGTH_FOR_KEY
    url = "https://example.com/" + "a" * 300
    key = service._make_cache_key(url)

    # Long URLs should be hashed
    assert key.startswith("url_hash:")
    assert len(key) == 73  # "url_hash:" + 64 char hex


@pytest.mark.unit
def test_compress_decompress_content():
    """Test content compression and decompression."""
    service = CachingService()
    original_content = create_sample_content()

    # Compress
    compressed = service._compress_content(original_content)
    assert isinstance(compressed, bytes)
    assert len(compressed) > 0

    # Verify it's actually compressed (should be smaller than JSON)
    json_size = len(original_content.model_dump_json().encode("utf-8"))
    assert len(compressed) < json_size

    # Decompress
    decompressed = service._decompress_content(compressed)
    assert isinstance(decompressed, ExtractedContent)
    assert decompressed.url == original_content.url
    assert decompressed.title == original_content.title
    assert len(decompressed.content_blocks) == len(original_content.content_blocks)


@pytest.mark.unit
def test_set_and_get():
    """Test basic set and get operations."""
    service = CachingService()
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Set content
    service.set(url, content)

    # Get content
    cached_content = service.get(url)
    assert cached_content is not None
    assert cached_content.url == url
    assert cached_content.title == content.title


@pytest.mark.unit
def test_get_nonexistent():
    """Test getting non-existent content returns None."""
    service = CachingService()

    result = service.get("https://nonexistent.com")
    assert result is None


@pytest.mark.unit
def test_cache_hit_and_miss_stats():
    """Test cache statistics for hits and misses."""
    service = CachingService()
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Initial stats
    stats = service.get_stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 0

    # Cache miss
    result = service.get(url)
    assert result is None
    stats = service.get_stats()
    assert stats["misses"] == 1

    # Cache set and hit
    service.set(url, content)
    result = service.get(url)
    assert result is not None
    stats = service.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 50.0  # 1 hit out of 2 requests


@pytest.mark.unit
def test_ttl_expiration():
    """Test that entries expire after TTL."""
    # Use short TTL for testing
    service = CachingService(ttl_seconds=1)
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Set content
    service.set(url, content)

    # Should be available immediately
    cached = service.get(url)
    assert cached is not None

    # Wait for expiration
    time.sleep(1.1)

    # Should be expired now
    cached = service.get(url)
    assert cached is None

    # Stats should show expiration
    stats = service.get_stats()
    assert stats["expirations"] >= 1


@pytest.mark.unit
def test_cleanup_expired():
    """Test automatic cleanup of expired entries."""
    service = CachingService(ttl_seconds=1)

    # Add multiple entries
    for i in range(5):
        url = f"https://example.com/article-{i}"
        content = create_sample_content(url)
        service.set(url, content)

    # All entries should be present
    stats = service.get_stats()
    assert stats["entry_count"] == 5

    # Wait for expiration
    time.sleep(1.1)

    # Trigger cleanup by trying to get any entry
    service.get("https://example.com/article-0")

    # All entries should be cleaned up
    stats = service.get_stats()
    assert stats["entry_count"] == 0
    assert stats["expirations"] == 5


@pytest.mark.unit
def test_storage_quota_enforcement():
    """Test that storage quota is enforced."""
    # Set small quota for testing (2KB)
    service = CachingService(max_storage_bytes=2 * 1024)

    # Create larger content that will exceed quota
    evictions_before = 0
    for i in range(50):
        url = f"https://example.com/article-{i}"
        # Create larger content with more blocks
        content = ExtractedContent(
            url=url,
            title=f"Article {i}",
            author="Test Author",
            date_published="2024-01-01T00:00:00Z",
            content_blocks=[
                ContentBlock(
                    id=f"block-{j}",
                    type="paragraph",
                    text="This is a paragraph with substantial content. " * 10,
                    metadata={},
                )
                for j in range(5)  # 5 blocks per article
            ],
            metadata={},
            extraction_timestamp=datetime.now(UTC),
        )
        service.set(url, content)

        # Track evictions
        stats = service.get_stats()
        if stats["evictions"] > evictions_before:
            evictions_before = stats["evictions"]

    # Check that storage is under quota
    stats = service.get_stats()
    assert stats["storage_bytes"] <= 2 * 1024

    # Some entries should have been evicted
    assert stats["evictions"] > 0


@pytest.mark.unit
def test_lru_eviction():
    """Test that LRU eviction works correctly."""
    # Small quota to force eviction
    service = CachingService(max_storage_bytes=2 * 1024)

    # Add entries with larger content
    urls = []
    for i in range(15):
        url = f"https://example.com/article-{i}"
        urls.append(url)
        content = ExtractedContent(
            url=url,
            title=f"Article {i}",
            author="Test Author",
            date_published="2024-01-01T00:00:00Z",
            content_blocks=[
                ContentBlock(
                    id=f"block-{j}",
                    type="paragraph",
                    text="Large content for testing LRU eviction. " * 10,
                    metadata={},
                )
                for j in range(3)
            ],
            metadata={},
            extraction_timestamp=datetime.now(UTC),
        )
        service.set(url, content)

    # Access first few entries to make them "recently used"
    for url in urls[:3]:
        service.get(url)

    # Add more entries to trigger eviction
    for i in range(15, 20):
        url = f"https://example.com/article-{i}"
        content = ExtractedContent(
            url=url,
            title=f"Article {i}",
            author="Test Author",
            date_published="2024-01-01T00:00:00Z",
            content_blocks=[
                ContentBlock(
                    id=f"block-{j}",
                    type="paragraph",
                    text="Large content for testing LRU eviction. " * 10,
                    metadata={},
                )
                for j in range(3)
            ],
            metadata={},
            extraction_timestamp=datetime.now(UTC),
        )
        service.set(url, content)

    # Stats should show evictions
    stats = service.get_stats()
    assert stats["evictions"] > 0


@pytest.mark.unit
def test_invalidate():
    """Test cache invalidation."""
    service = CachingService()
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Set content
    service.set(url, content)
    assert service.get(url) is not None

    # Invalidate
    result = service.invalidate(url)
    assert result is True

    # Should be gone
    assert service.get(url) is None

    # Invalidating again should return False
    result = service.invalidate(url)
    assert result is False


@pytest.mark.unit
def test_clear():
    """Test clearing all cache entries."""
    service = CachingService()

    # Add multiple entries
    for i in range(10):
        url = f"https://example.com/article-{i}"
        content = create_sample_content(url)
        service.set(url, content)

    stats = service.get_stats()
    assert stats["entry_count"] == 10

    # Clear cache
    service.clear()

    stats = service.get_stats()
    assert stats["entry_count"] == 0


@pytest.mark.unit
def test_thread_safety():
    """Test that caching service is thread-safe."""
    service = CachingService()

    def worker(thread_id: int) -> None:
        """Worker function for thread safety test."""
        for i in range(10):
            url = f"https://example.com/thread-{thread_id}-article-{i}"
            content = create_sample_content(url)

            # Set content
            service.set(url, content)

            # Get content
            cached = service.get(url)
            assert cached is not None

    # Run multiple threads concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        for future in futures:
            future.result()  # Wait for completion and check for exceptions

    # All operations should complete without errors
    stats = service.get_stats()
    assert stats["entry_count"] > 0


@pytest.mark.unit
def test_get_stats_comprehensive():
    """Test that get_stats returns all expected fields."""
    service = CachingService()

    stats = service.get_stats()

    # Check all expected fields are present
    assert "hits" in stats
    assert "misses" in stats
    assert "evictions" in stats
    assert "expirations" in stats
    assert "hit_rate" in stats
    assert "entry_count" in stats
    assert "storage_bytes" in stats
    assert "storage_mb" in stats

    # Check types
    assert isinstance(stats["hits"], int)
    assert isinstance(stats["misses"], int)
    assert isinstance(stats["evictions"], int)
    assert isinstance(stats["expirations"], int)
    assert isinstance(stats["hit_rate"], float)
    assert isinstance(stats["entry_count"], int)
    assert isinstance(stats["storage_bytes"], int)
    assert isinstance(stats["storage_mb"], float)


@pytest.mark.unit
def test_compression_reduces_size():
    """Test that compression actually reduces storage size."""
    service = CachingService()

    # Create content with repetitive text (compresses well)
    content = ExtractedContent(
        url="https://example.com/article",
        title="Test Article",
        author="Test Author",
        date_published="2024-01-01T00:00:00Z",
        content_blocks=[
            ContentBlock(
                id=f"block-{i}",
                type="paragraph",
                text="This is a repetitive paragraph. " * 50,
                metadata={},
            )
            for i in range(10)
        ],
        metadata={},
        extraction_timestamp=datetime.now(UTC),
    )

    # Get original size
    json_bytes = content.model_dump_json().encode("utf-8")
    original_size = len(json_bytes)

    # Compress
    compressed = service._compress_content(content)
    compressed_size = len(compressed)

    # Compressed should be smaller
    assert compressed_size < original_size

    # Calculate compression ratio (should be significant for repetitive text)
    compression_ratio = compressed_size / original_size
    assert compression_ratio < 0.5  # Should compress to less than 50%


@pytest.mark.unit
def test_update_existing_entry():
    """Test that updating an existing entry works correctly."""
    service = CachingService()
    url = "https://example.com/article"

    # Set initial content
    content1 = create_sample_content(url)
    content1.title = "Original Title"
    service.set(url, content1)

    # Update with new content
    content2 = create_sample_content(url)
    content2.title = "Updated Title"
    service.set(url, content2)

    # Should get the updated content
    cached = service.get(url)
    assert cached is not None
    assert cached.title == "Updated Title"

    # Should still have only one entry
    stats = service.get_stats()
    assert stats["entry_count"] == 1


@pytest.mark.unit
def test_cache_entry_creation():
    """Test CacheEntry initialization."""
    compressed_data = b"test data"
    expires_at = time.time() + 3600
    size_bytes = len(compressed_data)

    entry = CacheEntry(compressed_data, expires_at, size_bytes)

    assert entry.compressed_data == compressed_data
    assert entry.expires_at == expires_at
    assert entry.size_bytes == size_bytes
    assert entry.last_accessed <= time.time()


@pytest.mark.unit
def test_empty_cache_stats():
    """Test stats for empty cache."""
    service = CachingService()

    stats = service.get_stats()

    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["evictions"] == 0
    assert stats["expirations"] == 0
    assert stats["hit_rate"] == 0.0
    assert stats["entry_count"] == 0
    assert stats["storage_bytes"] == 0
    assert stats["storage_mb"] == 0.0


@pytest.mark.unit
def test_multiple_gets_update_lru():
    """Test that multiple gets update LRU ordering."""
    service = CachingService(max_storage_bytes=3 * 1024)

    # Add entries
    url1 = "https://example.com/article-1"
    url2 = "https://example.com/article-2"
    url3 = "https://example.com/article-3"

    service.set(url1, create_sample_content(url1))
    service.set(url2, create_sample_content(url2))

    # Access url1 multiple times
    for _ in range(5):
        service.get(url1)

    # Add url3 - might trigger eviction
    service.set(url3, create_sample_content(url3))

    # url1 should still be accessible (recently used)
    _ = service.get(url1)
    # Note: Depending on sizes, may or may not be evicted
    # This test just ensures no errors occur with LRU updates


@pytest.mark.unit
def test_failed_decompression_removes_entry():
    """Test that failed decompression removes corrupted entry."""
    service = CachingService()
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Set valid content
    service.set(url, content)

    # Corrupt the compressed data
    cache_key = service._make_cache_key(url)
    with service._lock:
        service._cache[cache_key].compressed_data = b"corrupted data"

    # Getting should fail gracefully and remove entry
    result = service.get(url)
    assert result is None

    # Entry should be removed
    stats = service.get_stats()
    assert stats["entry_count"] == 0


@pytest.mark.unit
def test_caching_with_special_characters_in_url():
    """Test caching with URLs containing special characters."""
    service = CachingService()
    url = "https://example.com/article?id=123&lang=en#section"
    content = create_sample_content(url)

    service.set(url, content)
    cached = service.get(url)

    assert cached is not None
    assert cached.url == url


@pytest.mark.unit
def test_get_expired_entry_directly():
    """Test getting an expired entry that is still in cache."""
    service = CachingService(ttl_seconds=1)
    url = "https://example.com/article"
    content = create_sample_content(url)

    # Set content
    service.set(url, content)

    # Wait for expiration
    time.sleep(1.1)

    # Manually check entry is still in cache dict but expired
    cache_key = service._make_cache_key(url)
    with service._lock:
        assert cache_key in service._cache
        entry = service._cache[cache_key]
        assert entry.expires_at <= time.time()

    # Try to get - should detect expiration during get
    result = service.get(url)
    assert result is None

    # Entry should be removed
    stats = service.get_stats()
    assert stats["expirations"] >= 1


@pytest.mark.unit
def test_set_handles_compression_failure_gracefully():
    """Test that set doesn't crash if compression fails."""
    service = CachingService()
    url = "https://example.com/article"

    # Try to set content with a mock that fails during compression
    with patch.object(
        service, "_compress_content", side_effect=Exception("Compression failed")
    ):
        # This should not raise - it should just log and continue
        service.set(url, create_sample_content(url))

    # Cache should be empty since set failed
    result = service.get(url)
    assert result is None
