/**
 * TypeScript type definitions for API requests and responses.
 *
 * These types align with the backend API schema (ADR-004) for consistent
 * error handling and request tracking across the frontend and backend.
 */

/**
 * Standard error response format from the backend API.
 * Follows ADR-004: Error Handling Patterns.
 */
export interface APIError {
	/** Human-readable error message */
	error: string;
	/** Machine-readable error code (e.g., VALIDATION_ERROR, INTERNAL_ERROR) */
	code: string;
	/** Additional error context and details */
	details: Record<string, unknown>;
	/** Unique request identifier for tracing */
	request_id: string;
}

/**
 * Standard success response format with generic data type.
 * All API responses include a request_id for tracing.
 */
export interface APIResponse<T> {
	/** Response data with generic type */
	data: T;
	/** Unique request identifier for tracing */
	request_id: string;
}

/**
 * Health check response from /health endpoint.
 */
export interface HealthCheckResponse {
	/** Service status (e.g., 'ok') */
	status: string;
	/** API version (e.g., '0.1.0') */
	version: string;
}

/**
 * Translation request parameters.
 */
export interface TranslationRequest {
	/** Source text to translate */
	text: string;
	/** Source language code (e.g., 'en', 'es', 'fr') */
	source_language: string;
	/** Target language code (e.g., 'en', 'es', 'fr') */
	target_language: string;
	/** AI provider to use (e.g., 'openai', 'anthropic') */
	provider: string;
	/** API key for the AI provider (BYOK) */
	api_key: string;
}

/**
 * Translation response data.
 */
export interface TranslationResponse {
	/** Translated text */
	translated_text: string;
	/** Source language detected/used */
	source_language: string;
	/** Target language used */
	target_language: string;
	/** AI provider used */
	provider: string;
	/** Timestamp of translation */
	timestamp: string;
}

/**
 * Content extraction request parameters.
 */
export interface ExtractionRequest {
	/** URL to extract content from */
	url: string;
	/** Optional: Content type (e.g., 'article', 'webpage') */
	content_type?: string;
}

/**
 * A single content block extracted from a document.
 * Aligns with backend ContentBlock schema in backend/app/schemas/extraction.py
 */
export interface ContentBlock {
	/** Unique identifier for the content block */
	id: string;
	/** Type of content block */
	type: 'paragraph' | 'heading' | 'list' | 'quote' | 'code' | 'image';
	/** Text content of the block */
	text: string;
	/** Additional block metadata (e.g., level for headings, language for code) */
	metadata: Record<string, unknown>;
}

/**
 * Content extraction response data.
 */
export interface ExtractionResponse {
	/** Extracted text content */
	content: string;
	/** Original URL */
	url: string;
	/** Page title (if available) */
	title?: string;
	/** Extracted metadata */
	metadata?: Record<string, unknown>;
}

/**
 * Configuration save request parameters.
 */
export interface ConfigSaveRequest {
	/** Configuration key (e.g., 'default_provider', 'default_source_language') */
	key: string;
	/** Configuration value */
	value: string | number | boolean;
}

/**
 * Configuration get response data.
 */
export interface ConfigResponse {
	/** Configuration key */
	key: string;
	/** Configuration value */
	value: string | number | boolean;
}

/**
 * Configuration validation request parameters.
 */
export interface ConfigValidationRequest {
	/** AI provider (e.g., 'openai', 'anthropic') */
	provider: string;
	/** Model identifier (e.g., 'gpt-4', 'claude-3-opus-20240229') */
	model: string;
	/** User's API key for the provider */
	api_key: string;
}

/**
 * Model capabilities information.
 */
export interface ModelCapabilities {
	/** Whether model supports streaming */
	streaming: boolean;
	/** Maximum tokens supported by model */
	max_tokens: number;
}

/**
 * Configuration validation response data.
 */
export interface ConfigValidationResponse {
	/** Whether the configuration is valid */
	valid: boolean;
	/** Provider name */
	provider: string;
	/** Model identifier */
	model: string;
	/** Model capabilities */
	capabilities: ModelCapabilities;
	/** Additional validation details */
	details: Record<string, unknown>;
}

/**
 * Generic API request options.
 */
export interface APIRequestOptions {
	/** HTTP method (GET, POST, PUT, DELETE, etc.) */
	method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
	/** Request headers */
	headers?: Record<string, string>;
	/** Request body (will be JSON stringified) */
	body?: unknown;
	/** Query parameters */
	params?: Record<string, string | number | boolean>;
	/** Request timeout in milliseconds */
	timeout?: number;
}
