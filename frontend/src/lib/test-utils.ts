/**
 * Test utilities for Luminote frontend tests.
 * Provides custom render functions, mock helpers, and test data generators.
 */

import { render as testingLibraryRender, type RenderResult } from '@testing-library/svelte';
import type { ComponentType, SvelteComponent } from 'svelte';
import { writable, type Writable } from 'svelte/store';
import { vi } from 'vitest';

/**
 * Custom render function that wraps Testing Library's render
 * with common test providers and context.
 */
export function render<T extends SvelteComponent>(
	component: ComponentType<T>,
	options?: Record<string, unknown>
): RenderResult<T> {
	// Add any global providers or context here as needed
	return testingLibraryRender(component, options);
}

/**
 * Creates a mock Svelte writable store with initial value.
 */
export function createMockStore<T>(initialValue: T): Writable<T> {
	return writable(initialValue);
}

/**
 * Test data generators for common data structures.
 */
export const testData = {
	/**
	 * Generates a sample translation request.
	 */
	translationRequest: () => ({
		text: 'Hello, world!',
		source_language: 'en',
		target_language: 'es',
		provider: 'openai',
		api_key: 'test-api-key'
	}),

	/**
	 * Generates a sample translation response.
	 */
	translationResponse: () => ({
		translated_text: '¡Hola, mundo!',
		source_language: 'en',
		target_language: 'es',
		provider: 'openai',
		model: 'gpt-4',
		request_id: 'test-request-id'
	}),

	/**
	 * Generates a sample extraction response.
	 */
	extractionResponse: () => ({
		title: 'Test Article',
		content: 'This is test content.',
		author: 'Test Author',
		url: 'https://example.com/article',
		request_id: 'test-request-id'
	}),

	/**
	 * Generates a sample API error response.
	 */
	apiError: () => ({
		error: 'Test error message',
		code: 'TEST_ERROR',
		details: { field: 'test' },
		request_id: 'error-request-id'
	})
};

/**
 * Waits for a condition to be true, with timeout.
 * Useful for waiting for async operations in tests.
 */
export async function waitFor(
	condition: () => boolean,
	timeout = 1000,
	interval = 50
): Promise<void> {
	const startTime = Date.now();
	while (!condition()) {
		if (Date.now() - startTime > timeout) {
			throw new Error('Timeout waiting for condition');
		}
		await new Promise((resolve) => setTimeout(resolve, interval));
	}
}

/**
 * Creates a mock fetch function for testing API calls.
 */
export function createMockFetch(responses: Record<string, unknown> = {}) {
	return vi.fn((url: RequestInfo | URL) => {
		const urlString = url.toString();
		const response = responses[urlString] || { data: {}, request_id: 'test-id' };

		return Promise.resolve({
			ok: true,
			status: 200,
			headers: new Headers({
				'X-Request-ID': (response as { request_id?: string }).request_id || 'test-id'
			}),
			json: () => Promise.resolve(response)
		} as Response);
	});
}
