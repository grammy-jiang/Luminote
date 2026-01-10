/**
 * SSE (Server-Sent Events) streaming utility for progressive block translation.
 *
 * This module provides client-side support for connecting to the backend's
 * /api/v1/translate/stream endpoint and processing translation events as they arrive.
 *
 * Features:
 * - Parses SSE event format (data:, event: lines)
 * - Handles block translation events, error events, and done events
 * - Supports stream cancellation via AbortController
 * - Automatic retry logic for transient network failures
 * - Graceful fallback to non-streaming mode on connection errors
 * - Type-safe event handling
 *
 * Event Types:
 * - Block event (default message): {"block_id": "1", "translation": "...", "tokens_used": 50}
 * - Error event: {"code": "...", "message": "...", "block_id": "..."}
 * - Done event: {"total_tokens": 95, "processing_time": 12.5, "blocks_translated": 2, "blocks_failed": 0}
 *
 * @see ADR-002: Streaming Translation Architecture
 */

/**
 * A single translated block event from the SSE stream.
 */
export interface BlockTranslationEvent {
	/** Unique identifier for the block */
	block_id: string;
	/** Translated text content */
	translation: string;
	/** Number of tokens used for this block's translation */
	tokens_used: number;
}

/**
 * Error event from the SSE stream.
 */
export interface StreamErrorEvent {
	/** Error code (e.g., TIMEOUT, TRANSLATION_ERROR, RATE_LIMIT_EXCEEDED) */
	code: string;
	/** Human-readable error message */
	message: string;
	/** Optional: ID of the block that failed (for per-block errors) */
	block_id?: string;
}

/**
 * Completion event from the SSE stream.
 */
export interface StreamDoneEvent {
	/** Total tokens used across all translated blocks */
	total_tokens: number;
	/** Total processing time in seconds */
	processing_time: number;
	/** Number of blocks successfully translated */
	blocks_translated: number;
	/** Number of blocks that failed to translate */
	blocks_failed: number;
}

/**
 * Translation request parameters for streaming endpoint.
 */
export interface StreamTranslationRequest {
	/** Array of content blocks to translate */
	content_blocks: Array<{
		id: string;
		type: 'paragraph' | 'heading' | 'list' | 'quote' | 'code' | 'image';
		text: string;
		metadata: Record<string, unknown>;
	}>;
	/** Target language code (ISO 639-1, e.g., 'es', 'fr') */
	target_language: string;
	/** AI provider to use (e.g., 'openai', 'anthropic') */
	provider: string;
	/** Model name (e.g., 'gpt-4', 'claude-3-opus') */
	model?: string;
	/** API key for the provider (BYOK - Bring Your Own Key) */
	api_key: string;
}

/**
 * Callback handlers for stream events.
 */
export interface StreamEventHandlers {
	/** Called when a block translation completes */
	onBlock: (event: BlockTranslationEvent) => void;
	/** Called when an error occurs (per-block or stream-level) */
	onError: (error: StreamErrorEvent) => void;
	/** Called when all blocks are processed (success or partial success) */
	onComplete: (done: StreamDoneEvent) => void;
}

/**
 * Options for stream translation.
 */
export interface StreamTranslationOptions {
	/** Base URL for API (defaults to /api/v1/translate/stream) */
	baseUrl?: string;
	/** AbortController signal for cancellation */
	signal?: AbortSignal;
	/** Maximum retry attempts for transient failures (default: 3) */
	maxRetries?: number;
	/** Delay between retries in milliseconds (default: 1000) */
	retryDelay?: number;
}

/**
 * Error thrown when stream connection fails.
 */
export class StreamConnectionError extends Error {
	constructor(
		message: string,
		public readonly statusCode?: number,
		public readonly originalError?: unknown
	) {
		super(message);
		this.name = 'StreamConnectionError';
	}
}

/**
 * Parse an SSE event from raw text lines.
 *
 * SSE format:
 * ```
 * event: error
 * data: {"code": "...", "message": "..."}
 *
 * data: {"block_id": "1", "translation": "..."}
 *
 * ```
 *
 * @param lines - Lines from SSE stream
 * @returns Parsed event with type and data, or null if incomplete
 */
function parseSSEEvent(lines: string[]): { type: string; data: unknown } | null {
	let eventType = 'message'; // Default event type
	let dataLine: string | null = null;

	for (const line of lines) {
		if (line.startsWith('event: ')) {
			eventType = line.slice(7).trim();
		} else if (line.startsWith('data: ')) {
			dataLine = line.slice(6).trim();
		}
	}

	if (dataLine) {
		try {
			const data = JSON.parse(dataLine);
			return { type: eventType, data };
		} catch (error) {
			console.error('Failed to parse SSE data:', dataLine, error);
			return null;
		}
	}

	return null;
}

/**
 * Stream translation results from the backend using SSE.
 *
 * This function connects to the /api/v1/translate/stream endpoint and
 * progressively receives translation events as blocks are translated.
 *
 * @param request - Translation request parameters
 * @param handlers - Event handlers for block, error, and completion events
 * @param options - Optional configuration (abort signal, retry settings)
 * @throws StreamConnectionError if connection fails after retries
 *
 * @example
 * ```typescript
 * const abortController = new AbortController();
 *
 * try {
 *   await streamTranslation(
 *     {
 *       content_blocks: [...],
 *       target_language: 'es',
 *       provider: 'openai',
 *       api_key: userKey,
 *     },
 *     {
 *       onBlock: (event) => {
 *         console.log(`Block ${event.block_id} translated`);
 *         updateUI(event.block_id, event.translation);
 *       },
 *       onError: (error) => {
 *         console.error(`Error: ${error.message}`);
 *         showErrorForBlock(error.block_id);
 *       },
 *       onComplete: (done) => {
 *         console.log(`Completed: ${done.blocks_translated} blocks`);
 *         hideLoadingIndicator();
 *       },
 *     },
 *     { signal: abortController.signal }
 *   );
 * } catch (error) {
 *   if (error instanceof StreamConnectionError) {
 *     // Fallback to non-streaming API
 *     console.error('Streaming failed, using fallback');
 *   }
 * }
 *
 * // Cancel stream
 * abortController.abort();
 * ```
 */
export async function streamTranslation(
	request: StreamTranslationRequest,
	handlers: StreamEventHandlers,
	options: StreamTranslationOptions = {}
): Promise<void> {
	const {
		baseUrl = '/api/v1/translate/stream',
		signal,
		maxRetries = 3,
		retryDelay = 1000
	} = options;

	let attempt = 0;

	while (attempt <= maxRetries) {
		try {
			// Make fetch request with SSE headers
			const response = await fetch(baseUrl, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'text/event-stream'
				},
				body: JSON.stringify(request),
				signal
			});

			// Check for HTTP errors
			if (!response.ok) {
				let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
				try {
					// Clone response to read body without consuming it
					const clonedResponse = response.clone();
					const errorText = await clonedResponse.text();
					const errorData = JSON.parse(errorText);
					if (errorData.message) {
						errorMessage = errorData.message;
					}
				} catch {
					// If parsing fails, use status text
				}

				throw new StreamConnectionError(errorMessage, response.status);
			}

			// Verify content type
			const contentType = response.headers.get('Content-Type');
			if (!contentType?.includes('text/event-stream')) {
				throw new StreamConnectionError(
					`Expected text/event-stream, got ${contentType}`,
					response.status
				);
			}

			// Get reader from response body
			const reader = response.body?.getReader();
			if (!reader) {
				throw new StreamConnectionError('Response body is null');
			}

			const decoder = new TextDecoder();
			let buffer = '';

			try {
				// Read stream chunks
				// eslint-disable-next-line no-constant-condition
				while (true) {
					const { done, value } = await reader.read();

					if (done) {
						// Stream ended without done event - this is unusual but not an error
						console.warn('Stream ended without done event');
						break;
					}

					// Decode chunk and add to buffer
					buffer += decoder.decode(value, { stream: true });

					// Process complete events (separated by double newline)
					const events = buffer.split('\n\n');

					// Keep incomplete event in buffer
					buffer = events.pop() || '';

					for (const eventText of events) {
						if (!eventText.trim()) continue;

						const lines = eventText.split('\n').filter((line) => line.trim());
						const event = parseSSEEvent(lines);

						if (!event) continue;

						// Handle different event types
						if (event.type === 'message' || event.type === 'block') {
							// Block translation event
							const blockEvent = event.data as BlockTranslationEvent;
							if (blockEvent.block_id && blockEvent.translation !== undefined) {
								handlers.onBlock(blockEvent);
							}
						} else if (event.type === 'error') {
							// Error event
							const errorEvent = event.data as StreamErrorEvent;
							if (errorEvent.code && errorEvent.message) {
								handlers.onError(errorEvent);
							}
						} else if (event.type === 'done') {
							// Completion event
							const doneEvent = event.data as StreamDoneEvent;
							handlers.onComplete(doneEvent);
							return; // Successfully completed
						}
					}
				}

				// Stream ended - return successfully (even without done event)
				return;
			} finally {
				reader.releaseLock();
			}
		} catch (error) {
			// Handle cancellation
			if (signal?.aborted) {
				throw new StreamConnectionError('Stream cancelled by user');
			}

			// Wrap non-StreamConnectionError errors
			const connectionError =
				error instanceof StreamConnectionError
					? error
					: new StreamConnectionError('Failed to connect to streaming endpoint', undefined, error);

			// If this is the last attempt, throw the error
			if (attempt >= maxRetries) {
				throw connectionError;
			}

			// Retry for transient errors (network issues, 5xx errors)
			const shouldRetry = !connectionError.statusCode || connectionError.statusCode >= 500;

			if (!shouldRetry) {
				throw connectionError;
			}

			console.warn(`Stream connection failed, retrying (attempt ${attempt + 1}/${maxRetries})...`);
			attempt++;

			// Wait before retrying
			await new Promise((resolve) => setTimeout(resolve, retryDelay * attempt));
		}
	}
}
