"""Mock translation provider for testing."""

from app.services.providers.base import (
    BaseProvider,
    TranslationResult,
    ValidationResult,
)


class MockProvider(BaseProvider):
    """Mock translation provider for testing.

    Returns a simple prefixed version of the input text without making any API calls.
    """

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name "mock"
        """
        return "mock"

    async def translate(
        self, text: str, target_language: str, model: str, api_key: str
    ) -> TranslationResult:
        """Mock translate that returns prefixed text.

        Args:
            text: Text to translate
            target_language: Target language code (ISO 639-1)
            model: Model identifier (ignored for mock)
            api_key: API key (ignored for mock)

        Returns:
            TranslationResult with prefixed text

        Raises:
            Never raises exceptions (for testing happy paths)
        """
        # Simple mock: prefix text with language code
        translated_text = f"[{target_language.upper()}] {text}"

        # Mock token count (roughly text length / 4)
        tokens_used = max(1, len(text) // 4)

        return TranslationResult(
            translated_text=translated_text,
            tokens_used=tokens_used,
            model=model,
            provider=self.get_provider_name(),
        )

    async def validate(self, model: str, api_key: str) -> ValidationResult:
        """Mock validate that always succeeds.

        Args:
            model: Model identifier
            api_key: API key (ignored for mock)

        Returns:
            ValidationResult with mock capabilities

        Raises:
            Never raises exceptions (for testing happy paths)
        """
        # Mock always validates successfully
        return ValidationResult(
            valid=True,
            provider=self.get_provider_name(),
            model=model,
            capabilities={
                "streaming": True,
                "max_tokens": 4096,
            },
        )
