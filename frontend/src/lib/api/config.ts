/**
 * Configuration API service.
 *
 * Provides methods for managing user configuration and preferences.
 * Follows ADR-003: Client-Side Storage Strategy.
 */

import { apiClient } from '$lib/utils/api';
import type {
	APIResponse,
	ConfigSaveRequest,
	ConfigResponse,
	ConfigValidationRequest,
	ConfigValidationResponse
} from '$lib/types/api';

/**
 * Get a configuration value by key.
 *
 * @param key - Configuration key
 * @returns Promise resolving to the configuration value
 * @throws {APIClientError} If key doesn't exist or request fails
 *
 * @example
 * ```typescript
 * const result = await getConfig('default_provider');
 * console.log(result.data.value); // 'openai'
 * ```
 */
export async function getConfig(key: string): Promise<APIResponse<ConfigResponse>> {
	return apiClient.get<ConfigResponse>(`/api/v1/config/${key}`);
}

/**
 * Save a configuration value.
 *
 * @param request - Configuration save request
 * @returns Promise resolving to the saved configuration
 * @throws {APIClientError} If save fails
 *
 * @example
 * ```typescript
 * await saveConfig({
 *   key: 'default_provider',
 *   value: 'openai'
 * });
 * ```
 */
export async function saveConfig(request: ConfigSaveRequest): Promise<APIResponse<ConfigResponse>> {
	return apiClient.post<ConfigResponse>('/api/v1/config', request);
}

/**
 * Get all configuration values.
 *
 * @returns Promise resolving to all configuration values
 *
 * @example
 * ```typescript
 * const result = await getAllConfig();
 * console.log(result.data); // { default_provider: 'openai', ... }
 * ```
 */
export async function getAllConfig(): Promise<APIResponse<Record<string, unknown>>> {
	return apiClient.get<Record<string, unknown>>('/api/v1/config');
}

/**
 * Delete a configuration value.
 *
 * @param key - Configuration key to delete
 * @returns Promise resolving when deletion is complete
 * @throws {APIClientError} If deletion fails
 *
 * @example
 * ```typescript
 * await deleteConfig('default_provider');
 * ```
 */
export async function deleteConfig(key: string): Promise<APIResponse<void>> {
	return apiClient.delete<void>(`/api/v1/config/${key}`);
}

/**
 * Validate API configuration.
 *
 * @param request - Configuration validation request
 * @returns Promise resolving to validation result
 * @throws {APIClientError} If validation fails or request fails
 *
 * @example
 * ```typescript
 * const result = await validateConfig({
 *   provider: 'openai',
 *   model: 'gpt-4',
 *   api_key: 'sk-...'
 * });
 * console.log(result.data.valid); // true/false
 * ```
 */
export async function validateConfig(
	request: ConfigValidationRequest
): Promise<APIResponse<ConfigValidationResponse>> {
	return apiClient.post<ConfigValidationResponse>('/api/v1/config/validate', request);
}

/**
 * Update a configuration value (alias for saveConfig).
 *
 * @param key - Configuration key
 * @param value - Configuration value
 * @returns Promise resolving to the updated configuration
 *
 * @example
 * ```typescript
 * await updateConfig('default_provider', 'anthropic');
 * ```
 */
export async function updateConfig(
	key: string,
	value: string | number | boolean
): Promise<APIResponse<ConfigResponse>> {
	return saveConfig({ key, value });
}
