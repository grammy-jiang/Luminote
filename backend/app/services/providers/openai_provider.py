"""OpenAI translation provider implementation."""

from typing import NoReturn

import httpx

from app.core.errors import (
    APIKeyError,
    InsufficientPermissionsError,
    ProviderTimeoutError,
    QuotaExceededError,
    RateLimitError,
    TranslationError,
)
from app.core.logging import logger
from app.services.providers.base import (
    BaseProvider,
    ModelCapabilitiesResult,
    TranslationResult,
    ValidationResult,
)


class OpenAIProvider(BaseProvider):
    """OpenAI translation provider implementation."""

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name "openai"
        """
        return "openai"

    def _handle_http_error(
        self, e: httpx.HTTPStatusError, model: str, operation: str
    ) -> NoReturn:
        """Handle HTTP errors from OpenAI API.

        Args:
            e: The HTTPStatusError from httpx
            model: Model identifier
            operation: Operation name for error messages (e.g., "translate", "validate")

        Raises:
            APIKeyError: If status is 401
            QuotaExceededError: If status is 402 or 429 with quota indicators
            InsufficientPermissionsError: If status is 403
            RateLimitError: If status is 429
            TranslationError: For other errors
        """
        status_code = e.response.status_code

        if status_code == 401:
            raise APIKeyError(
                provider="openai", reason="Invalid or expired API key"
            ) from e
        elif status_code == 402:
            # Payment required - quota exceeded
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get(
                    "message", "API quota exceeded"
                )
            except Exception:
                error_msg = "API quota exceeded"
            raise QuotaExceededError(provider="openai", reason=error_msg) from e
        elif status_code == 403:
            # Forbidden - insufficient permissions
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get(
                    "message", "Insufficient permissions"
                )
            except Exception:
                error_msg = "Insufficient permissions"
            raise InsufficientPermissionsError(
                provider="openai", reason=error_msg
            ) from e
        elif status_code == 429:
            # Try to extract retry-after from response headers first
            retry_after = 60  # Default
            if "retry-after" in e.response.headers:
                try:
                    retry_after = int(e.response.headers["retry-after"])
                except (ValueError, TypeError):
                    # Ignore invalid Retry-After header value and keep the default
                    pass
            # Also check for rate_limit_exceeded error type which may include quota info
            try:
                error_data = e.response.json()
                error_type = error_data.get("error", {}).get("type", "")
                # Check if this is a quota issue vs rate limit
                if (
                    "insufficient_quota" in error_type
                    or "quota" in error_data.get("error", {}).get("message", "").lower()
                ):
                    raise QuotaExceededError(
                        provider="openai",
                        reason=error_data.get("error", {}).get(
                            "message", "API quota exceeded"
                        ),
                    ) from e
            except QuotaExceededError:
                raise
            except Exception:
                # Failed to parse error response; treat as rate limit
                pass
            raise RateLimitError(retry_after=retry_after, provider="openai") from e
        elif status_code >= 500:
            raise TranslationError(
                provider="openai",
                model=model,
                reason=f"OpenAI API server error (status {status_code})",
            ) from e
        else:
            # Try to extract error message from response
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", str(e))
            except Exception:
                error_msg = str(e)
            raise TranslationError(
                provider="openai", model=model, reason=error_msg
            ) from e

    async def translate(
        self, text: str, target_language: str, model: str, api_key: str
    ) -> TranslationResult:
        """Translate text using OpenAI API.

        Args:
            text: Text to translate
            target_language: Target language code (ISO 639-1)
            model: OpenAI model identifier (e.g., "gpt-4", "gpt-4o-mini")
            api_key: User's OpenAI API key

        Returns:
            TranslationResult with translated text and metadata

        Raises:
            APIKeyError: If API key is invalid or missing
            RateLimitError: If rate limit is exceeded
            TranslationError: If translation fails
            LuminoteException: For other errors
        """
        # Validate API key format
        if not api_key or not api_key.startswith("sk-"):
            raise APIKeyError(
                provider="openai",
                reason="Invalid API key format (must start with 'sk-')",
            )

        # Construct translation prompt
        prompt = (
            f"Translate the following text to {target_language}. "
            f"Return ONLY the translated text without any explanation or additional text.\n\n"
            f"{text}"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,  # Lower temperature for more consistent translations
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract translation and token usage
                translated_text = data["choices"][0]["message"]["content"].strip()
                tokens_used = data["usage"]["total_tokens"]

                return TranslationResult(
                    translated_text=translated_text,
                    tokens_used=tokens_used,
                    model=model,
                    provider=self.get_provider_name(),
                )

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, model, "translate")

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(
                provider="openai", model=model, reason="Request timed out"
            ) from e

        except KeyError as e:
            raise TranslationError(
                provider="openai",
                model=model,
                reason=f"Unexpected API response format: {str(e)}",
            ) from e

        except Exception as e:
            raise TranslationError(
                provider="openai", model=model, reason=f"Unexpected error: {str(e)}"
            ) from e

    async def validate(self, model: str, api_key: str) -> ValidationResult:
        """Validate OpenAI API key and get model capabilities.

        Makes a minimal test API call to verify the API key is valid.
        Uses a single-word prompt to minimize cost.

        Args:
            model: OpenAI model identifier (e.g., "gpt-4", "gpt-4o-mini")
            api_key: User's OpenAI API key

        Returns:
            ValidationResult with validation status and model capabilities

        Raises:
            APIKeyError: If API key is invalid or missing (401)
            RateLimitError: If rate limit is exceeded (429)
            TranslationError: If validation fails
        """
        # Validate API key format
        if not api_key or not api_key.startswith("sk-"):
            raise APIKeyError(
                provider="openai",
                reason="Invalid API key format (must start with 'sk-')",
            )

        # Minimal test prompt (single word to minimize tokens/cost)
        test_prompt = "Hi"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": test_prompt}],
                        "max_tokens": 5,  # Minimal tokens to reduce cost
                        "temperature": 0.0,
                    },
                    timeout=10.0,  # 10-second timeout as per requirements
                )
                response.raise_for_status()
                # Note: We don't need to parse the response data, just verify it's valid
                # by checking that raise_for_status() didn't raise

                # Extract model capabilities from response
                # OpenAI models generally support streaming and have specific token limits
                # Map known models to their capabilities
                max_tokens_map = {
                    "gpt-4": 8192,
                    "gpt-4-32k": 32768,
                    "gpt-4-turbo": 128000,
                    "gpt-4-turbo-preview": 128000,
                    "gpt-4o": 128000,
                    "gpt-4o-mini": 16384,
                    "gpt-3.5-turbo": 4096,
                    "gpt-3.5-turbo-16k": 16384,
                }

                # Find matching model prefix for max tokens
                max_tokens = 4096  # Default fallback
                model_matched = False
                for model_prefix, tokens in max_tokens_map.items():
                    if model.startswith(model_prefix):
                        max_tokens = tokens
                        model_matched = True
                        break

                # Log when using fallback for unknown model
                if not model_matched:
                    logger.warning(
                        f"Unknown OpenAI model '{model}', using default max_tokens={max_tokens}",
                        extra={"model": model, "provider": "openai"},
                    )

                return ValidationResult(
                    valid=True,
                    provider=self.get_provider_name(),
                    model=model,
                    capabilities=ModelCapabilitiesResult(
                        streaming=True,  # All OpenAI chat models support streaming
                        max_tokens=max_tokens,
                    ),
                )

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, model, "validate")

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(
                provider="openai", model=model, reason="Validation request timed out"
            ) from e

        except KeyError as e:
            raise TranslationError(
                provider="openai",
                model=model,
                reason=f"Unexpected API response format: {str(e)}",
            ) from e

        except Exception as e:
            raise TranslationError(
                provider="openai", model=model, reason=f"Unexpected error: {str(e)}"
            ) from e
