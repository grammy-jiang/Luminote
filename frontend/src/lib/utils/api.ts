/**
 * API client utility for communicating with the Luminote backend.
 *
 * Provides a centralized client with:
 * - Type-safe requests and responses
 * - Consistent error handling
 * - Request ID tracking
 * - Configurable base URL
 */

import type { APIError, APIResponse, APIRequestOptions } from '$lib/types/api';

/**
 * Custom error class for API-related errors.
 * Wraps the backend APIError response for easy error handling.
 */
export class APIClientError extends Error {
	/** HTTP status code */
	public readonly statusCode: number;
	/** Machine-readable error code */
	public readonly code: string;
	/** Additional error context */
	public readonly details: Record<string, unknown>;
	/** Request ID for tracing */
	public readonly requestId: string;

	constructor(apiError: APIError, statusCode: number) {
		super(apiError.error);
		this.name = 'APIClientError';
		this.statusCode = statusCode;
		this.code = apiError.code;
		this.details = apiError.details;
		this.requestId = apiError.request_id;
	}
}

/**
 * Get the API base URL from environment variables.
 * Falls back to http://localhost:8000 for development.
 */
function getBaseURL(): string {
	// Check for Vite environment variable
	if (typeof import.meta !== 'undefined' && import.meta.env) {
		const envUrl = import.meta.env.VITE_API_BASE_URL;
		if (envUrl) {
			return envUrl;
		}
	}

	// Fallback to default
	return 'http://localhost:8000';
}

/**
 * API client class for making HTTP requests to the backend.
 */
export class APIClient {
	private baseURL: string;
	private defaultHeaders: Record<string, string>;

	constructor(baseURL?: string) {
		this.baseURL = baseURL || getBaseURL();
		this.defaultHeaders = {
			'Content-Type': 'application/json'
		};
	}

	/**
	 * Make an HTTP request to the API.
	 *
	 * @param endpoint - API endpoint (e.g., '/health', '/api/v1/translate')
	 * @param options - Request options (method, headers, body, params, timeout)
	 * @returns Promise resolving to the response data
	 * @throws {APIClientError} If the request fails
	 */
	async request<T>(endpoint: string, options: APIRequestOptions = {}): Promise<APIResponse<T>> {
		const { method = 'GET', headers = {}, body, params, timeout = 30000 } = options;

		// Build URL with query parameters
		const url = new URL(endpoint, this.baseURL);
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				url.searchParams.append(key, String(value));
			});
		}

		// Merge headers
		const requestHeaders = {
			...this.defaultHeaders,
			...headers
		};

		// Build request config
		const requestConfig: RequestInit = {
			method,
			headers: requestHeaders
		};

		// Add body for non-GET requests
		if (body && method !== 'GET') {
			requestConfig.body = JSON.stringify(body);
		}

		// Create abort controller for timeout
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);
		requestConfig.signal = controller.signal;

		try {
			const response = await fetch(url.toString(), requestConfig);
			clearTimeout(timeoutId);

			// Extract request ID from response headers
			const requestId = response.headers.get('X-Request-ID') || 'unknown';

			// Handle error responses
			if (!response.ok) {
				const errorData: APIError = await response.json();
				throw new APIClientError(errorData, response.status);
			}

			// Parse successful response
			const data = await response.json();

			// Handle different response formats
			// If the response already has request_id, it's a success response
			if ('request_id' in data) {
				return data as APIResponse<T>;
			}

			// Otherwise, wrap the data in our standard format
			return {
				data: data as T,
				request_id: requestId
			};
		} catch (error) {
			clearTimeout(timeoutId);

			// Handle timeout errors
			if (error instanceof Error && error.name === 'AbortError') {
				throw new APIClientError(
					{
						error: 'Request timeout',
						code: 'REQUEST_TIMEOUT',
						details: { timeout },
						request_id: 'unknown'
					},
					408
				);
			}

			// Handle network errors
			if (error instanceof TypeError) {
				throw new APIClientError(
					{
						error: 'Network error',
						code: 'NETWORK_ERROR',
						details: { message: error.message },
						request_id: 'unknown'
					},
					0
				);
			}

			// Re-throw APIClientError
			if (error instanceof APIClientError) {
				throw error;
			}

			// Handle unexpected errors
			throw new APIClientError(
				{
					error: 'Unexpected error',
					code: 'UNEXPECTED_ERROR',
					details: { message: error instanceof Error ? error.message : 'Unknown error' },
					request_id: 'unknown'
				},
				500
			);
		}
	}

	/**
	 * Make a GET request.
	 *
	 * @param endpoint - API endpoint
	 * @param params - Optional query parameters
	 * @returns Promise resolving to the response data
	 */
	async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<APIResponse<T>> {
		return this.request<T>(endpoint, { method: 'GET', params });
	}

	/**
	 * Make a POST request.
	 *
	 * @param endpoint - API endpoint
	 * @param body - Request body
	 * @returns Promise resolving to the response data
	 */
	async post<T>(endpoint: string, body: unknown): Promise<APIResponse<T>> {
		return this.request<T>(endpoint, { method: 'POST', body });
	}

	/**
	 * Make a PUT request.
	 *
	 * @param endpoint - API endpoint
	 * @param body - Request body
	 * @returns Promise resolving to the response data
	 */
	async put<T>(endpoint: string, body: unknown): Promise<APIResponse<T>> {
		return this.request<T>(endpoint, { method: 'PUT', body });
	}

	/**
	 * Make a DELETE request.
	 *
	 * @param endpoint - API endpoint
	 * @returns Promise resolving to the response data
	 */
	async delete<T>(endpoint: string): Promise<APIResponse<T>> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}

	/**
	 * Make a PATCH request.
	 *
	 * @param endpoint - API endpoint
	 * @param body - Request body
	 * @returns Promise resolving to the response data
	 */
	async patch<T>(endpoint: string, body: unknown): Promise<APIResponse<T>> {
		return this.request<T>(endpoint, { method: 'PATCH', body });
	}
}

/**
 * Default API client instance.
 * Use this singleton instance for all API calls.
 */
export const apiClient = new APIClient();
