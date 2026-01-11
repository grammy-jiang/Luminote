"""Tests for ExtractionService."""

import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from bs4 import BeautifulSoup

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
from app.schemas.extraction import ContentBlock
from app.services.extraction_service import ExtractionService

# Load sample HTML fixture
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
SAMPLE_HTML = (FIXTURES_DIR / "sample_articles.html").read_text()


@pytest.mark.unit
def test_extraction_service_init():
    """Test ExtractionService initialization."""
    service = ExtractionService()
    assert service.timeout == 30.0

    service_custom = ExtractionService(timeout=60.0)
    assert service_custom.timeout == 60.0


@pytest.mark.unit
def test_validate_url_valid():
    """Test URL validation with valid URLs."""
    service = ExtractionService()

    # Should not raise
    service._validate_url("https://example.com")
    service._validate_url("http://example.com")
    service._validate_url("https://example.com/path/to/article")
    service._validate_url("https://subdomain.example.com")
    service._validate_url("https://example.com:8080/path")


@pytest.mark.unit
def test_validate_url_invalid():
    """Test URL validation with invalid URLs."""
    service = ExtractionService()

    # Empty URL
    with pytest.raises(InvalidURLError):
        service._validate_url("")

    # Invalid scheme
    with pytest.raises(InvalidURLError):
        service._validate_url("ftp://example.com")

    # No scheme
    with pytest.raises(InvalidURLError):
        service._validate_url("example.com")

    # No domain
    with pytest.raises(InvalidURLError):
        service._validate_url("https://")

    # None value
    with pytest.raises(InvalidURLError):
        service._validate_url(None)  # type: ignore


@pytest.mark.unit
async def test_fetch_url_success():
    """Test successful URL fetching."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.headers = {"content-type": "text/html"}

        # Setup async context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await service._fetch_url("https://example.com")

        assert result == "<html><body>Test</body></html>"
        mock_client_instance.get.assert_called_once()
        call_args = mock_client_instance.get.call_args
        assert call_args[0][0] == "https://example.com"
        assert call_args[1]["follow_redirects"] is True


@pytest.mark.unit
async def test_fetch_url_timeout():
    """Test URL fetch timeout handling."""
    service = ExtractionService(timeout=5.0)

    with patch("httpx.AsyncClient") as mock_client:
        # Setup timeout exception
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.TimeoutException("Request timeout")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(URLFetchError) as exc_info:
            await service._fetch_url("https://example.com")

        assert exc_info.value.code == "URL_FETCH_ERROR"
        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_fetch_url_http_error():
    """Test URL fetch HTTP error handling."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not found", request=MagicMock(), response=mock_response
            )
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(URLFetchError) as exc_info:
            await service._fetch_url("https://example.com/notfound")

        assert exc_info.value.code == "URL_FETCH_ERROR"
        assert exc_info.value.status_code == 404  # 404 is preserved
        assert "404" in exc_info.value.message


@pytest.mark.unit
async def test_fetch_url_network_error():
    """Test URL fetch network error handling."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup network error
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.NetworkError("Connection refused")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(URLFetchError) as exc_info:
            await service._fetch_url("https://unreachable.example.com")

        assert exc_info.value.code == "URL_FETCH_ERROR"
        assert exc_info.value.status_code == 502
        assert "unreachable" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_fetch_url_non_html_content():
    """Test URL fetch with non-HTML content type."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response with PDF content type
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "PDF content"
        mock_response.headers = {"content-type": "application/pdf"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(ExtractionError) as exc_info:
            await service._fetch_url("https://example.com/document.pdf")

        assert exc_info.value.code == "EXTRACTION_ERROR"
        assert exc_info.value.status_code == 422
        assert "non-html" in exc_info.value.message.lower()


@pytest.mark.unit
def test_extract_with_readability():
    """Test Readability extraction."""
    service = ExtractionService()

    html = """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Main Heading</h1>
                <p>Article content here.</p>
            </article>
        </body>
    </html>
    """

    result = service._extract_with_readability(html, "https://example.com")

    assert "title" in result
    assert "content" in result
    assert result["title"] == "Test Article"


@pytest.mark.unit
def test_parse_html_to_blocks_paragraphs():
    """Test parsing HTML paragraphs to blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 2
    assert all(block.type == "paragraph" for block in blocks)
    assert blocks[0].text == "First paragraph."
    assert blocks[1].text == "Second paragraph."


@pytest.mark.unit
def test_parse_html_to_blocks_headings():
    """Test parsing HTML headings to blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <h3>Heading 3</h3>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 3
    assert all(block.type == "heading" for block in blocks)
    assert blocks[0].text == "Heading 1"
    assert blocks[0].metadata["level"] == 1
    assert blocks[1].text == "Heading 2"
    assert blocks[1].metadata["level"] == 2
    assert blocks[2].text == "Heading 3"
    assert blocks[2].metadata["level"] == 3


@pytest.mark.unit
def test_parse_html_to_blocks_lists():
    """Test parsing HTML lists to blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <ol>
            <li>Step 1</li>
            <li>Step 2</li>
        </ol>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 2
    assert all(block.type == "list" for block in blocks)

    # Unordered list
    assert blocks[0].metadata["list_type"] == "unordered"
    assert blocks[0].metadata["items"] == ["Item 1", "Item 2"]
    assert "• Item 1" in blocks[0].text
    assert "• Item 2" in blocks[0].text

    # Ordered list
    assert blocks[1].metadata["list_type"] == "ordered"
    assert blocks[1].metadata["items"] == ["Step 1", "Step 2"]
    assert "1. Step 1" in blocks[1].text
    assert "2. Step 2" in blocks[1].text


@pytest.mark.unit
def test_parse_html_to_blocks_quote():
    """Test parsing HTML blockquote to blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <blockquote>This is a quote from someone.</blockquote>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 1
    assert blocks[0].type == "quote"
    assert blocks[0].text == "This is a quote from someone."


@pytest.mark.unit
def test_parse_html_to_blocks_code():
    """Test parsing HTML code blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <pre><code class="language-python">
def hello():
    return "world"
        </code></pre>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 1
    assert blocks[0].type == "code"
    assert "def hello():" in blocks[0].text
    assert blocks[0].metadata.get("language") == "python"


@pytest.mark.unit
def test_parse_html_to_blocks_image():
    """Test parsing HTML image to blocks."""
    service = ExtractionService()

    html = """
    <html><body>
        <img src="https://example.com/image.jpg" alt="Test image" width="800" height="600">
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 1
    assert blocks[0].type == "image"
    assert blocks[0].text == "Test image"
    assert blocks[0].metadata["src"] == "https://example.com/image.jpg"
    assert blocks[0].metadata["alt"] == "Test image"
    assert blocks[0].metadata["width"] == "800"
    assert blocks[0].metadata["height"] == "600"


@pytest.mark.unit
def test_parse_html_to_blocks_skips_empty():
    """Test that empty elements are skipped."""
    service = ExtractionService()

    html = """
    <html><body>
        <p></p>
        <p>   </p>
        <p>Valid paragraph</p>
        <h1></h1>
        <h2>Valid heading</h2>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 2
    assert blocks[0].text == "Valid paragraph"
    assert blocks[1].text == "Valid heading"


@pytest.mark.unit
def test_extract_metadata():
    """Test metadata extraction from HTML."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <meta name="author" content="John Smith">
            <meta property="article:published_time" content="2024-01-15T10:30:00Z">
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    assert metadata["author"] == "John Smith"
    assert metadata["date_published"] == "2024-01-15T10:30:00Z"


@pytest.mark.unit
async def test_extract_full_workflow():
    """Test complete extraction workflow."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response with sample HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await service.extract("https://example.com/article")

        # Verify basic properties
        assert result.url == "https://example.com/article"
        assert result.title
        assert result.author == "Jane Doe"
        assert result.date_published == "2024-01-15T10:30:00Z"
        assert len(result.content_blocks) > 0

        # Verify block types
        block_types = {block.type for block in result.content_blocks}
        assert "paragraph" in block_types
        assert "heading" in block_types


@pytest.mark.unit
async def test_extract_invalid_url():
    """Test extraction with invalid URL."""
    service = ExtractionService()

    with pytest.raises(InvalidURLError):
        await service.extract("not-a-valid-url")


@pytest.mark.unit
async def test_extract_unreachable_url():
    """Test extraction with unreachable URL."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.NetworkError("Connection refused")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(URLFetchError) as exc_info:
            await service.extract("https://unreachable.test")

        assert exc_info.value.status_code == 502


@pytest.mark.unit
async def test_extract_timeout():
    """Test extraction with timeout."""
    service = ExtractionService(timeout=1.0)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(URLFetchError) as exc_info:
            await service.extract("https://slow.test")

        assert exc_info.value.status_code == 504


@pytest.mark.unit
async def test_extract_no_content():
    """Test extraction when no content blocks are extracted."""
    service = ExtractionService()

    empty_html = "<html><body></body></html>"

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = empty_html
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(ExtractionError) as exc_info:
            await service.extract("https://example.com/empty")

        assert "no content blocks" in exc_info.value.message.lower()


@pytest.mark.integration
@pytest.mark.skip(reason="Requires internet access - run manually")
async def test_extract_real_article():
    """Integration test with a real URL.

    This test is marked as integration and requires internet access. It can be skipped
    in CI/CD environments.
    """
    service = ExtractionService()

    # Use example.com as it's stable and always available
    result = await service.extract("https://example.com")

    assert result.url == "https://example.com"
    assert result.title
    assert len(result.content_blocks) > 0
    assert result.extraction_timestamp is not None


@pytest.mark.unit
def test_parse_html_to_blocks_empty_list():
    """Test that lists with no items are skipped."""
    service = ExtractionService()

    html = """
    <html><body>
        <ul></ul>
        <ol>
            <li></li>
            <li>   </li>
        </ol>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    # Both lists should be skipped because they're empty or contain only whitespace
    assert len(blocks) == 0


@pytest.mark.unit
def test_parse_html_to_blocks_empty_quote():
    """Test that empty blockquote is skipped."""
    service = ExtractionService()

    html = """
    <html><body>
        <blockquote></blockquote>
        <blockquote>   </blockquote>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 0


@pytest.mark.unit
def test_parse_html_to_blocks_image_without_src():
    """Test that images without src are skipped."""
    service = ExtractionService()

    html = """
    <html><body>
        <img alt="No source">
        <img src="" alt="Empty source">
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    # Both images should be skipped
    assert len(blocks) == 0


@pytest.mark.unit
def test_parse_html_to_blocks_code_without_language():
    """Test parsing code block without language class."""
    service = ExtractionService()

    html = """
    <html><body>
        <pre><code>
plain code without language
        </code></pre>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 1
    assert blocks[0].type == "code"
    assert "language" not in blocks[0].metadata


@pytest.mark.unit
def test_parse_html_to_blocks_standalone_code():
    """Test parsing standalone code element (not in pre)."""
    service = ExtractionService()

    html = """
    <html><body>
        <p>Some text with <code>inline code</code> here.</p>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    # Should only get the paragraph, not the inline code
    assert len(blocks) == 1
    assert blocks[0].type == "paragraph"


@pytest.mark.unit
def test_element_to_block_unknown_type():
    """Test that unknown element types return None."""
    service = ExtractionService()

    html = """
    <html><body>
        <div>This is a div</div>
        <span>This is a span</span>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    # div and span should not be converted to blocks
    assert len(blocks) == 0


@pytest.mark.unit
def test_extract_metadata_json_ld_author():
    """Test extracting author from JSON-LD."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "author": {
                    "@type": "Person",
                    "name": "JSON-LD Author"
                }
            }
            </script>
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    assert metadata["author"] == "JSON-LD Author"


@pytest.mark.unit
def test_extract_metadata_json_ld_author_string():
    """Test extracting author as string from JSON-LD."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "author": "String Author"
            }
            </script>
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    assert metadata["author"] == "String Author"


@pytest.mark.unit
def test_extract_metadata_json_ld_date():
    """Test extracting date from JSON-LD."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "datePublished": "2024-01-20T12:00:00Z"
            }
            </script>
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    assert metadata["date_published"] == "2024-01-20T12:00:00Z"


@pytest.mark.unit
def test_extract_metadata_invalid_json_ld():
    """Test that invalid JSON-LD doesn't break extraction."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {invalid json}
            </script>
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    # Should return empty dict without crashing
    assert isinstance(metadata, dict)


@pytest.mark.unit
def test_extract_metadata_date_meta_tag():
    """Test extracting date from meta name tag."""
    service = ExtractionService()

    html = """
    <html>
        <head>
            <meta name="date" content="2024-02-01">
        </head>
        <body>Content</body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = service._extract_metadata(soup, {}, [], [])

    assert metadata["date_published"] == "2024-02-01"


@pytest.mark.unit
async def test_extract_readability_failure():
    """Test handling of Readability extraction failure."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock Readability to raise an exception
        with patch("app.services.extraction_service.Document") as mock_doc:
            mock_doc.side_effect = Exception("Readability error")

            with pytest.raises(ExtractionError) as exc_info:
                await service.extract("https://example.com")

            assert "readability extraction failed" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_extract_block_parsing_failure():
    """Test handling of block parsing failure."""
    service = ExtractionService()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "<html><head><title>Test</title></head><body>Content</body></html>"
        )
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock _parse_html_to_blocks to raise an exception
        with patch.object(
            service, "_parse_html_to_blocks", side_effect=Exception("Parse error")
        ):
            with pytest.raises(ExtractionError) as exc_info:
                await service.extract("https://example.com")

            assert "block parsing failed" in exc_info.value.message.lower()


@pytest.mark.unit
async def test_news_article():
    """Test news article extraction with headlines, byline, pull quotes, and
    captions."""
    service = ExtractionService()

    # Load news article fixture
    NEWS_ARTICLE_HTML = (FIXTURES_DIR / "news_article.html").read_text()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response with news article HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = NEWS_ARTICLE_HTML
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await service.extract("https://example.com/news/article")

        # Verify basic properties
        assert result.url == "https://example.com/news/article"
        assert result.title
        assert result.author == "Sarah Johnson"
        assert result.date_published == "2024-01-20T14:30:00Z"

        # Verify article type is detected as news
        assert result.metadata.get("article_type") == "news"

        # Verify byline is extracted
        assert "byline" in result.metadata
        byline = result.metadata["byline"]
        assert "Sarah Johnson" in byline

        # Verify content blocks exist
        assert len(result.content_blocks) > 0

        # Verify headlines are extracted (H2 and H3, since H1 becomes title)
        headings = [b for b in result.content_blocks if b.type == "heading"]
        assert len(headings) > 0
        # Check for H2 headings
        h2_headings = [b for b in headings if b.metadata.get("level") == 2]
        assert len(h2_headings) >= 2
        # Check for specific section headings
        heading_texts = [h.text for h in headings]
        assert any("Discovery" in text for text in heading_texts)
        assert any("Industry" in text for text in heading_texts)

        # Verify images with captions are extracted
        images = [b for b in result.content_blocks if b.type == "image"]
        assert len(images) >= 2  # Should have at least 2 images
        # Check for captions
        images_with_captions = [b for b in images if b.metadata.get("caption")]
        assert len(images_with_captions) >= 2
        # Verify caption content
        captions = [img.metadata.get("caption", "") for img in images_with_captions]
        assert any(
            "Lead researcher" in caption or "Dr. Emily Chen" in caption
            for caption in captions
        )
        assert any(
            "Diagram" in caption or "internal structure" in caption
            for caption in captions
        )

        # Verify quotes exist
        quotes = [b for b in result.content_blocks if b.type == "quote"]
        assert len(quotes) >= 1

        # Verify regular quotes exist (not pull quotes in content blocks)
        # Pull quotes are extracted from original HTML, regular quotes from cleaned HTML
        regular_quotes = [
            b for b in quotes if not b.metadata.get("is_pull_quote", False)
        ]
        assert len(regular_quotes) >= 1
        # Check content of regular quote
        regular_quote_texts = [q.text for q in regular_quotes]
        assert any("Dr. Michael Torres" in text for text in regular_quote_texts)

        # Verify pull quotes are in metadata (extracted from original HTML)
        assert "pull_quotes" in result.metadata
        pull_quotes_list = result.metadata["pull_quotes"]
        assert len(pull_quotes_list) >= 2
        # Check content of pull quotes
        assert any(
            "change the entire renewable energy landscape" in pq
            for pq in pull_quotes_list
        )
        assert any("future of energy production" in pq for pq in pull_quotes_list)

        # Verify navigation and sidebar content is filtered out
        # Check that navigation items are not in content
        all_text = " ".join([b.text for b in result.content_blocks])
        # Navigation links should not appear
        assert "Trending Now" not in all_text
        # The actual content should be present
        assert "Scientists at the Advanced Research Institute" in all_text


@pytest.mark.unit
def test_is_navigation_or_sidebar():
    """Test navigation and sidebar detection."""
    service = ExtractionService()

    # Test nav element
    html = "<nav><p>Navigation</p></nav>"
    soup = BeautifulSoup(html, "lxml")
    nav_p = soup.find("p")
    assert service._is_navigation_or_sidebar(nav_p) is True

    # Test aside element
    html = "<aside><p>Sidebar</p></aside>"
    soup = BeautifulSoup(html, "lxml")
    aside_p = soup.find("p")
    assert service._is_navigation_or_sidebar(aside_p) is True

    # Test element with navigation class
    html = '<div class="site-navigation"><p>Nav</p></div>'
    soup = BeautifulSoup(html, "lxml")
    nav_div_p = soup.find("p")
    assert service._is_navigation_or_sidebar(nav_div_p) is True

    # Test element with sidebar class
    html = '<div class="sidebar"><p>Side</p></div>'
    soup = BeautifulSoup(html, "lxml")
    sidebar_div_p = soup.find("p")
    assert service._is_navigation_or_sidebar(sidebar_div_p) is True

    # Test regular content
    html = "<article><p>Content</p></article>"
    soup = BeautifulSoup(html, "lxml")
    article_p = soup.find("p")
    assert service._is_navigation_or_sidebar(article_p) is False


@pytest.mark.unit
def test_is_pull_quote():
    """Test pull quote detection."""
    service = ExtractionService()

    # Test blockquote with pullquote class
    html = '<blockquote class="pullquote">Quote text</blockquote>'
    soup = BeautifulSoup(html, "lxml")
    blockquote = soup.find("blockquote")
    assert service._is_pull_quote(blockquote) is True

    # Test blockquote inside aside with pull quote class
    html = '<aside class="pull-quote"><blockquote>Quote text</blockquote></aside>'
    soup = BeautifulSoup(html, "lxml")
    blockquote = soup.find("blockquote")
    assert service._is_pull_quote(blockquote) is True

    # Test regular blockquote
    html = "<blockquote>Regular quote</blockquote>"
    soup = BeautifulSoup(html, "lxml")
    blockquote = soup.find("blockquote")
    assert service._is_pull_quote(blockquote) is False


@pytest.mark.unit
def test_detect_article_type():
    """Test article type detection."""
    service = ExtractionService()

    # Test NewsArticle in JSON-LD
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "NewsArticle",
                "headline": "Test"
            }
            </script>
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_article_type(soup) == "news"

    # Test og:type article
    html = """
    <html>
        <head>
            <meta property="og:type" content="article">
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_article_type(soup) == "news"

    # Test no article type
    html = "<html><head></head></html>"
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_article_type(soup) is None


@pytest.mark.unit
def test_extract_byline():
    """Test byline extraction."""
    service = ExtractionService()

    # Test with byline class
    html = '<p class="byline">By John Doe</p>'
    soup = BeautifulSoup(html, "lxml")
    byline = service._extract_byline(soup)
    assert byline == "By John Doe"

    # Test with author in paragraph containing "by"
    html = '<article><p>By <span class="author">Jane Smith</span></p></article>'
    soup = BeautifulSoup(html, "lxml")
    byline = service._extract_byline(soup)
    assert byline == "By Jane Smith"

    # Test with no byline
    html = "<html><body><p>Regular content</p></body></html>"
    soup = BeautifulSoup(html, "lxml")
    byline = service._extract_byline(soup)
    assert byline is None


@pytest.mark.unit
def test_extract_pull_quotes_from_html():
    """Test pull quote extraction from HTML."""
    service = ExtractionService()

    # Test with pull quote classes
    html = """
    <html>
        <body>
            <blockquote class="pullquote">First pull quote</blockquote>
            <aside class="pull-quote"><blockquote>Second pull quote</blockquote></aside>
            <blockquote>Regular quote</blockquote>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    pull_quotes = service._extract_pull_quotes_from_html(soup)

    assert len(pull_quotes) == 2
    assert "First pull quote" in pull_quotes
    assert "Second pull quote" in pull_quotes
    assert "Regular quote" not in pull_quotes


@pytest.mark.unit
def test_parse_html_to_blocks_with_figure():
    """Test parsing HTML figure with caption."""
    service = ExtractionService()

    html = """
    <html><body>
        <figure>
            <img src="https://example.com/photo.jpg" alt="Photo alt text">
            <figcaption>This is the caption text</figcaption>
        </figure>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    assert len(blocks) == 1
    assert blocks[0].type == "image"
    assert blocks[0].text == "This is the caption text"
    assert blocks[0].metadata["src"] == "https://example.com/photo.jpg"
    assert blocks[0].metadata["alt"] == "Photo alt text"
    assert blocks[0].metadata["caption"] == "This is the caption text"


@pytest.mark.unit
def test_parse_html_to_blocks_filters_navigation():
    """Test that navigation elements are filtered out."""
    service = ExtractionService()

    html = """
    <html><body>
        <nav>
            <p>Navigation link</p>
        </nav>
        <aside class="sidebar">
            <p>Sidebar content</p>
        </aside>
        <article>
            <p>Main content</p>
        </article>
    </body></html>
    """

    blocks = service._parse_html_to_blocks(html)

    # Only main content should be extracted
    assert len(blocks) == 1
    assert blocks[0].text == "Main content"


@pytest.mark.unit
async def test_blog_post():
    """Test blog post extraction with title, author, date, tags, and filtered
    comments."""
    service = ExtractionService()

    # Load blog post fixture
    BLOG_POST_HTML = (FIXTURES_DIR / "blog_post.html").read_text()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response with blog post HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = BLOG_POST_HTML
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await service.extract("https://example.com/blog/react-guide")

        # Verify basic properties
        assert result.url == "https://example.com/blog/react-guide"
        assert result.title
        assert "React" in result.title
        assert result.author == "Alex Thompson"
        assert result.date_published == "2024-01-25T09:15:00Z"

        # Verify article type is detected as blog
        assert result.metadata.get("article_type") == "blog"

        # Verify tags are extracted
        assert "tags" in result.metadata
        tags = result.metadata["tags"]
        assert isinstance(tags, list)
        assert len(tags) == 4
        assert "web development" in tags
        assert "javascript" in tags
        assert "react" in tags
        assert "tutorial" in tags

        # Verify content blocks exist
        assert len(result.content_blocks) > 0

        # Verify headings are extracted
        headings = [b for b in result.content_blocks if b.type == "heading"]
        assert len(headings) > 0
        # Check for specific section headings
        heading_texts = [h.text for h in headings]
        assert any("Getting Started" in text for text in heading_texts)
        assert any("Core Concepts" in text for text in heading_texts)

        # Verify code blocks are preserved
        code_blocks = [b for b in result.content_blocks if b.type == "code"]
        assert len(code_blocks) >= 1
        # Check for language detection
        assert any(b.metadata.get("language") == "javascript" for b in code_blocks)

        # Verify lists are extracted
        lists = [b for b in result.content_blocks if b.type == "list"]
        assert len(lists) >= 2  # At least 2 lists in the blog post

        # Verify images with captions are preserved
        images = [b for b in result.content_blocks if b.type == "image"]
        assert len(images) >= 2
        # Check for captions
        images_with_captions = [b for b in images if b.metadata.get("caption")]
        assert len(images_with_captions) >= 2

        # Verify quotes exist
        quotes = [b for b in result.content_blocks if b.type == "quote"]
        assert len(quotes) >= 1

        # Verify comments section is filtered out
        all_text = " ".join([b.text for b in result.content_blocks])
        # Comments should not appear
        assert "User123" not in all_text
        assert "DevGuru" not in all_text
        assert "Great article! Very helpful" not in all_text
        # The actual content should be present
        assert "React has revolutionized" in all_text

        # Verify sidebar content is filtered out
        assert "Popular Posts" not in all_text
        assert "You Might Also Like" not in all_text


@pytest.mark.unit
def test_is_navigation_or_sidebar_filters_comments():
    """Test that comments sections are filtered out."""
    service = ExtractionService()

    # Test comments class
    html = '<section class="comments-section"><p>Comment text</p></section>'
    soup = BeautifulSoup(html, "lxml")
    p = soup.find("p")
    assert service._is_navigation_or_sidebar(p) is True

    # Test comment id
    html = '<div id="comments"><p>Comment text</p></div>'
    soup = BeautifulSoup(html, "lxml")
    p = soup.find("p")
    assert service._is_navigation_or_sidebar(p) is True

    # Test disqus
    html = '<div id="disqus_thread"><p>Comment text</p></div>'
    soup = BeautifulSoup(html, "lxml")
    p = soup.find("p")
    assert service._is_navigation_or_sidebar(p) is True

    # Test regular content is not filtered
    html = "<article><p>Article content</p></article>"
    soup = BeautifulSoup(html, "lxml")
    p = soup.find("p")
    assert service._is_navigation_or_sidebar(p) is False


@pytest.mark.unit
def test_detect_article_type_blog():
    """Test blog post type detection."""
    service = ExtractionService()

    # Test BlogPosting in JSON-LD
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "BlogPosting",
                "headline": "Test Blog"
            }
            </script>
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_article_type(soup) == "blog"

    # Test og:type blog
    html = """
    <html>
        <head>
            <meta property="og:type" content="blog">
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_article_type(soup) == "blog"


@pytest.mark.unit
def test_extract_tags():
    """Test tag extraction from blog posts."""
    service = ExtractionService()

    # Test with keywords meta tag
    html = """
    <html>
        <head>
            <meta name="keywords" content="python, django, web development">
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    assert len(tags) == 3
    assert "python" in tags
    assert "django" in tags
    assert "web development" in tags

    # Test with article:tag meta tags
    html = """
    <html>
        <head>
            <meta name="article:tag" content="javascript">
            <meta name="article:tag" content="react">
            <meta name="article:tag" content="frontend">
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    assert len(tags) == 3
    assert "javascript" in tags
    assert "react" in tags
    assert "frontend" in tags

    # Test with JSON-LD keywords (array)
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "BlogPosting",
                "keywords": ["ai", "machine learning", "python"]
            }
            </script>
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    assert len(tags) == 3
    assert "ai" in tags
    assert "machine learning" in tags
    assert "python" in tags

    # Test with JSON-LD keywords (string)
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "BlogPosting",
                "keywords": "golang, backend, api"
            }
            </script>
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    assert len(tags) == 3
    assert "golang" in tags
    assert "backend" in tags
    assert "api" in tags

    # Test with no tags
    html = "<html><head></head></html>"
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    assert len(tags) == 0

    # Test duplicate removal
    html = """
    <html>
        <head>
            <meta name="keywords" content="python, Django, web">
            <meta name="article:tag" content="python">
            <meta name="article:tag" content="django">
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    tags = service._extract_tags(soup)
    # Should have 3 unique tags (case-insensitive deduplication)
    assert len(tags) == 3
    assert "python" in tags
    assert "web" in tags
    # Either "Django" or "django" should be present (first occurrence wins)
    assert any(tag.lower() == "django" for tag in tags)


@pytest.mark.unit
async def test_technical_doc():
    """Test technical documentation extraction with special features."""
    service = ExtractionService()

    # Load technical doc fixture
    TECHNICAL_DOC_HTML = (FIXTURES_DIR / "technical_doc.html").read_text()

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock response with technical doc HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = TECHNICAL_DOC_HTML
        mock_response.headers = {"content-type": "text/html"}

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await service.extract("https://example.com/docs/fastapi-guide")

        # Verify basic properties
        assert result.url == "https://example.com/docs/fastapi-guide"
        assert result.title
        assert "FastAPI" in result.title

        # Verify article type is detected as technical
        assert result.metadata.get("article_type") == "technical"

        # Verify code languages are extracted
        assert "code_languages" in result.metadata
        code_languages = result.metadata["code_languages"]
        assert isinstance(code_languages, list)
        assert "python" in code_languages
        assert "bash" in code_languages
        # May also have json, typescript depending on extraction

        # Verify heading structure is preserved
        assert "heading_structure" in result.metadata
        heading_structure = result.metadata["heading_structure"]
        assert heading_structure["type"] == "root"
        assert "children" in heading_structure
        assert len(heading_structure["children"]) > 0

        # Verify nested headings (Getting Started -> Installation)
        root_children = heading_structure["children"]
        assert len(root_children) == 1  # Should have H1 as root

        h1 = root_children[0]
        assert h1["level"] == 1
        assert "FastAPI" in h1["text"]

        # Find Getting Started section (should be H2 under H1)
        getting_started = None
        for child in h1["children"]:
            if "Getting Started" in child.get("text", ""):
                getting_started = child
                break
        assert getting_started is not None
        assert getting_started["level"] == 2
        assert len(getting_started.get("children", [])) > 0

        # Verify nested H3s under Getting Started
        installation = None
        for child in getting_started["children"]:
            if "Installation" in child.get("text", ""):
                installation = child
                break
        assert installation is not None
        assert installation["level"] == 3

        # Verify reference links are extracted
        assert "reference_links" in result.metadata
        reference_links = result.metadata["reference_links"]
        assert isinstance(reference_links, list)
        assert len(reference_links) > 0
        # Check for specific reference links
        reference_texts = [link["text"] for link in reference_links]
        assert any("FastAPI" in text for text in reference_texts)

        # Verify API documentation is detected
        assert result.metadata.get("is_api_documentation") is True

        # Verify content blocks exist
        assert len(result.content_blocks) > 0

        # Verify headings with proper hierarchy
        headings = [b for b in result.content_blocks if b.type == "heading"]
        assert len(headings) >= 8  # Multiple heading levels

        # Check for specific headings at different levels
        h2_headings = [b for b in headings if b.metadata.get("level") == 2]
        assert len(h2_headings) >= 4  # Getting Started, Core Concepts, etc.

        h3_headings = [b for b in headings if b.metadata.get("level") == 3]
        assert len(h3_headings) >= 6  # Installation, First Application, etc.

        h4_headings = [b for b in headings if b.metadata.get("level") == 4]
        assert len(h4_headings) >= 2  # GET /users, POST /users

        # Verify code blocks are preserved with language info
        code_blocks = [b for b in result.content_blocks if b.type == "code"]
        assert len(code_blocks) >= 8  # Multiple code examples

        # Check that languages are detected
        code_with_lang = [
            b for b in code_blocks if b.metadata.get("language") is not None
        ]
        assert len(code_with_lang) >= 6

        # Check for specific languages
        python_blocks = [
            b for b in code_blocks if b.metadata.get("language") == "python"
        ]
        assert len(python_blocks) >= 5

        bash_blocks = [b for b in code_blocks if b.metadata.get("language") == "bash"]
        assert len(bash_blocks) >= 2

        # Verify line numbers are removed from code
        for code_block in code_blocks:
            # Code should not contain patterns like "1. " at start of lines
            lines = code_block.text.split("\n")
            for line in lines:
                # Allow empty lines and lines with content, but not "1. pip install"
                if line.strip():
                    assert not re.match(r"^\s*\d+[.:]\s", line), (
                        f"Line number found in code: {line}"
                    )

        # Verify tabbed content is handled
        # Should have code from both Python and TypeScript tabs
        all_code_text = " ".join([b.text for b in code_blocks])
        # Python example from tab
        assert "async def read_user" in all_code_text
        # TypeScript example from tab
        assert "req.params.userId" in all_code_text or "typescript" in code_languages

        # Verify lists are extracted
        lists = [b for b in result.content_blocks if b.type == "list"]
        assert len(lists) >= 2  # At least 2 lists in the doc

        # Verify API endpoint structure is captured in headings
        heading_texts = [h.text for h in headings]
        assert any("GET /users" in text for text in heading_texts)
        assert any("POST /users" in text for text in heading_texts)


@pytest.mark.unit
def test_remove_line_numbers():
    """Test line number removal from code blocks."""
    service = ExtractionService()

    # Test with numbered lines (period separator) - consecutive numbers
    code_with_numbers = """1. pip install fastapi
2. pip install uvicorn"""
    cleaned = service._remove_line_numbers(code_with_numbers)
    assert (
        cleaned
        == """pip install fastapi
pip install uvicorn"""
    )

    # Test with numbered lines (colon separator) - consecutive numbers
    code_with_colons = """1: import fastapi
2: from fastapi import FastAPI"""
    cleaned = service._remove_line_numbers(code_with_colons)
    assert (
        cleaned
        == """import fastapi
from fastapi import FastAPI"""
    )

    # Test with indented line numbers - consecutive numbers
    code_indented = """  1. def hello():
  2.     return "world" """
    cleaned = service._remove_line_numbers(code_indented)
    assert (
        cleaned
        == """  def hello():
      return "world" """
    )

    # Test code without line numbers (should remain unchanged)
    code_no_numbers = """def test():
    pass"""
    cleaned = service._remove_line_numbers(code_no_numbers)
    assert cleaned == code_no_numbers

    # Test with non-consecutive numbers (should remain unchanged to avoid false positives)
    code_non_consecutive = """1. first line
3. third line"""
    cleaned = service._remove_line_numbers(code_non_consecutive)
    assert cleaned == code_non_consecutive

    # Test with sparse line numbers (less than 50% of lines, should remain unchanged)
    code_sparse = """def function():
1. line with number
    return value"""
    cleaned = service._remove_line_numbers(code_sparse)
    assert cleaned == code_sparse

    # Test with floating point literals (should remain unchanged)
    code_with_floats = """result = [1. + x, 2. * y]
other_line = 3. / z"""
    cleaned = service._remove_line_numbers(code_with_floats)
    assert cleaned == code_with_floats


@pytest.mark.unit
def test_build_heading_structure():
    """Test heading structure building for technical docs."""
    service = ExtractionService()

    # Create sample content blocks with headings
    blocks = [
        ContentBlock(
            id="h1",
            type="heading",
            text="Introduction",
            metadata={"level": 1},
        ),
        ContentBlock(
            id="p1",
            type="paragraph",
            text="Some content",
            metadata={},
        ),
        ContentBlock(
            id="h2",
            type="heading",
            text="Getting Started",
            metadata={"level": 2},
        ),
        ContentBlock(
            id="h3-1",
            type="heading",
            text="Installation",
            metadata={"level": 3},
        ),
        ContentBlock(
            id="h3-2",
            type="heading",
            text="Configuration",
            metadata={"level": 3},
        ),
        ContentBlock(
            id="h2-2",
            type="heading",
            text="Advanced Topics",
            metadata={"level": 2},
        ),
    ]

    structure = service._build_heading_structure(blocks)

    # Verify root structure
    assert structure["type"] == "root"
    assert len(structure["children"]) == 1  # Only H1

    # Verify H1
    h1 = structure["children"][0]
    assert h1["text"] == "Introduction"
    assert h1["level"] == 1
    assert len(h1["children"]) == 2  # Two H2s

    # Verify first H2
    h2_1 = h1["children"][0]
    assert h2_1["text"] == "Getting Started"
    assert h2_1["level"] == 2
    assert len(h2_1["children"]) == 2  # Two H3s

    # Verify H3s
    assert h2_1["children"][0]["text"] == "Installation"
    assert h2_1["children"][1]["text"] == "Configuration"

    # Verify second H2
    h2_2 = h1["children"][1]
    assert h2_2["text"] == "Advanced Topics"
    assert h2_2["level"] == 2


@pytest.mark.unit
def test_extract_code_languages():
    """Test code language extraction."""
    service = ExtractionService()

    blocks = [
        ContentBlock(
            id="c1",
            type="code",
            text="print('hello')",
            metadata={"language": "python"},
        ),
        ContentBlock(
            id="c2",
            type="code",
            text="console.log('hello')",
            metadata={"language": "javascript"},
        ),
        ContentBlock(
            id="c3",
            type="code",
            text="echo 'hello'",
            metadata={"language": "bash"},
        ),
        ContentBlock(
            id="c4",
            type="code",
            text="SELECT * FROM users",
            metadata={},  # No language
        ),
        ContentBlock(
            id="c5",
            type="code",
            text="more python",
            metadata={"language": "python"},  # Duplicate
        ),
    ]

    languages = service._extract_code_languages(blocks)

    # Should be sorted and deduplicated
    assert languages == ["bash", "javascript", "python"]


@pytest.mark.unit
def test_detect_api_documentation():
    """Test API documentation detection."""
    service = ExtractionService()

    # Test with API class
    html = '<article class="api-documentation"><p>Content</p></article>'
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_api_documentation(soup) is True

    # Test with endpoint patterns
    html = """
    <html>
        <body>
            <h3>GET /users</h3>
            <h3>POST /users</h3>
            <h3>DELETE /users/{id}</h3>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_api_documentation(soup) is True

    # Test without API indicators
    html = "<html><body><h3>Regular Heading</h3></body></html>"
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_api_documentation(soup) is False


@pytest.mark.unit
def test_extract_reference_links():
    """Test reference link extraction."""
    service = ExtractionService()

    html = """
    <html>
        <body>
            <h2>References</h2>
            <ul>
                <li><a href="https://example.com/doc1">Documentation 1</a></li>
                <li><a href="https://example.com/doc2">Documentation 2</a></li>
            </ul>
            <h2>See Also</h2>
            <p><a href="https://example.com/guide">Related Guide</a></p>
            <h2>Other Section</h2>
            <p><a href="https://example.com/other">Not a reference</a></p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    links = service._extract_reference_links(soup)

    # Should extract 3 links from References and See Also sections
    assert len(links) == 3
    link_texts = [link["text"] for link in links]
    assert "Documentation 1" in link_texts
    assert "Documentation 2" in link_texts
    assert "Related Guide" in link_texts
    assert "Not a reference" not in link_texts


@pytest.mark.unit
def test_detect_technical_article():
    """Test technical article detection."""
    service = ExtractionService()

    # Test with TechArticle schema
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "TechArticle",
                "headline": "Test"
            }
            </script>
        </head>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_technical_article(soup) is True

    # Test with multiple code blocks
    html = """
    <html>
        <body>
            <pre><code>code1</code></pre>
            <pre><code>code2</code></pre>
            <pre><code>code3</code></pre>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_technical_article(soup) is True

    # Test with technical keywords and structure
    html = """
    <html>
        <head><title>API Documentation Guide</title></head>
        <body>
            <h2>Section 1</h2>
            <h2>Section 2</h2>
            <h3>Subsection 1</h3>
            <h3>Subsection 2</h3>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_technical_article(soup) is True

    # Test regular article (should be False)
    html = """
    <html>
        <head><title>Regular Blog Post</title></head>
        <body><p>Content</p></body>
    </html>
    """
    soup = BeautifulSoup(html, "lxml")
    assert service._detect_technical_article(soup) is False


@pytest.mark.unit
def test_is_inside_tabbed_content():
    """Test detection of elements inside tabbed content."""
    service = ExtractionService()

    # Test element inside tabbed-content div
    html = '<div class="tabbed-content"><pre><code>test</code></pre></div>'
    soup = BeautifulSoup(html, "lxml")
    pre = soup.find("pre")
    assert service._is_inside_tabbed_content(pre) is True

    # Test element with data-tabs attribute
    html = '<div data-tabs="python,js"><code>test</code></div>'
    soup = BeautifulSoup(html, "lxml")
    code = soup.find("code")
    assert service._is_inside_tabbed_content(code) is True

    # Test regular element
    html = "<article><pre><code>test</code></pre></article>"
    soup = BeautifulSoup(html, "lxml")
    pre = soup.find("pre")
    assert service._is_inside_tabbed_content(pre) is False
