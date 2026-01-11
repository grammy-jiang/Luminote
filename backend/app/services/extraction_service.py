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

        # First, handle tabbed content (common in technical docs)
        tabbed_containers = content_root.find_all(
            "div", class_=re.compile(r"(?:tab|tabbed)[-_]content", re.I)
        )
        tabbed_containers.extend(
            content_root.find_all("div", attrs={"data-tabs": True})
        )

        for tab_container in tabbed_containers:
            # Extract all code blocks from tabs
            tab_blocks = tab_container.find_all(["pre", "code"])
            for tab_block in tab_blocks:
                parent_pre = tab_block.find_parent("pre")
                if not parent_pre:
                    continue
                block = self._element_to_block(parent_pre)
                if block:
                    blocks.append(block)
            # Remove the tabbed container from the tree so its content
            # is not processed again in the main element loop below.
            tab_container.decompose()

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
                "figure",
            ]
        ):
            # Skip code elements that are inside pre elements
            if element.name == "code" and element.find_parent("pre"):
                continue

            # Skip img elements that are inside figure elements
            if element.name == "img" and element.find_parent("figure"):
                continue

            # Skip navigation and sidebar elements
            if self._is_navigation_or_sidebar(element):
                continue

            # Skip if already processed as part of tabbed content
            if self._is_inside_tabbed_content(element):
                continue

            block = self._element_to_block(element)
            if block:
                blocks.append(block)

        return blocks

    def _is_inside_tabbed_content(self, element: Any) -> bool:
        """Check if element is inside a tabbed content container.

        Args:
            element: BeautifulSoup element

        Returns:
            True if element is inside tabbed content
        """
        current = element
        while current:
            # Check for tabbed content classes
            classes = current.get("class", [])
            if isinstance(classes, list):
                class_str = " ".join(classes).lower()
                if "tabbed" in class_str or "tab-content" in class_str:
                    return True

            # Check for data-tabs attribute
            if current.get("data-tabs"):
                return True

            current = current.parent
            if current and current.name in ["body", "html", "[document]"]:
                break

        return False

    def _is_navigation_or_sidebar(self, element: Any) -> bool:
        """Check if element is part of navigation, sidebar, or comments.

        Args:
            element: BeautifulSoup element

        Returns:
            True if element should be filtered out
        """
        # Check if element or any parent has navigation/sidebar/comments indicators
        current = element
        while current:
            # Check tag names
            if current.name == "nav":
                return True

            # For aside elements, check if they're pull quotes before filtering
            if current.name == "aside":
                # Check if this aside contains pull quote indicators
                aside_classes = current.get("class", [])
                if isinstance(aside_classes, list):
                    aside_class_str = " ".join(aside_classes).lower()
                    # If aside has pull quote classes, don't filter it
                    if any(
                        keyword in aside_class_str
                        for keyword in ["pull", "pullquote", "highlight"]
                    ):
                        # This is a pull quote aside, don't filter
                        pass
                    else:
                        # Regular aside (sidebar), filter it out
                        return True
                else:
                    # No classes, treat as regular aside
                    return True

            # Check class names
            classes = current.get("class", [])
            if isinstance(classes, list):
                class_str = " ".join(classes).lower()
                if any(
                    keyword in class_str
                    for keyword in [
                        "nav",
                        "navigation",
                        "sidebar",
                        "side-bar",
                        "related",
                        "trending",
                        "menu",
                        "comment",
                        "comments",
                        "disqus",
                        "discourse",
                        "replies",
                    ]
                ):
                    return True

            # Check id
            element_id = current.get("id", "").lower()
            if any(
                keyword in element_id
                for keyword in [
                    "nav",
                    "sidebar",
                    "menu",
                    "related",
                    "trending",
                    "comment",
                    "comments",
                    "disqus",
                    "discourse",
                ]
            ):
                return True

            # Move to parent
            current = current.parent
            # Stop at body or html
            if current and current.name in ["body", "html", "[document]"]:
                break

        return False

    def _is_pull_quote(self, element: Any) -> bool:
        """Check if a blockquote is a pull quote.

        Pull quotes are typically styled differently and used for emphasis,
        often wrapped in aside or having specific class names.

        Args:
            element: BeautifulSoup element (blockquote)

        Returns:
            True if element is a pull quote
        """
        # Check if blockquote has pull quote class
        classes = element.get("class", [])
        if isinstance(classes, list):
            class_str = " ".join(classes).lower()
            if any(
                keyword in class_str for keyword in ["pull", "pullquote", "highlight"]
            ):
                return True

        # Check if blockquote is inside an aside with pull quote indicators
        parent = element.parent
        if parent and parent.name == "aside":
            parent_classes = parent.get("class", [])
            if isinstance(parent_classes, list):
                parent_class_str = " ".join(parent_classes).lower()
                if any(
                    keyword in parent_class_str
                    for keyword in ["pull", "pullquote", "highlight"]
                ):
                    return True

        return False

    def _remove_line_numbers(self, code_text: str) -> str:
        """Remove line numbers from code blocks.

        This method is intentionally conservative: it only strips prefixes that
        look like line numbers when most lines in the block follow the same
        pattern and their numbers are consecutive. This avoids corrupting
        legitimate code such as floating point literals (e.g. ``1. + x``) or
        ordered list markers in comments.

        Common patterns in technical documentation:
        - "1. code line"
        - "1: code line"
        - "  1. code line" (with leading spaces)

        Args:
            code_text: Raw code text that may contain line numbers

        Returns:
            Code text with line numbers removed when a consistent line number
            pattern is detected, otherwise the original text.
        """
        lines = code_text.split("\n")

        # Match: optional spaces, then digits, then . or :, then space, then rest
        pattern = re.compile(r"^(\s*)(\d+)[.:]\s(.*)$")

        matches: list[tuple[int, int, re.Match[str]]] = []
        for idx, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                number = int(match.group(2))
                matches.append((idx, number, match))

        # If we don't have enough lines that look numbered, or they are sparse,
        # leave the text unchanged to avoid false positives.
        if len(matches) < 2 or len(matches) < len(lines) / 2:
            return code_text

        # Ensure the detected numbers are consecutive in order of appearance
        numbers = [m[1] for m in matches]
        if not all(
            later == earlier + 1
            for earlier, later in zip(numbers, numbers[1:], strict=False)
        ):
            return code_text

        # At this point we are confident these are real line numbers - strip them.
        cleaned_lines: list[str] = []
        match_by_index = {idx: m for idx, _, m in matches}

        for idx, line in enumerate(lines):
            match = match_by_index.get(idx)
            if match:
                # Preserve indentation (group 1) and the rest of the line (group 3)
                cleaned_lines.append(f"{match.group(1)}{match.group(3)}")
            else:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _build_heading_structure(
        self, content_blocks: list[ContentBlock]
    ) -> dict[str, Any]:
        """Build nested heading structure for technical documentation.

        Creates a hierarchical structure of headings (H1-H6) that represents
        the document's organization. Handles malformed HTML gracefully by
        inserting missing parent levels when needed.

        Args:
            content_blocks: List of content blocks

        Returns:
            Nested dictionary representing heading hierarchy
        """
        structure: dict[str, Any] = {"type": "root", "children": []}
        stack: list[dict[str, Any]] = [structure]

        for block in content_blocks:
            if block.type == "heading":
                level = block.metadata.get("level", 1)
                node = {
                    "type": "heading",
                    "level": level,
                    "text": block.text,
                    "id": block.id,
                    "children": [],
                }

                # Pop stack until we find the parent level
                while len(stack) > 1 and stack[-1].get("level", 0) >= level:
                    stack.pop()

                # If there's a gap in heading levels (e.g., H1 followed by H3),
                # the current parent in the stack is still appropriate since we
                # want H3 to be a child of H1, not a sibling.

                # Add to current parent
                stack[-1]["children"].append(node)
                stack.append(node)

        return structure

    def _extract_code_languages(self, content_blocks: list[ContentBlock]) -> list[str]:
        """Extract all unique programming languages from code blocks.

        Args:
            content_blocks: List of content blocks

        Returns:
            Sorted list of unique language identifiers
        """
        languages = set()
        for block in content_blocks:
            if block.type == "code" and "language" in block.metadata:
                languages.add(block.metadata["language"])
        return sorted(languages)

    def _detect_api_documentation(self, soup: BeautifulSoup) -> bool:
        """Detect if content is API documentation.

        Looks for common API documentation patterns:
        - Classes like "api-documentation", "api-reference"
        - Multiple code blocks with endpoint patterns
        - Structured endpoint documentation (GET, POST, etc.)

        Args:
            soup: BeautifulSoup object

        Returns:
            True if content appears to be API documentation
        """
        # Check for API-related classes
        api_classes = soup.find_all(
            class_=re.compile(r"api[-_]?(doc|reference|endpoint)", re.I)
        )
        if api_classes:
            return True

        # Check for structured endpoint patterns (HTTP methods)
        http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        api_pattern_count = 0

        for heading in headings:
            heading_text = heading.get_text(strip=True)
            # Look for patterns like "GET /users" or "POST /api/items"
            for method in http_methods:
                if heading_text.startswith(method + " /"):
                    api_pattern_count += 1
                    break

        # If we find 2+ endpoint patterns, likely API docs
        return api_pattern_count >= 2

    def _extract_reference_links(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        """Extract reference links from documentation.

        Preserves links from "References", "See Also", or similar sections
        that are common in technical documentation.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of dictionaries with 'text' and 'url' keys
        """
        reference_links: list[dict[str, str]] = []

        # Look for reference sections
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            heading_text = heading.get_text(strip=True).lower()

            # Check if this is a reference section
            if any(
                keyword in heading_text
                for keyword in ["reference", "see also", "further reading", "links"]
            ):
                # Find the next sibling elements until we hit another heading
                current = heading.find_next_sibling()

                while current and current.name not in [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                ]:
                    # Extract links from lists or paragraphs
                    links = current.find_all("a", href=True)
                    for link in links:
                        href = link.get("href", "")
                        text = link.get_text(strip=True)
                        if href and text:
                            reference_links.append({"text": text, "url": href})

                    current = current.find_next_sibling()

        # Deduplicate by URL while preserving order of first occurrence
        seen_urls: set[str] = set()
        unique_reference_links: list[dict[str, str]] = []
        for link_info in reference_links:
            url = link_info.get("url")
            if not url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            unique_reference_links.append(link_info)

        return unique_reference_links

    def _detect_technical_article(self, soup: BeautifulSoup) -> bool:
        """Detect if content is a technical article/documentation.

        Criteria:
        - Multiple code blocks
        - Technical keywords in title/headings
        - Structured content with nested headings
        - TechArticle schema type

        Args:
            soup: BeautifulSoup object

        Returns:
            True if content is technical documentation
        """
        # Check for TechArticle in JSON-LD
        json_ld = soup.find("script", attrs={"type": "application/ld+json"})
        if json_ld:
            try:
                data = json.loads(json_ld.string or "")
                if isinstance(data, dict) and data.get("@type") == "TechArticle":
                    return True
            except (TypeError, json.JSONDecodeError, ValueError) as exc:
                logger.debug(
                    "Failed to parse JSON-LD while detecting TechArticle schema.",
                    exc_info=exc,
                )

        # Count logical code blocks without double-counting <pre><code> pairs
        pre_code_blocks = [
            pre for pre in soup.find_all("pre") if pre.find("code") is not None
        ]
        standalone_code_blocks = [
            code for code in soup.find_all("code") if code.find_parent("pre") is None
        ]
        code_block_count = len(pre_code_blocks) + len(standalone_code_blocks)
        if code_block_count >= 3:  # 3+ code blocks suggests technical content
            return True

        # Check for technical keywords in title/headings
        title = soup.find("title")
        if title:
            title_text = title.get_text().lower()
            technical_keywords = [
                "api",
                "documentation",
                "guide",
                "tutorial",
                "reference",
                "sdk",
                "library",
            ]
            if any(keyword in title_text for keyword in technical_keywords):
                # Also need multiple headings for structure
                headings = soup.find_all(["h2", "h3", "h4"])
                if len(headings) >= 4:
                    return True

        return False

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

            # Determine if this is a pull quote
            is_pull_quote = self._is_pull_quote(element)

            return ContentBlock(
                id=block_id,
                type="quote",
                text=text,
                metadata={"is_pull_quote": is_pull_quote},
            )

        # Code block (pre or code)
        elif element.name in ["pre", "code"]:
            text = element.get_text()  # Preserve whitespace in code
            if not text.strip():
                return None

            # Remove line numbers from code (common in technical docs)
            text = self._remove_line_numbers(text)

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

        # Figure (with caption support)
        elif element.name == "figure":
            # Extract image from figure
            img = element.find("img")
            if not img or not img.get("src"):
                return None

            src = img.get("src", "")
            alt = img.get("alt", "")

            # Extract caption from figcaption
            caption = ""
            figcaption = element.find("figcaption")
            if figcaption:
                caption = figcaption.get_text(strip=True)

            # Use caption as text if available, otherwise use alt text
            text = caption if caption else alt

            return ContentBlock(
                id=block_id,
                type="image",
                text=text,
                metadata={
                    "src": src,
                    "alt": alt,
                    "caption": caption,
                    "width": img.get("width"),
                    "height": img.get("height"),
                },
            )

        return None

    def _detect_article_type(self, soup: BeautifulSoup) -> str | None:
        """Detect the type of article from HTML metadata.

        Args:
            soup: BeautifulSoup object

        Returns:
            Article type string ("news", "blog") or None
        """
        # Check JSON-LD for article type
        json_ld = soup.find("script", attrs={"type": "application/ld+json"})
        if json_ld:
            try:
                data = json.loads(json_ld.string or "")
                if isinstance(data, dict):
                    article_type = data.get("@type", "")
                    if article_type == "NewsArticle":
                        return "news"
                    elif article_type == "BlogPosting":
                        return "blog"
            except (TypeError, json.JSONDecodeError, ValueError) as exc:
                # Best-effort JSON-LD parsing; log and continue on invalid JSON
                logger.debug(
                    "Failed to parse JSON-LD while detecting article type",
                    exc_info=exc,
                )

        # Check Open Graph type
        og_type = soup.find("meta", attrs={"property": "og:type"})
        if og_type:
            content = og_type.get("content", "").lower()
            if "blog" in content:
                return "blog"
            elif "article" in content:
                return "news"

        return None

    def _extract_byline(self, soup: BeautifulSoup) -> str | None:
        """Extract byline from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Byline text or None
        """
        # Look for common byline patterns
        byline_elem = soup.find(class_=re.compile(r"byline", re.I))
        if byline_elem:
            text = byline_elem.get_text(strip=True)
            return text if text else None

        # Look for author span/element in common locations
        author_elem = soup.find(class_=re.compile(r"author", re.I))
        if author_elem:
            # Get parent context if it looks like a byline
            parent = author_elem.parent
            if parent and parent.name in ["p", "div", "span"]:
                # Get text with some whitespace preserved to check for "by"
                parent_text = parent.get_text(separator=" ", strip=True)
                # Check if it contains "by" or similar patterns (case insensitive)
                if re.search(r"\bby\b", parent_text, re.I):
                    return parent_text if parent_text else None

        return None

    def _extract_pull_quotes_from_html(self, soup: BeautifulSoup) -> list[str]:
        """Extract pull quotes from original HTML.

        Pull quotes are identified by:
        - blockquote inside aside with pull-quote class
        - blockquote with pullquote/pull-quote class

        Args:
            soup: BeautifulSoup object of original HTML

        Returns:
            List of pull quote texts
        """
        pull_quotes = []

        # Find all blockquotes
        for blockquote in soup.find_all("blockquote"):
            # Check if blockquote has pull quote class
            classes = blockquote.get("class", [])
            if isinstance(classes, list):
                class_str = " ".join(classes).lower()
                if any(
                    keyword in class_str
                    for keyword in ["pull", "pullquote", "highlight"]
                ):
                    text = blockquote.get_text(strip=True)
                    if text:
                        pull_quotes.append(text)
                    continue

            # Check if blockquote is inside aside with pull quote indicators
            parent = blockquote.parent
            if parent and parent.name == "aside":
                parent_classes = parent.get("class", [])
                if isinstance(parent_classes, list):
                    parent_class_str = " ".join(parent_classes).lower()
                    if any(
                        keyword in parent_class_str
                        for keyword in ["pull", "pullquote", "highlight"]
                    ):
                        text = blockquote.get_text(strip=True)
                        if text:
                            pull_quotes.append(text)

        return pull_quotes

    def _extract_pull_quotes(self, content_blocks: list[ContentBlock]) -> list[str]:
        """Extract pull quotes from content blocks.

        Args:
            content_blocks: List of ContentBlock objects

        Returns:
            List of pull quote texts
        """
        pull_quotes = []
        for block in content_blocks:
            if block.type == "quote" and block.metadata.get("is_pull_quote"):
                pull_quotes.append(block.text)
        return pull_quotes

    def _extract_tags(self, soup: BeautifulSoup) -> list[str]:
        """Extract tags from blog post HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of tag strings (deduplicated case-insensitively)
        """
        tags = []
        seen = set()  # Track seen tags (lowercase) for case-insensitive deduplication

        # Try to extract from meta keywords
        keywords_meta = soup.find("meta", attrs={"name": "keywords"})
        if keywords_meta:
            content = keywords_meta.get("content", "")
            if content:
                # Split by comma and clean up
                for tag in content.split(","):
                    tag = tag.strip()
                    if tag and tag.lower() not in seen:
                        seen.add(tag.lower())
                        tags.append(tag)

        # Try to extract from article:tag meta tags
        article_tags = soup.find_all("meta", attrs={"name": "article:tag"})
        for tag_meta in article_tags:
            tag = tag_meta.get("content", "").strip()
            if tag and tag.lower() not in seen:
                seen.add(tag.lower())
                tags.append(tag)

        # Try to extract from JSON-LD keywords
        json_ld = soup.find("script", attrs={"type": "application/ld+json"})
        if json_ld:
            try:
                data = json.loads(json_ld.string or "")
                if isinstance(data, dict) and "keywords" in data:
                    keywords = data["keywords"]
                    if isinstance(keywords, list):
                        for kw in keywords:
                            if isinstance(kw, str):
                                kw = kw.strip()
                                if kw and kw.lower() not in seen:
                                    seen.add(kw.lower())
                                    tags.append(kw)
                    elif isinstance(keywords, str):
                        for kw in keywords.split(","):
                            kw = kw.strip()
                            if kw and kw.lower() not in seen:
                                seen.add(kw.lower())
                                tags.append(kw)
            except (TypeError, json.JSONDecodeError, ValueError):
                # Ignore invalid JSON-LD - tags are optional
                pass

        return tags

    def _extract_metadata(
        self,
        soup: BeautifulSoup,
        readability_data: dict[str, Any],
        content_blocks: list[ContentBlock],
        pull_quotes_from_html: list[str],
    ) -> dict[str, Any]:
        """Extract metadata from HTML.

        Args:
            soup: BeautifulSoup object
            readability_data: Data from Readability extraction
            content_blocks: Parsed content blocks
            pull_quotes_from_html: Pull quotes extracted from original HTML

        Returns:
            Dictionary of metadata
        """
        metadata: dict[str, Any] = {}

        # Detect article type (blog, news, or technical)
        article_type = self._detect_article_type(soup)

        # Check for technical documentation
        is_technical = self._detect_technical_article(soup)
        if is_technical and not article_type:
            article_type = "technical"

        if article_type:
            metadata["article_type"] = article_type

        # For technical documentation, add specialized metadata
        if article_type == "technical":
            # Extract code languages
            code_languages = self._extract_code_languages(content_blocks)
            if code_languages:
                metadata["code_languages"] = code_languages

            # Build heading structure
            heading_structure = self._build_heading_structure(content_blocks)
            if heading_structure.get("children"):
                metadata["heading_structure"] = heading_structure

            # Extract reference links
            reference_links = self._extract_reference_links(soup)
            if reference_links:
                metadata["reference_links"] = reference_links

            # Detect if this is API documentation
            is_api_doc = self._detect_api_documentation(soup)
            if is_api_doc:
                metadata["is_api_documentation"] = True

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

        # Extract byline (for news articles)
        byline = self._extract_byline(soup)
        if byline:
            metadata["byline"] = byline

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

        # Combine pull quotes from original HTML and content blocks
        pull_quotes_from_blocks = self._extract_pull_quotes(content_blocks)
        all_pull_quotes = list(set(pull_quotes_from_html + pull_quotes_from_blocks))

        if all_pull_quotes:
            metadata["pull_quotes"] = all_pull_quotes

        # Extract tags for blog posts
        if article_type == "blog":
            tags = self._extract_tags(soup)
            if tags:
                metadata["tags"] = tags

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

        # Parse original HTML for metadata extraction and pull quotes
        soup = BeautifulSoup(html, "lxml")

        # Extract pull quotes from original HTML (before Readability cleaning)
        pull_quotes_from_html = self._extract_pull_quotes_from_html(soup)

        # Parse cleaned HTML into blocks
        try:
            content_blocks = self._parse_html_to_blocks(readability_data["content"])
        except Exception as e:
            raise ExtractionError(
                url=url, reason=f"Block parsing failed: {str(e)}"
            ) from e

        if not content_blocks:
            raise ExtractionError(url=url, reason="No content blocks extracted")

        # Extract metadata (including pull quotes from both sources)
        metadata = self._extract_metadata(
            soup, readability_data, content_blocks, pull_quotes_from_html
        )

        # Build result
        return ExtractedContent(
            url=url,
            title=readability_data["title"] or "Untitled",
            author=metadata.get("author"),
            date_published=metadata.get("date_published"),
            content_blocks=content_blocks,
            metadata=metadata,
        )
