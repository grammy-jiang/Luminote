/**
 * Translation API service.
 *
 * Provides methods for translating text using various AI providers.
 * All translations require user-provided API keys (BYOK).
 */

import { apiClient } from '$lib/utils/api';
import type { APIResponse, TranslationRequest, TranslationResponse } from '$lib/types/api';

/**
 * Translate text from one language to another.
 *
 * @param request - Translation request parameters
 * @returns Promise resolving to the translation response
 * @throws {APIClientError} If translation fails
 *
 * @example
 * ```typescript
 * const result = await translateText({
 *   text: 'Hello, world!',
 *   source_language: 'en',
 *   target_language: 'es',
 *   provider: 'openai',
 *   api_key: 'sk-...'
 * });
 * console.log(result.data.translated_text); // 'Hola, mundo!'
 * ```
 */
export async function translateText(
	request: TranslationRequest
): Promise<APIResponse<TranslationResponse>> {
	return apiClient.post<TranslationResponse>('/api/v1/translate', request);
}

/**
 * Translate text with streaming support (future feature).
 *
 * Note: This is a placeholder for future SSE streaming implementation.
 * See ADR-002: Streaming Translation Architecture.
 *
 * @param request - Translation request parameters
 * @param onChunk - Callback for each translated chunk
 * @returns Promise resolving when streaming completes
 */
export async function translateTextStreaming(
	request: TranslationRequest,
	onChunk: (chunk: string) => void
): Promise<void> {
	// TODO: Implement SSE streaming when backend endpoint is ready
	// For now, fall back to non-streaming translation
	const response = await translateText(request);
	onChunk(response.data.translated_text);
}

/**
 * Get list of supported AI providers.
 *
 * @returns Promise resolving to list of provider names
 *
 * @example
 * ```typescript
 * const providers = await getSupportedProviders();
 * console.log(providers.data); // ['openai', 'anthropic', 'google']
 * ```
 */
export async function getSupportedProviders(): Promise<APIResponse<string[]>> {
	return apiClient.get<string[]>('/api/v1/providers');
}

/**
 * Get list of supported languages for translation.
 *
 * @returns Promise resolving to list of language codes
 *
 * @example
 * ```typescript
 * const languages = await getSupportedLanguages();
 * console.log(languages.data); // ['en', 'es', 'fr', 'de', ...]
 * ```
 */
export async function getSupportedLanguages(): Promise<APIResponse<string[]>> {
	return apiClient.get<string[]>('/api/v1/languages');
}
