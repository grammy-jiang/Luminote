"""Base provider abstract class for translation services.

This module defines the interface that all translation providers must implement.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    """Result from a translation operation."""

    translated_text: str = Field(..., description="The translated text")
    tokens_used: int = Field(..., description="Number of tokens used", ge=0)
    model: str = Field(..., description="Model used for translation")
    provider: str = Field(..., description="Provider name")


class ModelCapabilitiesResult(BaseModel):
    """Model capabilities for validation result."""

    streaming: bool = Field(..., description="Whether model supports streaming")
    max_tokens: int = Field(..., description="Maximum tokens supported", ge=0)


class ValidationResult(BaseModel):
    """Result from a validation operation."""

    valid: bool = Field(..., description="Whether the validation succeeded")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model identifier")
    capabilities: ModelCapabilitiesResult = Field(..., description="Model capabilities")


class BaseProvider(ABC):
    """Abstract base class for translation providers.

    All provider implementations (OpenAI, Anthropic, etc.) must inherit from this class
    and implement the translate method.
    """

    @abstractmethod
    async def translate(
        self, text: str, target_language: str, model: str, api_key: str
    ) -> TranslationResult:
        """Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code (ISO 639-1)
            model: Model identifier for the provider
            api_key: User's API key for authentication

        Returns:
            TranslationResult with translated text and metadata

        Raises:
            LuminoteException: On translation failure or API errors
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name (e.g., "openai", "anthropic")
        """
        pass

    @abstractmethod
    async def validate(self, model: str, api_key: str) -> ValidationResult:
        """Validate API key and get model capabilities.

        This method makes a minimal test API call to verify the API key is valid
        and retrieve model capabilities. Uses a minimal prompt to avoid charging
        the user significant costs.

        Args:
            model: Model identifier for the provider
            api_key: User's API key for authentication

        Returns:
            ValidationResult with validation status and model capabilities

        Raises:
            LuminoteException: On validation failure or API errors (401, 429, etc.)
        """
        pass
