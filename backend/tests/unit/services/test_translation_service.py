"""Tests for TranslationService."""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.errors import LuminoteException
from app.schemas.translation import ContentBlock
from app.services.providers.base import BaseProvider, TranslationResult
from app.services.translation_service import ProviderFactory, TranslationService


class CustomTestProvider(BaseProvider):
    """Custom test provider for registration testing."""

    def get_provider_name(self) -> str:
        return "custom"

    async def translate(
        self, text: str, target_language: str, model: str, api_key: str
    ) -> TranslationResult:
        return TranslationResult(
            translated_text=f"[CUSTOM] {text}",
            tokens_used=10,
            model=model,
            provider="custom",
        )


@pytest.mark.unit
def test_provider_factory_get_openai():
    """Test getting OpenAI provider from factory."""
    provider = ProviderFactory.get_provider("openai")
    assert provider.get_provider_name() == "openai"


@pytest.mark.unit
def test_provider_factory_get_anthropic():
    """Test getting Anthropic provider from factory."""
    provider = ProviderFactory.get_provider("anthropic")
    assert provider.get_provider_name() == "anthropic"


@pytest.mark.unit
def test_provider_factory_get_mock():
    """Test getting mock provider from factory."""
    provider = ProviderFactory.get_provider("mock")
    assert provider.get_provider_name() == "mock"


@pytest.mark.unit
def test_provider_factory_case_insensitive():
    """Test that provider factory is case insensitive."""
    provider_lower = ProviderFactory.get_provider("openai")
    provider_upper = ProviderFactory.get_provider("OPENAI")
    provider_mixed = ProviderFactory.get_provider("OpenAI")

    assert provider_lower.get_provider_name() == "openai"
    assert provider_upper.get_provider_name() == "openai"
    assert provider_mixed.get_provider_name() == "openai"


@pytest.mark.unit
def test_provider_factory_unsupported_provider():
    """Test that unsupported provider raises exception."""
    with pytest.raises(LuminoteException) as exc_info:
        ProviderFactory.get_provider("unsupported")

    assert exc_info.value.code == "UNSUPPORTED_PROVIDER"
    assert "unsupported" in exc_info.value.message.lower()
    assert exc_info.value.status_code == 400


@pytest.mark.unit
async def test_translation_service_translate_block():
    """Test translating a single block."""
    service = TranslationService()

    block = ContentBlock(
        id="block-1", type="paragraph", text="Hello world", metadata={"key": "value"}
    )

    # Mock the provider
    with patch(
        "app.services.translation_service.ProviderFactory.get_provider"
    ) as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.translate.return_value = TranslationResult(
            translated_text="Hola mundo",
            tokens_used=25,
            model="gpt-4",
            provider="openai",
        )
        mock_get_provider.return_value = mock_provider

        result = await service.translate_block(
            block=block,
            target_language="es",
            provider="openai",
            model="gpt-4",
            api_key="sk-test",
        )

        # Verify result
        assert result.id == "block-1"
        assert result.type == "paragraph"
        assert result.text == "Hola mundo"
        assert result.metadata["provider"] == "openai"
        assert result.metadata["model"] == "gpt-4"
        assert result.metadata["tokens_used"] == 25
        assert result.metadata["key"] == "value"  # Original metadata preserved

        # Verify provider was called correctly
        mock_provider.translate.assert_called_once_with(
            text="Hello world",
            target_language="es",
            model="gpt-4",
            api_key="sk-test",
        )


@pytest.mark.unit
async def test_translation_service_translate_blocks():
    """Test translating multiple blocks."""
    service = TranslationService()

    blocks = [
        ContentBlock(id="block-1", type="paragraph", text="Hello", metadata={}),
        ContentBlock(id="block-2", type="heading", text="World", metadata={}),
    ]

    # Mock the provider
    with patch(
        "app.services.translation_service.ProviderFactory.get_provider"
    ) as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.translate.side_effect = [
            TranslationResult(
                translated_text="Hola", tokens_used=10, model="gpt-4", provider="openai"
            ),
            TranslationResult(
                translated_text="Mundo",
                tokens_used=10,
                model="gpt-4",
                provider="openai",
            ),
        ]
        mock_get_provider.return_value = mock_provider

        results = await service.translate_blocks(
            blocks=blocks,
            target_language="es",
            provider="openai",
            model="gpt-4",
            api_key="sk-test",
        )

        # Verify results
        assert len(results) == 2
        assert results[0].id == "block-1"
        assert results[0].text == "Hola"
        assert results[1].id == "block-2"
        assert results[1].text == "Mundo"

        # Verify provider was called for each block
        assert mock_provider.translate.call_count == 2


@pytest.mark.unit
async def test_translation_service_preserves_block_order():
    """Test that translation service preserves block order."""
    service = TranslationService()

    blocks = [
        ContentBlock(id=f"block-{i}", type="paragraph", text=f"Text {i}", metadata={})
        for i in range(5)
    ]

    # Mock the provider
    with patch(
        "app.services.translation_service.ProviderFactory.get_provider"
    ) as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.translate.side_effect = [
            TranslationResult(
                translated_text=f"Texto {i}",
                tokens_used=10,
                model="gpt-4",
                provider="openai",
            )
            for i in range(5)
        ]
        mock_get_provider.return_value = mock_provider

        results = await service.translate_blocks(
            blocks=blocks,
            target_language="es",
            provider="openai",
            model="gpt-4",
            api_key="sk-test",
        )

        # Verify order is preserved
        for i, result in enumerate(results):
            assert result.id == f"block-{i}"
            assert result.text == f"Texto {i}"


@pytest.mark.unit
async def test_translation_service_with_mock_provider():
    """Test translation service with mock provider."""
    service = TranslationService()

    block = ContentBlock(
        id="block-1", type="paragraph", text="Hello world", metadata={}
    )

    result = await service.translate_block(
        block=block,
        target_language="es",
        provider="mock",
        model="test-model",
        api_key="test-key",
    )

    # Mock provider just prefixes with language code
    assert result.text == "[ES] Hello world"
    assert result.metadata["provider"] == "mock"


@pytest.mark.unit
async def test_translation_service_propagates_provider_errors():
    """Test that service propagates provider errors."""
    service = TranslationService()

    block = ContentBlock(id="block-1", type="paragraph", text="Hello", metadata={})

    # Mock provider that raises an error
    with patch(
        "app.services.translation_service.ProviderFactory.get_provider"
    ) as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.translate.side_effect = LuminoteException(
            message="API error",
            code="API_ERROR",
            status_code=500,
        )
        mock_get_provider.return_value = mock_provider

        with pytest.raises(LuminoteException) as exc_info:
            await service.translate_block(
                block=block,
                target_language="es",
                provider="openai",
                model="gpt-4",
                api_key="sk-test",
            )

        assert exc_info.value.code == "API_ERROR"


@pytest.mark.unit
def test_provider_factory_register_provider():
    """Test registering a custom provider."""
    # Register custom provider
    ProviderFactory.register_provider("custom", CustomTestProvider)

    # Get the custom provider
    provider = ProviderFactory.get_provider("custom")
    assert provider.get_provider_name() == "custom"

    # Clean up - unregister (reset to original state)
    if "custom" in ProviderFactory._providers:
        del ProviderFactory._providers["custom"]


@pytest.mark.unit
async def test_translation_service_with_registered_provider():
    """Test using a registered custom provider."""
    service = TranslationService()

    # Register custom provider
    ProviderFactory.register_provider("custom", CustomTestProvider)

    try:
        block = ContentBlock(
            id="block-1", type="paragraph", text="Hello", metadata={}
        )

        result = await service.translate_block(
            block=block,
            target_language="es",
            provider="custom",
            model="test-model",
            api_key="test-key",
        )

        assert result.text == "[CUSTOM] Hello"
        assert result.metadata["provider"] == "custom"
    finally:
        # Clean up
        if "custom" in ProviderFactory._providers:
            del ProviderFactory._providers["custom"]
