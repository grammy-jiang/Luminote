"""OpenAI translation provider implementation."""

import httpx

from app.core.errors import APIKeyError, RateLimitError, TranslationError
from app.services.providers.base import BaseProvider, TranslationResult


class OpenAIProvider(BaseProvider):
    """OpenAI translation provider implementation."""

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name "openai"
        """
        return "openai"

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
            status_code = e.response.status_code

            if status_code == 401:
                raise APIKeyError(
                    provider="openai", reason="Invalid or expired API key"
                ) from e
            elif status_code == 429:
                # Try to extract retry-after from response
                retry_after = 60  # Default
                try:
                    error_data = e.response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        # OpenAI sometimes includes retry info in message
                        pass
                except Exception:
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

        except httpx.TimeoutException as e:
            raise TranslationError(
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
