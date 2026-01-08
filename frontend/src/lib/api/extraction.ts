/**
 * Content extraction API service.
 *
 * Provides methods for extracting content from web pages.
 * Used for the left pane content extraction feature.
 */

import { apiClient } from '$lib/utils/api';
import type { APIResponse, ExtractionRequest, ExtractionResponse } from '$lib/types/api';

/**
 * Extract content from a web page URL.
 *
 * @param request - Extraction request parameters
 * @returns Promise resolving to the extraction response
 * @throws {APIClientError} If extraction fails
 *
 * @example
 * ```typescript
 * const result = await extractContent({
 *   url: 'https://example.com/article',
 *   content_type: 'article'
 * });
 * console.log(result.data.content); // Extracted text content
 * console.log(result.data.title); // Page title
 * ```
 */
export async function extractContent(
	request: ExtractionRequest
): Promise<APIResponse<ExtractionResponse>> {
	return apiClient.post<ExtractionResponse>('/api/v1/extract', request);
}

/**
 * Extract content from a URL (simplified version).
 *
 * @param url - URL to extract content from
 * @returns Promise resolving to the extraction response
 * @throws {APIClientError} If extraction fails
 *
 * @example
 * ```typescript
 * const result = await extractFromURL('https://example.com/article');
 * console.log(result.data.content); // Extracted text content
 * ```
 */
export async function extractFromURL(url: string): Promise<APIResponse<ExtractionResponse>> {
	return extractContent({ url });
}

/**
 * Validate a URL before extraction.
 *
 * @param url - URL to validate
 * @returns Promise resolving to validation result
 *
 * @example
 * ```typescript
 * const result = await validateURL('https://example.com');
 * console.log(result.data.valid); // true or false
 * ```
 */
export async function validateURL(
	url: string
): Promise<APIResponse<{ valid: boolean; error?: string }>> {
	return apiClient.post<{ valid: boolean; error?: string }>('/api/v1/validate-url', { url });
}
