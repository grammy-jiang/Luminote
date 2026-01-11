"""Content caching service with TTL, compression, and LRU eviction.

This module provides an in-memory cache for extracted content with:
- 24-hour TTL per cached item
- URL-based cache keys (hashed for long URLs)
- Gzip compression for storage efficiency
- Automatic cleanup of expired entries
- Storage quota enforcement (100MB max)
- LRU eviction when quota is exceeded
- Thread-safe operations
"""

import gzip
import hashlib
import json
import threading
import time
from collections import OrderedDict
from typing import Any

from app.core.logging import get_logger
from app.schemas.extraction import ExtractedContent

logger = get_logger(__name__)

# Constants
DEFAULT_TTL_SECONDS = 24 * 60 * 60  # 24 hours
DEFAULT_MAX_STORAGE_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_URL_LENGTH_FOR_KEY = 200  # URLs longer than this will be hashed


class CacheEntry:
    """A single cache entry with metadata."""

    def __init__(
        self, compressed_data: bytes, expires_at: float, size_bytes: int
    ) -> None:
        """Initialize a cache entry.

        Args:
            compressed_data: Gzip-compressed JSON data
            expires_at: Unix timestamp when entry expires
            size_bytes: Size of compressed data in bytes
        """
        self.compressed_data = compressed_data
        self.expires_at = expires_at
        self.size_bytes = size_bytes
        self.last_accessed = time.time()


class CachingService:
    """Thread-safe caching service for extracted content.

    Provides in-memory caching with TTL, compression, quota management,
    and LRU eviction.
    """

    def __init__(
        self,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        max_storage_bytes: int = DEFAULT_MAX_STORAGE_BYTES,
    ) -> None:
        """Initialize the caching service.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 24h)
            max_storage_bytes: Maximum storage quota in bytes (default: 100MB)
        """
        self.ttl_seconds = ttl_seconds
        self.max_storage_bytes = max_storage_bytes
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
        }

    def _make_cache_key(self, url: str) -> str:
        """Generate cache key from URL.

        For short URLs, use the URL directly. For long URLs, use SHA256 hash
        to keep keys manageable.

        Args:
            url: URL to generate key from

        Returns:
            Cache key string
        """
        if len(url) <= MAX_URL_LENGTH_FOR_KEY:
            return url

        # Hash long URLs
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return f"url_hash:{url_hash}"

    def _compress_content(self, content: ExtractedContent) -> bytes:
        """Compress extracted content using gzip.

        Args:
            content: ExtractedContent to compress

        Returns:
            Gzip-compressed JSON bytes
        """
        # Convert to JSON
        json_str = content.model_dump_json()
        json_bytes = json_str.encode("utf-8")

        # Compress with gzip
        compressed = gzip.compress(json_bytes, compresslevel=6)
        return compressed

    def _decompress_content(self, compressed_data: bytes) -> ExtractedContent:
        """Decompress content from gzip format.

        Args:
            compressed_data: Gzip-compressed JSON bytes

        Returns:
            ExtractedContent instance
        """
        # Decompress
        json_bytes = gzip.decompress(compressed_data)
        json_str = json_bytes.decode("utf-8")

        # Parse JSON and create ExtractedContent
        data = json.loads(json_str)
        return ExtractedContent(**data)

    def _get_current_storage_bytes(self) -> int:
        """Calculate current storage usage in bytes.

        Returns:
            Total size of all cache entries in bytes
        """
        return sum(entry.size_bytes for entry in self._cache.values())

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache.

        This method should be called while holding the lock.
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if entry.expires_at <= current_time
        ]

        for key in expired_keys:
            del self._cache[key]
            self._stats["expirations"] += 1

        if expired_keys:
            logger.debug(
                "Cleaned up expired cache entries",
                extra={"count": len(expired_keys)},
            )

    def _evict_lru(self, bytes_needed: int) -> None:
        """Evict least recently used entries to free up space.

        This method should be called while holding the lock.

        Args:
            bytes_needed: Number of bytes that need to be freed
        """
        bytes_freed = 0
        evicted_count = 0

        # Sort by last_accessed (oldest first)
        sorted_items = sorted(self._cache.items(), key=lambda x: x[1].last_accessed)

        for key, entry in sorted_items:
            if bytes_freed >= bytes_needed:
                break

            bytes_freed += entry.size_bytes
            del self._cache[key]
            evicted_count += 1
            self._stats["evictions"] += 1

        if evicted_count > 0:
            logger.info(
                "Evicted LRU cache entries",
                extra={
                    "evicted_count": evicted_count,
                    "bytes_freed": bytes_freed,
                },
            )

    def get(self, url: str) -> ExtractedContent | None:
        """Retrieve content from cache.

        Args:
            url: URL to look up

        Returns:
            ExtractedContent if found and not expired, None otherwise
        """
        cache_key = self._make_cache_key(url)

        with self._lock:
            # Cleanup expired entries
            self._cleanup_expired()

            # Try to get from cache
            entry = self._cache.get(cache_key)

            if entry is None:
                self._stats["misses"] += 1
                logger.debug("Cache miss", extra={"url": url})
                return None

            # Check if expired
            if entry.expires_at <= time.time():
                del self._cache[cache_key]
                self._stats["misses"] += 1
                self._stats["expirations"] += 1
                logger.debug("Cache expired", extra={"url": url})
                return None

            # Update access time and move to end (for LRU)
            entry.last_accessed = time.time()
            self._cache.move_to_end(cache_key)

            # Decompress and return
            self._stats["hits"] += 1
            logger.debug("Cache hit", extra={"url": url})

            try:
                content = self._decompress_content(entry.compressed_data)
                return content
            except Exception as e:
                # If decompression fails, remove from cache
                logger.error(
                    "Failed to decompress cached content",
                    extra={"url": url, "error": str(e)},
                )
                del self._cache[cache_key]
                self._stats["misses"] += 1
                return None

    def set(self, url: str, content: ExtractedContent) -> None:
        """Store content in cache.

        Args:
            url: URL to use as cache key
            content: ExtractedContent to cache
        """
        cache_key = self._make_cache_key(url)

        try:
            # Compress content
            compressed_data = self._compress_content(content)
            size_bytes = len(compressed_data)

            # Calculate expiration time
            expires_at = time.time() + self.ttl_seconds

            with self._lock:
                # Cleanup expired entries first
                self._cleanup_expired()

                # Check if we need to evict entries
                current_storage = self._get_current_storage_bytes()

                # If entry already exists, subtract its size
                if cache_key in self._cache:
                    current_storage -= self._cache[cache_key].size_bytes

                # Calculate space needed
                space_needed = (current_storage + size_bytes) - self.max_storage_bytes

                if space_needed > 0:
                    # Need to evict LRU entries
                    self._evict_lru(space_needed)

                # Store in cache
                entry = CacheEntry(compressed_data, expires_at, size_bytes)
                self._cache[cache_key] = entry
                self._cache.move_to_end(cache_key)  # Move to end (most recent)

                logger.debug(
                    "Cached content",
                    extra={
                        "url": url,
                        "size_bytes": size_bytes,
                        "compression_ratio": round(
                            size_bytes / len(content.model_dump_json().encode("utf-8")),
                            2,
                        ),
                    },
                )

        except Exception as e:
            # Don't fail if caching fails - just log the error
            logger.error(
                "Failed to cache content",
                extra={"url": url, "error": str(e)},
            )

    def invalidate(self, url: str) -> bool:
        """Remove content from cache.

        Args:
            url: URL to invalidate

        Returns:
            True if entry was found and removed, False otherwise
        """
        cache_key = self._make_cache_key(url)

        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug("Invalidated cache entry", extra={"url": url})
                return True

            return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
            logger.info("Cleared cache", extra={"entries_removed": entry_count})

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - evictions: Number of LRU evictions
            - expirations: Number of expired entries removed
            - hit_rate: Cache hit rate as percentage
            - entry_count: Current number of entries
            - storage_bytes: Current storage usage in bytes
            - storage_mb: Current storage usage in MB
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                (self._stats["hits"] / total_requests * 100.0)
                if total_requests > 0
                else 0.0
            )

            storage_bytes = self._get_current_storage_bytes()

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "expirations": self._stats["expirations"],
                "hit_rate": round(hit_rate, 2),
                "entry_count": len(self._cache),
                "storage_bytes": storage_bytes,
                "storage_mb": round(storage_bytes / (1024 * 1024), 2),
            }
