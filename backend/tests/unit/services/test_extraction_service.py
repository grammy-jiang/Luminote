"""Tests for ExtractionService."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from bs4 import BeautifulSoup

from app.core.errors import ExtractionError, InvalidURLError, URLFetchError
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
    metadata = service._extract_metadata(soup, {})

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
    metadata = service._extract_metadata(soup, {})

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
    metadata = service._extract_metadata(soup, {})

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
    metadata = service._extract_metadata(soup, {})

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
    metadata = service._extract_metadata(soup, {})

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
    metadata = service._extract_metadata(soup, {})

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
