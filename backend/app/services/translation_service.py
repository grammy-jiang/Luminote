"""Translation service with multi-provider support."""

from app.core.errors import LuminoteException
from app.schemas.translation import ContentBlock
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.base import BaseProvider
from app.services.providers.mock_provider import MockProvider
from app.services.providers.openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for creating translation provider instances."""

    _providers: dict[str, type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "mock": MockProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseProvider:
        """Get a provider instance by name.

        Args:
            provider_name: Name of the provider (openai, anthropic, mock)

        Returns:
            Instance of the requested provider

        Raises:
            LuminoteException: If provider is not supported
        """
        provider_class = cls._providers.get(provider_name.lower())
        if provider_class is None:
            supported = ", ".join(cls._providers.keys())
            raise LuminoteException(
                message=f"Unsupported provider: {provider_name}. Supported providers: {supported}",
                code="UNSUPPORTED_PROVIDER",
                status_code=400,
                details={
                    "provider": provider_name,
                    "supported_providers": list(cls._providers.keys()),
                },
            )
        return provider_class()

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseProvider]) -> None:
        """Register a new provider (for testing or extensions).

        Args:
            name: Provider name
            provider_class: Provider class to register
        """
        cls._providers[name.lower()] = provider_class


class TranslationService:
    """Translation service with multi-provider support.

    This service abstracts provider differences and provides a unified interface for
    translating content blocks.
    """

    async def translate_block(
        self,
        block: ContentBlock,
        target_language: str,
        provider: str,
        model: str,
        api_key: str,
    ) -> ContentBlock:
        """Translate a single content block.

        Args:
            block: Content block to translate
            target_language: Target language code (ISO 639-1)
            provider: Provider name (openai, anthropic)
            model: Model identifier
            api_key: User's API key for the provider

        Returns:
            Content block with translated text and metadata

        Raises:
            LuminoteException: On translation failure
        """
        # Get the provider
        provider_instance = ProviderFactory.get_provider(provider)

        # Translate the text
        result = await provider_instance.translate(
            text=block.text,
            target_language=target_language,
            model=model,
            api_key=api_key,
        )

        # Create translated block with metadata
        translated_block = ContentBlock(
            id=block.id,
            type=block.type,
            text=result.translated_text,
            metadata={
                **block.metadata,
                "provider": result.provider,
                "model": result.model,
                "tokens_used": result.tokens_used,
            },
        )

        return translated_block

    async def translate_blocks(
        self,
        blocks: list[ContentBlock],
        target_language: str,
        provider: str,
        model: str,
        api_key: str,
    ) -> list[ContentBlock]:
        """Translate multiple content blocks.

        Args:
            blocks: List of content blocks to translate
            target_language: Target language code (ISO 639-1)
            provider: Provider name (openai, anthropic)
            model: Model identifier
            api_key: User's API key for the provider

        Returns:
            List of translated content blocks with metadata

        Raises:
            LuminoteException: On translation failure
        """
        translated_blocks = []

        for block in blocks:
            translated_block = await self.translate_block(
                block=block,
                target_language=target_language,
                provider=provider,
                model=model,
                api_key=api_key,
            )
            translated_blocks.append(translated_block)

        return translated_blocks
