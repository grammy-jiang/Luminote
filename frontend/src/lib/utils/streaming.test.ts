/**
 * Unit tests for SSE streaming utility.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	streamTranslation,
	StreamConnectionError,
	type StreamTranslationRequest,
	type StreamEventHandlers
} from './streaming';

/**
 * Mock ReadableStream for testing SSE responses.
 */
function createMockReadableStream(events: string[]): ReadableStream<Uint8Array> {
	const encoder = new TextEncoder();
	let index = 0;

	return new ReadableStream({
		pull(controller) {
			if (index < events.length) {
				const chunk = encoder.encode(events[index]);
				controller.enqueue(chunk);
				index++;
			} else {
				controller.close();
			}
		}
	});
}

/**
 * Create mock fetch response for SSE.
 */
function createSSEResponse(events: string[], status = 200): Response {
	const body = createMockReadableStream(events);

	return new Response(body, {
		status,
		headers: {
			'Content-Type': 'text/event-stream; charset=utf-8',
			'Cache-Control': 'no-cache',
			'X-Request-ID': 'test-request-id'
		}
	});
}

describe('streamTranslation', () => {
	let mockFetch: ReturnType<typeof vi.fn>;
	let mockHandlers: StreamEventHandlers;

	beforeEach(() => {
		// Mock global fetch
		mockFetch = vi.fn();
		global.fetch = mockFetch as unknown as typeof fetch;

		// Create spy handlers
		mockHandlers = {
			onBlock: vi.fn(),
			onError: vi.fn(),
			onComplete: vi.fn()
		};
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Successful Streaming', () => {
		it('should parse single block translation event', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Hola mundo", "tokens_used": 5}\n\n',
				'event: done\ndata: {"total_tokens": 5, "processing_time": 1.2, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Hello world', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onBlock).toHaveBeenCalledWith({
				block_id: '1',
				translation: 'Hola mundo',
				tokens_used: 5
			});

			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).toHaveBeenCalledWith({
				total_tokens: 5,
				processing_time: 1.2,
				blocks_translated: 1,
				blocks_failed: 0
			});

			expect(mockHandlers.onError).not.toHaveBeenCalled();
		});

		it('should parse multiple block translation events', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "First block", "tokens_used": 10}\n\n',
				'data: {"block_id": "2", "translation": "Second block", "tokens_used": 15}\n\n',
				'data: {"block_id": "3", "translation": "Third block", "tokens_used": 20}\n\n',
				'event: done\ndata: {"total_tokens": 45, "processing_time": 3.5, "blocks_translated": 3, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [
					{ id: '1', type: 'paragraph', text: 'Block 1', metadata: {} },
					{ id: '2', type: 'paragraph', text: 'Block 2', metadata: {} },
					{ id: '3', type: 'paragraph', text: 'Block 3', metadata: {} }
				],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(3);
			expect(mockHandlers.onBlock).toHaveBeenNthCalledWith(1, {
				block_id: '1',
				translation: 'First block',
				tokens_used: 10
			});
			expect(mockHandlers.onBlock).toHaveBeenNthCalledWith(2, {
				block_id: '2',
				translation: 'Second block',
				tokens_used: 15
			});
			expect(mockHandlers.onBlock).toHaveBeenNthCalledWith(3, {
				block_id: '3',
				translation: 'Third block',
				tokens_used: 20
			});

			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).toHaveBeenCalledWith({
				total_tokens: 45,
				processing_time: 3.5,
				blocks_translated: 3,
				blocks_failed: 0
			});
		});

		it('should handle events split across multiple chunks', async () => {
			// Arrange - Simulate SSE events split across chunks
			const events = [
				'data: {"block_id": "1", "translat',
				'ion": "Split event", "tokens_used": 8}\n\n',
				'event: done\ndata: {"total_tokens": 8, "processing_time": 1.0, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onBlock).toHaveBeenCalledWith({
				block_id: '1',
				translation: 'Split event',
				tokens_used: 8
			});
		});
	});

	describe('Error Event Handling', () => {
		it('should handle per-block error events', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Success", "tokens_used": 10}\n\n',
				'event: error\ndata: {"code": "TRANSLATION_ERROR", "message": "Failed to translate", "block_id": "2"}\n\n',
				'data: {"block_id": "3", "translation": "Another success", "tokens_used": 12}\n\n',
				'event: done\ndata: {"total_tokens": 22, "processing_time": 2.5, "blocks_translated": 2, "blocks_failed": 1}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [
					{ id: '1', type: 'paragraph', text: 'Block 1', metadata: {} },
					{ id: '2', type: 'paragraph', text: 'Block 2', metadata: {} },
					{ id: '3', type: 'paragraph', text: 'Block 3', metadata: {} }
				],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(2);
			expect(mockHandlers.onError).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onError).toHaveBeenCalledWith({
				code: 'TRANSLATION_ERROR',
				message: 'Failed to translate',
				block_id: '2'
			});

			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).toHaveBeenCalledWith({
				total_tokens: 22,
				processing_time: 2.5,
				blocks_translated: 2,
				blocks_failed: 1
			});
		});

		it('should handle timeout error events', async () => {
			// Arrange
			const events = [
				'event: error\ndata: {"code": "TIMEOUT", "message": "Translation timed out after 120s", "block_id": "1"}\n\n',
				'event: done\ndata: {"total_tokens": 0, "processing_time": 120.5, "blocks_translated": 0, "blocks_failed": 1}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Very long text...', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onError).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onError).toHaveBeenCalledWith({
				code: 'TIMEOUT',
				message: 'Translation timed out after 120s',
				block_id: '1'
			});

			expect(mockHandlers.onBlock).not.toHaveBeenCalled();
			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
		});

		it('should handle stream-level error events', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Success", "tokens_used": 10}\n\n',
				'event: error\ndata: {"code": "INTERNAL_ERROR", "message": "Unexpected error occurred"}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onError).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onError).toHaveBeenCalledWith({
				code: 'INTERNAL_ERROR',
				message: 'Unexpected error occurred'
			});
		});
	});

	describe('Connection Error Handling', () => {
		it('should throw StreamConnectionError on HTTP error', async () => {
			// Arrange
			mockFetch.mockResolvedValue(
				new Response(JSON.stringify({ code: 'VALIDATION_ERROR', message: 'Invalid request' }), {
					status: 422,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'invalid',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(streamTranslation(request, mockHandlers)).rejects.toThrow(StreamConnectionError);
			await expect(streamTranslation(request, mockHandlers)).rejects.toThrow('Invalid request');
		});

		it('should throw StreamConnectionError on wrong content type', async () => {
			// Arrange
			mockFetch.mockResolvedValue(
				new Response('Not SSE', {
					status: 200,
					headers: { 'Content-Type': 'text/plain' }
				})
			);

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(streamTranslation(request, mockHandlers)).rejects.toThrow(StreamConnectionError);
			await expect(streamTranslation(request, mockHandlers)).rejects.toThrow(
				'Expected text/event-stream'
			);
		});

		it('should throw StreamConnectionError on null response body', async () => {
			// Arrange
			mockFetch.mockResolvedValue(
				new Response(null, {
					status: 200,
					headers: { 'Content-Type': 'text/event-stream' }
				})
			);

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(
				streamTranslation(request, mockHandlers, { maxRetries: 0, retryDelay: 1 })
			).rejects.toThrow(StreamConnectionError);
			await expect(
				streamTranslation(request, mockHandlers, { maxRetries: 0, retryDelay: 1 })
			).rejects.toThrow('Response body is null');
		});

		it('should throw StreamConnectionError on network error', async () => {
			// Arrange
			mockFetch.mockRejectedValue(new Error('Network error'));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert - Use short retry settings to avoid timeout
			await expect(
				streamTranslation(request, mockHandlers, { maxRetries: 1, retryDelay: 10 })
			).rejects.toThrow(StreamConnectionError);
			await expect(
				streamTranslation(request, mockHandlers, { maxRetries: 1, retryDelay: 10 })
			).rejects.toThrow('Failed to connect to streaming endpoint');
		});
	});

	describe('Stream Cancellation', () => {
		it('should handle stream cancellation via AbortController', async () => {
			// Arrange
			const abortController = new AbortController();

			mockFetch.mockImplementation(() => {
				// Abort immediately when fetch is called
				abortController.abort();
				return Promise.reject(new DOMException('The user aborted a request.', 'AbortError'));
			});

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(
				streamTranslation(request, mockHandlers, { signal: abortController.signal })
			).rejects.toThrow(StreamConnectionError);
			await expect(
				streamTranslation(request, mockHandlers, { signal: abortController.signal })
			).rejects.toThrow('Stream cancelled by user');
		});
	});

	describe('Retry Logic', () => {
		it('should retry on 500 server error', async () => {
			// Arrange
			let attemptCount = 0;
			mockFetch.mockImplementation(() => {
				attemptCount++;
				if (attemptCount < 2) {
					// Fail first attempt with 500 error
					return Promise.resolve(
						new Response('Internal Server Error', {
							status: 500,
							headers: { 'Content-Type': 'text/plain' }
						})
					);
				}
				// Succeed on second attempt
				const events = [
					'data: {"block_id": "1", "translation": "Success after retry", "tokens_used": 10}\n\n',
					'event: done\ndata: {"total_tokens": 10, "processing_time": 1.5, "blocks_translated": 1, "blocks_failed": 0}\n\n'
				];
				return Promise.resolve(createSSEResponse(events));
			});

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers, {
				maxRetries: 3,
				retryDelay: 10 // Short delay for testing
			});

			// Assert
			expect(attemptCount).toBe(2);
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
		});

		it('should not retry on 4xx client error', async () => {
			// Arrange
			mockFetch.mockResolvedValue(
				new Response(JSON.stringify({ code: 'VALIDATION_ERROR', message: 'Bad request' }), {
					status: 400,
					headers: { 'Content-Type': 'application/json' }
				})
			);

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(streamTranslation(request, mockHandlers, { maxRetries: 3 })).rejects.toThrow(
				StreamConnectionError
			);

			// Should only call fetch once (no retries for 4xx errors)
			expect(mockFetch).toHaveBeenCalledTimes(1);
		});

		it('should give up after max retries', async () => {
			// Arrange
			mockFetch.mockResolvedValue(
				new Response('Service Unavailable', {
					status: 503,
					headers: { 'Content-Type': 'text/plain' }
				})
			);

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act & Assert
			await expect(
				streamTranslation(request, mockHandlers, {
					maxRetries: 2,
					retryDelay: 10
				})
			).rejects.toThrow(StreamConnectionError);

			// Should attempt 1 initial + 2 retries = 3 total
			expect(mockFetch).toHaveBeenCalledTimes(3);
		});
	});

	describe('Edge Cases', () => {
		it('should handle empty translation text', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "", "tokens_used": 0}\n\n',
				'event: done\ndata: {"total_tokens": 0, "processing_time": 0.1, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: '', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onBlock).toHaveBeenCalledWith({
				block_id: '1',
				translation: '',
				tokens_used: 0
			});
		});

		it('should handle stream ending without done event', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Incomplete stream", "tokens_used": 5}\n\n'
				// No done event - stream just ends
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).not.toHaveBeenCalled();
		});

		it('should ignore malformed JSON in data lines', async () => {
			// Arrange
			const events = [
				'data: {invalid json}\n\n',
				'data: {"block_id": "1", "translation": "Valid", "tokens_used": 5}\n\n',
				'event: done\ndata: {"total_tokens": 5, "processing_time": 1.0, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert - Should only process valid event
			expect(mockHandlers.onBlock).toHaveBeenCalledTimes(1);
			expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
		});

		it('should handle custom base URL', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Test", "tokens_used": 5}\n\n',
				'event: done\ndata: {"total_tokens": 5, "processing_time": 1.0, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Test', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				api_key: 'test-key'
			};

			// Act
			await streamTranslation(request, mockHandlers, {
				baseUrl: 'https://custom-api.example.com/translate/stream'
			});

			// Assert
			expect(mockFetch).toHaveBeenCalledWith(
				'https://custom-api.example.com/translate/stream',
				expect.objectContaining({
					method: 'POST',
					headers: expect.objectContaining({
						'Content-Type': 'application/json',
						Accept: 'text/event-stream'
					})
				})
			);
		});
	});

	describe('Request Format', () => {
		it('should send correct request body', async () => {
			// Arrange
			const events = [
				'data: {"block_id": "1", "translation": "Test", "tokens_used": 5}\n\n',
				'event: done\ndata: {"total_tokens": 5, "processing_time": 1.0, "blocks_translated": 1, "blocks_failed": 0}\n\n'
			];

			mockFetch.mockResolvedValue(createSSEResponse(events));

			const request: StreamTranslationRequest = {
				content_blocks: [{ id: '1', type: 'paragraph', text: 'Hello world', metadata: {} }],
				target_language: 'es',
				provider: 'openai',
				model: 'gpt-4',
				api_key: 'sk-test-key-123'
			};

			// Act
			await streamTranslation(request, mockHandlers);

			// Assert
			expect(mockFetch).toHaveBeenCalledWith(
				'/api/v1/translate/stream',
				expect.objectContaining({
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						Accept: 'text/event-stream'
					},
					body: JSON.stringify(request)
				})
			);
		});
	});
});
