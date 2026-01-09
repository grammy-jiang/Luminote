"""Anthropic translation provider implementation."""

import httpx

from app.core.errors import APIKeyError, RateLimitError, TranslationError
from app.services.providers.base import BaseProvider, TranslationResult


class AnthropicProvider(BaseProvider):
    """Anthropic translation provider implementation."""

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name "anthropic"
        """
        return "anthropic"

    async def translate(
        self, text: str, target_language: str, model: str, api_key: str
    ) -> TranslationResult:
        """Translate text using Anthropic API.

        Args:
            text: Text to translate
            target_language: Target language code (ISO 639-1)
            model: Anthropic model identifier (e.g., "claude-3-5-sonnet-20241022")
            api_key: User's Anthropic API key

        Returns:
            TranslationResult with translated text and metadata

        Raises:
            APIKeyError: If API key is invalid or missing
            RateLimitError: If rate limit is exceeded
            TranslationError: If translation fails
            LuminoteException: For other errors
        """
        # Validate API key format
        if not api_key or not api_key.startswith("sk-ant-"):
            raise APIKeyError(
                provider="anthropic",
                reason="Invalid API key format (must start with 'sk-ant-')",
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
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4096,
                        "temperature": 0.3,  # Lower temperature for more consistent translations
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract translation and token usage
                # Anthropic returns content as array of objects
                translated_text = data["content"][0]["text"].strip()
                input_tokens = data["usage"]["input_tokens"]
                output_tokens = data["usage"]["output_tokens"]
                tokens_used = input_tokens + output_tokens

                return TranslationResult(
                    translated_text=translated_text,
                    tokens_used=tokens_used,
                    model=model,
                    provider=self.get_provider_name(),
                )

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            if status_code == 401:
                raise APIKeyError(
                    provider="anthropic", reason="Invalid or expired API key"
                ) from e
            elif status_code == 429:
                # Try to extract retry-after from response headers
                retry_after = 60  # Default
                if "retry-after" in e.response.headers:
                    try:
                        retry_after = int(e.response.headers["retry-after"])
                    except (ValueError, TypeError):
                        pass
                raise RateLimitError(
                    retry_after=retry_after, provider="anthropic"
                ) from e
            elif status_code >= 500:
                raise TranslationError(
                    provider="anthropic",
                    model=model,
                    reason=f"Anthropic API server error (status {status_code})",
                ) from e
            else:
                # Try to extract error message from response
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                except Exception:
                    error_msg = str(e)
                raise TranslationError(
                    provider="anthropic", model=model, reason=error_msg
                ) from e

        except httpx.TimeoutException as e:
            raise TranslationError(
                provider="anthropic", model=model, reason="Request timed out"
            ) from e

        except KeyError as e:
            raise TranslationError(
                provider="anthropic",
                model=model,
                reason=f"Unexpected API response format: {str(e)}",
            ) from e

        except Exception as e:
            raise TranslationError(
                provider="anthropic", model=model, reason=f"Unexpected error: {str(e)}"
            ) from e
