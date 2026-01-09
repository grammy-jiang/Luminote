"""Content extraction service using Mozilla Readability.

This module provides functionality to extract clean, reader-mode content from URLs.
"""

import json
import re
import uuid
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
from app.core.logging import get_logger
from app.schemas.extraction import ContentBlock, ExtractedContent

logger = get_logger(__name__)


class ExtractionService:
    """Service for extracting structured content from URLs.

    Uses Mozilla Readability for article extraction and BeautifulSoup for HTML parsing
    and block detection.
    """

    def __init__(self, timeout: float = 30.0, user_agent: str | None = None) -> None:
        """Initialize the extraction service.

        Args:
            timeout: Request timeout in seconds (default: 30)
            user_agent: User-Agent header for HTTP requests (optional)
        """
        self.timeout = timeout
        self.user_agent = user_agent or self._get_default_user_agent()

    def _get_default_user_agent(self) -> str:
        """Get default User-Agent from settings.

        Returns:
            Default User-Agent string
        """
        from app.config import get_settings

        settings = get_settings()
        return settings.EXTRACTION_USER_AGENT

    def _validate_url(self, url: str) -> None:
        """Validate URL format.

        Args:
            url: URL to validate

        Raises:
            InvalidURLError: If URL format is invalid
        """
        if not url or not isinstance(url, str):
            raise InvalidURLError(url="(empty or invalid)")

        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise InvalidURLError(url=url) from e

        # Check scheme
        if parsed.scheme not in ("http", "https"):
            raise InvalidURLError(url=url)

        # Check netloc (domain)
        if not parsed.netloc:
            raise InvalidURLError(url=url)

    async def _fetch_url(self, url: str) -> str:
        """Fetch URL content via HTTP.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string

        Raises:
            URLFetchError: On network errors or timeout
            ExtractionError: On non-HTML content
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if "html" not in content_type:
                    raise ExtractionError(
                        url=url,
                        reason=f"Non-HTML content type: {content_type}",
                    )

                return response.text

        except httpx.TimeoutException as e:
            raise URLFetchError(
                url=url, reason="Request timeout", status_code=504
            ) from e
        except httpx.HTTPStatusError as e:
            # Preserve the original HTTP status code for 404s
            status_code = 404 if e.response.status_code == 404 else 502
            raise URLFetchError(
                url=url,
                reason=f"HTTP {e.response.status_code}",
                status_code=status_code,
            ) from e
        except httpx.NetworkError as e:
            raise URLFetchError(
                url=url, reason="Network error (unreachable host)", status_code=502
            ) from e
        except ExtractionError:
            # Re-raise ExtractionError as-is
            raise
        except Exception as e:
            raise URLFetchError(
                url=url, reason=f"Unexpected error: {str(e)}", status_code=502
            ) from e

    def _extract_with_readability(self, html: str, url: str) -> dict[str, Any]:
        """Extract article content using Readability.

        Args:
            html: Raw HTML content
            url: Source URL (for relative link resolution)

        Returns:
            Dictionary with title and cleaned HTML content
        """
        doc = Document(html, url=url)
        return {
            "title": doc.title(),
            "content": doc.summary(html_partial=False),
        }

    def _parse_html_to_blocks(self, html: str) -> list[ContentBlock]:
        """Parse HTML content into structured ContentBlock list.

        Args:
            html: HTML content to parse

        Returns:
            List of ContentBlock objects
        """
        soup = BeautifulSoup(html, "lxml")
        blocks: list[ContentBlock] = []

        # Find the body or main content area
        content_root = soup.find("body") or soup

        # Process each element
        for element in content_root.find_all(
            [
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "ul",
                "ol",
                "blockquote",
                "pre",
                "img",
            ]
        ):
            # Skip code elements that are inside pre elements
            if element.name == "code" and element.find_parent("pre"):
                continue

            block = self._element_to_block(element)
            if block:
                blocks.append(block)

        return blocks

    def _element_to_block(self, element: Any) -> ContentBlock | None:
        """Convert HTML element to ContentBlock.

        Args:
            element: BeautifulSoup element

        Returns:
            ContentBlock or None if element should be skipped
        """
        block_id = str(uuid.uuid4())

        # Heading
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(element.name[1])
            text = element.get_text(strip=True)
            if not text:
                return None
            return ContentBlock(
                id=block_id,
                type="heading",
                text=text,
                metadata={"level": level},
            )

        # Paragraph
        elif element.name == "p":
            text = element.get_text(strip=True)
            if not text:
                return None
            return ContentBlock(
                id=block_id,
                type="paragraph",
                text=text,
                metadata={},
            )

        # List (ul/ol)
        elif element.name in ["ul", "ol"]:
            # Extract list items
            items = [
                li.get_text(strip=True)
                for li in element.find_all("li", recursive=False)
            ]
            items = [item for item in items if item]  # Filter empty
            if not items:
                return None

            # Join items with newlines for text representation
            text = "\n".join(
                f"• {item}" if element.name == "ul" else f"{i + 1}. {item}"
                for i, item in enumerate(items)
            )

            return ContentBlock(
                id=block_id,
                type="list",
                text=text,
                metadata={
                    "list_type": "unordered" if element.name == "ul" else "ordered",
                    "items": items,
                },
            )

        # Blockquote
        elif element.name == "blockquote":
            text = element.get_text(strip=True)
            if not text:
                return None
            return ContentBlock(
                id=block_id,
                type="quote",
                text=text,
                metadata={},
            )

        # Code block (pre or code)
        elif element.name in ["pre", "code"]:
            text = element.get_text()  # Preserve whitespace in code
            if not text.strip():
                return None

            # Try to detect language
            language = None
            if element.name == "pre":
                code_elem = element.find("code")
                if code_elem and code_elem.get("class"):
                    # Common pattern: class="language-python"
                    for cls in code_elem.get("class", []):
                        if cls.startswith("language-"):
                            language = cls.replace("language-", "")
                            break

            metadata = {}
            if language:
                metadata["language"] = language

            return ContentBlock(
                id=block_id,
                type="code",
                text=text,
                metadata=metadata,
            )

        # Image
        elif element.name == "img":
            src = element.get("src", "")
            alt = element.get("alt", "")

            if not src:
                return None

            return ContentBlock(
                id=block_id,
                type="image",
                text=alt,  # Use alt text as the text content
                metadata={
                    "src": src,
                    "alt": alt,
                    "width": element.get("width"),
                    "height": element.get("height"),
                },
            )

        return None

    def _extract_metadata(
        self, soup: BeautifulSoup, readability_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract metadata from HTML.

        Args:
            soup: BeautifulSoup object
            readability_data: Data from Readability extraction

        Returns:
            Dictionary of metadata
        """
        metadata: dict[str, Any] = {}

        # Try to find author
        author = None
        # Look for common author meta tags
        author_meta = soup.find("meta", attrs={"name": re.compile(r"author", re.I)})
        if author_meta:
            author = author_meta.get("content")
        # Try JSON-LD
        if not author:
            json_ld = soup.find("script", attrs={"type": "application/ld+json"})
            if json_ld:
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, dict) and "author" in data:
                        author_data = data["author"]
                        if isinstance(author_data, dict):
                            author = author_data.get("name")
                        elif isinstance(author_data, str):
                            author = author_data
                except Exception:
                    # Ignore invalid JSON-LD - metadata is optional
                    pass

        if author:
            metadata["author"] = author

        # Try to find publication date
        date_published = None
        # Look for common date meta tags
        date_meta = soup.find("meta", attrs={"property": "article:published_time"})
        if not date_meta:
            date_meta = soup.find("meta", attrs={"name": re.compile(r"date", re.I)})
        if date_meta:
            date_published = date_meta.get("content")

        # Try JSON-LD for date
        if not date_published:
            json_ld = soup.find("script", attrs={"type": "application/ld+json"})
            if json_ld:
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, dict):
                        date_published = data.get("datePublished")
                except Exception:
                    # Ignore invalid JSON-LD - metadata is optional
                    pass

        if date_published:
            metadata["date_published"] = date_published

        return metadata

    async def extract(self, url: str) -> ExtractedContent:
        """Extract structured content from a URL.

        Args:
            url: URL to extract content from

        Returns:
            ExtractedContent with structured blocks and metadata

        Raises:
            InvalidURLError: If URL format is invalid (400)
            URLFetchError: If URL is unreachable or times out (502/504)
            ExtractionError: If content extraction fails (422)
        """
        # Validate URL format
        self._validate_url(url)

        # Fetch URL content
        html = await self._fetch_url(url)

        # Extract with Readability
        try:
            readability_data = self._extract_with_readability(html, url)
        except Exception as e:
            logger.error(
                "Readability extraction failed",
                extra={"url": url, "error": str(e), "error_type": type(e).__name__},
            )
            raise ExtractionError(
                url=url, reason=f"Readability extraction failed: {str(e)}"
            ) from e

        # Parse original HTML for metadata
        soup = BeautifulSoup(html, "lxml")
        metadata = self._extract_metadata(soup, readability_data)

        # Parse cleaned HTML into blocks
        try:
            content_blocks = self._parse_html_to_blocks(readability_data["content"])
        except Exception as e:
            raise ExtractionError(
                url=url, reason=f"Block parsing failed: {str(e)}"
            ) from e

        if not content_blocks:
            raise ExtractionError(url=url, reason="No content blocks extracted")

        # Build result
        return ExtractedContent(
            url=url,
            title=readability_data["title"] or "Untitled",
            author=metadata.get("author"),
            date_published=metadata.get("date_published"),
            content_blocks=content_blocks,
            metadata=metadata,
        )
