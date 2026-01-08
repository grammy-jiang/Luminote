/**
 * Unit tests for API client utility.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { APIClient, APIClientError, apiClient } from './api';
import type { APIError } from '$lib/types/api';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('APIClient', () => {
	let client: APIClient;

	beforeEach(() => {
		client = new APIClient('http://localhost:8000');
		mockFetch.mockClear();
	});

	afterEach(() => {
		vi.clearAllTimers();
	});

	describe('constructor', () => {
		it('should use provided base URL', () => {
			const customClient = new APIClient('https://api.example.com');
			expect(customClient).toBeInstanceOf(APIClient);
		});

		it('should use default base URL when not provided', () => {
			const defaultClient = new APIClient();
			expect(defaultClient).toBeInstanceOf(APIClient);
		});
	});

	describe('request method', () => {
		it('should make successful GET request', async () => {
			const mockData = { status: 'ok', version: '0.1.0' };
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue(mockData)
			};
			mockFetch.mockResolvedValue(mockResponse);

			const response = await client.get('/health');

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/health',
				expect.objectContaining({
					method: 'GET',
					headers: { 'Content-Type': 'application/json' }
				})
			);
			expect(response.data).toEqual(mockData);
			expect(response.request_id).toBe('test-request-id');
		});

		it('should make successful POST request with body', async () => {
			const mockRequestBody = { text: 'Hello', source_language: 'en', target_language: 'es' };
			const mockResponseData = { translated_text: 'Hola' };
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue({ data: mockResponseData, request_id: 'test-request-id' })
			};
			mockFetch.mockResolvedValue(mockResponse);

			const response = await client.post('/api/v1/translate', mockRequestBody);

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/translate',
				expect.objectContaining({
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(mockRequestBody)
				})
			);
			expect(response.data).toEqual(mockResponseData);
		});

		it('should include query parameters in GET request', async () => {
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue({ data: [], request_id: 'test-request-id' })
			};
			mockFetch.mockResolvedValue(mockResponse);

			await client.get('/api/v1/search', { query: 'test', limit: 10 });

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/search?query=test&limit=10',
				expect.any(Object)
			);
		});

		it('should handle API error responses', async () => {
			const mockErrorData: APIError = {
				error: 'Validation failed',
				code: 'VALIDATION_ERROR',
				details: { field: 'text', message: 'Text is required' },
				request_id: 'error-request-id'
			};
			const mockResponse = {
				ok: false,
				status: 422,
				headers: new Headers({ 'X-Request-ID': 'error-request-id' }),
				json: vi.fn().mockResolvedValue(mockErrorData)
			};
			mockFetch.mockResolvedValue(mockResponse);

			await expect(client.post('/api/v1/translate', {})).rejects.toThrow(APIClientError);

			try {
				await client.post('/api/v1/translate', {});
			} catch (error) {
				expect(error).toBeInstanceOf(APIClientError);
				if (error instanceof APIClientError) {
					expect(error.statusCode).toBe(422);
					expect(error.code).toBe('VALIDATION_ERROR');
					expect(error.message).toBe('Validation failed');
					expect(error.requestId).toBe('error-request-id');
					expect(error.details).toEqual({ field: 'text', message: 'Text is required' });
				}
			}
		});

		it('should handle network errors', async () => {
			mockFetch.mockRejectedValue(new TypeError('Failed to fetch'));

			await expect(client.get('/health')).rejects.toThrow(APIClientError);

			try {
				await client.get('/health');
			} catch (error) {
				expect(error).toBeInstanceOf(APIClientError);
				if (error instanceof APIClientError) {
					expect(error.code).toBe('NETWORK_ERROR');
					expect(error.statusCode).toBe(0);
				}
			}
		});

		it('should handle timeout errors', async () => {
			// Mock AbortError to simulate timeout
			const abortError = new Error('The operation was aborted');
			abortError.name = 'AbortError';
			mockFetch.mockRejectedValue(abortError);

			try {
				await client.request('/slow-endpoint', { timeout: 1000 });
				// Should not reach here
				expect(true).toBe(false);
			} catch (error) {
				expect(error).toBeInstanceOf(APIClientError);
				if (error instanceof APIClientError) {
					expect(error.code).toBe('REQUEST_TIMEOUT');
					expect(error.statusCode).toBe(408);
				}
			}
		});

		it('should handle custom headers', async () => {
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue({ data: {}, request_id: 'test-request-id' })
			};
			mockFetch.mockResolvedValue(mockResponse);

			await client.request('/api/v1/custom', {
				headers: { 'X-Custom-Header': 'custom-value' }
			});

			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/api/v1/custom',
				expect.objectContaining({
					headers: {
						'Content-Type': 'application/json',
						'X-Custom-Header': 'custom-value'
					}
				})
			);
		});
	});

	describe('convenience methods', () => {
		beforeEach(() => {
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue({ data: {}, request_id: 'test-request-id' })
			};
			mockFetch.mockResolvedValue(mockResponse);
		});

		it('should make GET request using get method', async () => {
			await client.get('/endpoint');
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/endpoint',
				expect.objectContaining({ method: 'GET' })
			);
		});

		it('should make POST request using post method', async () => {
			await client.post('/endpoint', { data: 'test' });
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/endpoint',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify({ data: 'test' })
				})
			);
		});

		it('should make PUT request using put method', async () => {
			await client.put('/endpoint', { data: 'test' });
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/endpoint',
				expect.objectContaining({
					method: 'PUT',
					body: JSON.stringify({ data: 'test' })
				})
			);
		});

		it('should make DELETE request using delete method', async () => {
			await client.delete('/endpoint');
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/endpoint',
				expect.objectContaining({ method: 'DELETE' })
			);
		});

		it('should make PATCH request using patch method', async () => {
			await client.patch('/endpoint', { data: 'test' });
			expect(mockFetch).toHaveBeenCalledWith(
				'http://localhost:8000/endpoint',
				expect.objectContaining({
					method: 'PATCH',
					body: JSON.stringify({ data: 'test' })
				})
			);
		});
	});

	describe('response format handling', () => {
		it('should handle response with request_id field', async () => {
			const mockResponseData = {
				data: { value: 'test' },
				request_id: 'test-request-id'
			};
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue(mockResponseData)
			};
			mockFetch.mockResolvedValue(mockResponse);

			const response = await client.get('/endpoint');

			expect(response).toEqual(mockResponseData);
		});

		it('should wrap response without request_id field', async () => {
			const mockResponseData = { value: 'test' };
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
				json: vi.fn().mockResolvedValue(mockResponseData)
			};
			mockFetch.mockResolvedValue(mockResponse);

			const response = await client.get('/endpoint');

			expect(response).toEqual({
				data: mockResponseData,
				request_id: 'test-request-id'
			});
		});

		it('should use "unknown" request_id when header is missing', async () => {
			const mockResponseData = { value: 'test' };
			const mockResponse = {
				ok: true,
				status: 200,
				headers: new Headers(),
				json: vi.fn().mockResolvedValue(mockResponseData)
			};
			mockFetch.mockResolvedValue(mockResponse);

			const response = await client.get('/endpoint');

			expect(response.request_id).toBe('unknown');
		});
	});
});

describe('apiClient singleton', () => {
	it('should export a default instance', () => {
		expect(apiClient).toBeInstanceOf(APIClient);
	});

	it('should be usable for making requests', async () => {
		const mockResponse = {
			ok: true,
			status: 200,
			headers: new Headers({ 'X-Request-ID': 'test-request-id' }),
			json: vi.fn().mockResolvedValue({ status: 'ok', version: '0.1.0' })
		};
		mockFetch.mockResolvedValue(mockResponse);

		const response = await apiClient.get('/health');

		expect(response.data).toEqual({ status: 'ok', version: '0.1.0' });
	});
});

describe('APIClientError', () => {
	it('should create error with correct properties', () => {
		const apiError: APIError = {
			error: 'Test error',
			code: 'TEST_ERROR',
			details: { info: 'test' },
			request_id: 'test-id'
		};

		const error = new APIClientError(apiError, 400);

		expect(error.name).toBe('APIClientError');
		expect(error.message).toBe('Test error');
		expect(error.statusCode).toBe(400);
		expect(error.code).toBe('TEST_ERROR');
		expect(error.details).toEqual({ info: 'test' });
		expect(error.requestId).toBe('test-id');
	});

	it('should be an instance of Error', () => {
		const apiError: APIError = {
			error: 'Test error',
			code: 'TEST_ERROR',
			details: {},
			request_id: 'test-id'
		};

		const error = new APIClientError(apiError, 400);

		expect(error).toBeInstanceOf(Error);
		expect(error).toBeInstanceOf(APIClientError);
	});
});
