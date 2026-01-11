/**
 * Unit tests for configuration store.
 *
 * Tests cover:
 * - Default state initialization
 * - localStorage persistence (excluding API key)
 * - API key memory-only behavior
 * - Reset to defaults functionality
 * - Validation on set operations
 * - Change notifications
 * - SSR compatibility
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { configStore, DEFAULT_CONFIG_EXPORT, type ConfigState } from './config';

describe('Configuration Store', () => {
	// Mock localStorage
	let localStorageMock: { [key: string]: string } = {};

	beforeEach(() => {
		// Clear localStorage mock
		localStorageMock = {};

		// Mock localStorage methods
		vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key: string) => {
			return localStorageMock[key] || null;
		});

		vi.spyOn(Storage.prototype, 'setItem').mockImplementation((key: string, value: string) => {
			localStorageMock[key] = value;
		});

		vi.spyOn(Storage.prototype, 'removeItem').mockImplementation((key: string) => {
			delete localStorageMock[key];
		});

		// Reset store to defaults
		configStore.reset();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Initialization', () => {
		it('initializes with default values', () => {
			const state = get(configStore);

			expect(state.provider).toBe('openai');
			expect(state.model).toBe('gpt-4');
			expect(state.target_language).toBe('en');
			expect(state.api_key).toBe('');
		});

		it('uses defaults if stored provider is invalid', () => {
			localStorageMock['luminote_config'] = JSON.stringify({
				provider: 'invalid_provider',
				model: 'gpt-4',
				target_language: 'en'
			});

			configStore.reset();
			const state = get(configStore);

			expect(state.provider).toBe('openai');
		});

		it('uses defaults if stored model is invalid', () => {
			localStorageMock['luminote_config'] = JSON.stringify({
				provider: 'openai',
				model: '',
				target_language: 'en'
			});

			configStore.reset();
			const state = get(configStore);

			expect(state.model).toBe('gpt-4');
		});

		it('uses defaults if stored target_language is invalid', () => {
			localStorageMock['luminote_config'] = JSON.stringify({
				provider: 'openai',
				model: 'gpt-4',
				target_language: 'english' // Invalid: should be 2-letter code
			});

			configStore.reset();
			const state = get(configStore);

			expect(state.target_language).toBe('en');
		});
	});

	describe('Provider Management', () => {
		it('sets provider to openai', () => {
			configStore.setProvider('openai');
			const state = get(configStore);

			expect(state.provider).toBe('openai');
		});

		it('sets provider to anthropic', () => {
			configStore.setProvider('anthropic');
			const state = get(configStore);

			expect(state.provider).toBe('anthropic');
		});

		it('persists provider to localStorage', () => {
			configStore.setProvider('anthropic');

			const stored = localStorageMock['luminote_config'];
			expect(stored).toBeDefined();
			const parsed = JSON.parse(stored);
			expect(parsed.provider).toBe('anthropic');
		});

		it('throws error for invalid provider', () => {
			expect(() => {
				// @ts-expect-error - Testing invalid input
				configStore.setProvider('invalid_provider');
			}).toThrow('Invalid provider');
		});
	});

	describe('Model Management', () => {
		it('sets model', () => {
			configStore.setModel('gpt-4-turbo');
			const state = get(configStore);

			expect(state.model).toBe('gpt-4-turbo');
		});

		it('persists model to localStorage', () => {
			configStore.setModel('claude-3-opus');

			const stored = localStorageMock['luminote_config'];
			expect(stored).toBeDefined();
			const parsed = JSON.parse(stored);
			expect(parsed.model).toBe('claude-3-opus');
		});

		it('throws error for empty model', () => {
			expect(() => {
				configStore.setModel('');
			}).toThrow('Invalid model');
		});

		it('throws error for whitespace-only model', () => {
			expect(() => {
				configStore.setModel('   ');
			}).toThrow('Invalid model');
		});
	});

	describe('Target Language Management', () => {
		it('sets target language', () => {
			configStore.setTargetLanguage('es');
			const state = get(configStore);

			expect(state.target_language).toBe('es');
		});

		it('persists target language to localStorage', () => {
			configStore.setTargetLanguage('fr');

			const stored = localStorageMock['luminote_config'];
			expect(stored).toBeDefined();
			const parsed = JSON.parse(stored);
			expect(parsed.target_language).toBe('fr');
		});

		it('accepts various ISO 639-1 language codes', () => {
			const validCodes = ['en', 'es', 'fr', 'de', 'ja', 'zh', 'ko', 'ar'];

			validCodes.forEach((code) => {
				configStore.setTargetLanguage(code);
				const state = get(configStore);
				expect(state.target_language).toBe(code);
			});
		});

		it('throws error for invalid language code format', () => {
			expect(() => {
				configStore.setTargetLanguage('eng'); // 3 letters
			}).toThrow('Invalid target_language');

			expect(() => {
				configStore.setTargetLanguage('e'); // 1 letter
			}).toThrow('Invalid target_language');

			expect(() => {
				configStore.setTargetLanguage('EN'); // Uppercase
			}).toThrow('Invalid target_language');

			expect(() => {
				configStore.setTargetLanguage('e1'); // Contains digit
			}).toThrow('Invalid target_language');

			expect(() => {
				configStore.setTargetLanguage(''); // Empty
			}).toThrow('Invalid target_language');
		});
	});

	describe('API Key Management', () => {
		it('sets API key', () => {
			configStore.setAPIKey('sk-test-key-12345');
			const state = get(configStore);

			expect(state.api_key).toBe('sk-test-key-12345');
		});

		it('does NOT persist API key to localStorage', () => {
			configStore.setAPIKey('sk-secret-key-67890');

			const stored = localStorageMock['luminote_config'];
			if (stored) {
				const parsed = JSON.parse(stored);
				expect(parsed.api_key).toBeUndefined();
			}
		});

		it('API key is NOT loaded from localStorage', () => {
			// Try to manually inject API key into localStorage
			localStorageMock['luminote_config'] = JSON.stringify({
				provider: 'openai',
				model: 'gpt-4',
				target_language: 'en',
				api_key: 'sk-should-not-be-loaded'
			});

			configStore.reset();
			const state = get(configStore);

			expect(state.api_key).toBe(''); // Should be empty
		});

		it('allows empty API key', () => {
			configStore.setAPIKey('test-key');
			configStore.setAPIKey('');

			const state = get(configStore);
			expect(state.api_key).toBe('');
		});
	});

	describe('Reset Functionality', () => {
		it('resets all fields to defaults', () => {
			configStore.setProvider('anthropic');
			configStore.setModel('claude-3-opus');
			configStore.setTargetLanguage('fr');
			configStore.setAPIKey('test-key');

			configStore.reset();
			const state = get(configStore);

			expect(state.provider).toBe(DEFAULT_CONFIG_EXPORT.provider);
			expect(state.model).toBe(DEFAULT_CONFIG_EXPORT.model);
			expect(state.target_language).toBe(DEFAULT_CONFIG_EXPORT.target_language);
			expect(state.api_key).toBe(DEFAULT_CONFIG_EXPORT.api_key);
		});

		it('removes config from localStorage on reset', () => {
			configStore.setProvider('anthropic');
			expect(localStorageMock['luminote_config']).toBeDefined();

			configStore.reset();
			expect(localStorageMock['luminote_config']).toBeUndefined();
		});
	});

	describe('Persistence', () => {
		it('persists configuration excluding API key', () => {
			configStore.setProvider('anthropic');
			configStore.setModel('claude-3-opus');
			configStore.setTargetLanguage('es');
			configStore.setAPIKey('sk-secret');

			const stored = localStorageMock['luminote_config'];
			expect(stored).toBeDefined();

			const parsed = JSON.parse(stored);
			expect(parsed.provider).toBe('anthropic');
			expect(parsed.model).toBe('claude-3-opus');
			expect(parsed.target_language).toBe('es');
			expect(parsed.api_key).toBeUndefined();
		});

		it('maintains state across multiple updates', () => {
			configStore.setProvider('openai');
			configStore.setModel('gpt-4-turbo');
			configStore.setTargetLanguage('de');

			const state = get(configStore);

			expect(state.provider).toBe('openai');
			expect(state.model).toBe('gpt-4-turbo');
			expect(state.target_language).toBe('de');
		});
	});

	describe('Store Subscription', () => {
		it('notifies subscribers on provider change', () => {
			const values: string[] = [];
			const unsubscribe = configStore.subscribe((state) => {
				values.push(state.provider);
			});

			configStore.setProvider('anthropic');
			configStore.setProvider('openai');

			unsubscribe();

			// First value is initial state, then the two changes
			expect(values.length).toBeGreaterThanOrEqual(2);
			expect(values).toContain('anthropic');
			expect(values).toContain('openai');
		});

		it('notifies subscribers on model change', () => {
			const values: string[] = [];
			const unsubscribe = configStore.subscribe((state) => {
				values.push(state.model);
			});

			configStore.setModel('gpt-4-turbo');
			configStore.setModel('claude-3-opus');

			unsubscribe();

			expect(values).toContain('gpt-4-turbo');
			expect(values).toContain('claude-3-opus');
		});

		it('notifies subscribers on target language change', () => {
			const values: string[] = [];
			const unsubscribe = configStore.subscribe((state) => {
				values.push(state.target_language);
			});

			configStore.setTargetLanguage('es');
			configStore.setTargetLanguage('fr');

			unsubscribe();

			expect(values).toContain('es');
			expect(values).toContain('fr');
		});

		it('notifies subscribers on API key change', () => {
			const values: string[] = [];
			const unsubscribe = configStore.subscribe((state) => {
				values.push(state.api_key);
			});

			configStore.setAPIKey('key1');
			configStore.setAPIKey('key2');

			unsubscribe();

			expect(values).toContain('key1');
			expect(values).toContain('key2');
		});

		it('notifies subscribers on reset', () => {
			configStore.setProvider('anthropic');

			const values: ConfigState[] = [];
			const unsubscribe = configStore.subscribe((state) => {
				values.push({ ...state });
			});

			configStore.reset();

			unsubscribe();

			const lastValue = values[values.length - 1];
			expect(lastValue.provider).toBe('openai');
			expect(lastValue.model).toBe('gpt-4');
			expect(lastValue.target_language).toBe('en');
			expect(lastValue.api_key).toBe('');
		});
	});

	describe('Validation', () => {
		it('validates provider on set()', () => {
			expect(() => {
				configStore.set({
					// @ts-expect-error - Testing invalid input
					provider: 'invalid',
					model: 'gpt-4',
					target_language: 'en',
					api_key: ''
				});
			}).toThrow('Invalid provider');
		});

		it('validates model on set()', () => {
			expect(() => {
				configStore.set({
					provider: 'openai',
					model: '',
					target_language: 'en',
					api_key: ''
				});
			}).toThrow('Invalid model');
		});

		it('validates target_language on set()', () => {
			expect(() => {
				configStore.set({
					provider: 'openai',
					model: 'gpt-4',
					target_language: 'invalid',
					api_key: ''
				});
			}).toThrow('Invalid target_language');
		});

		it('allows valid set()', () => {
			expect(() => {
				configStore.set({
					provider: 'anthropic',
					model: 'claude-3-opus',
					target_language: 'es',
					api_key: 'test-key'
				});
			}).not.toThrow();

			const state = get(configStore);
			expect(state.provider).toBe('anthropic');
			expect(state.model).toBe('claude-3-opus');
			expect(state.target_language).toBe('es');
			expect(state.api_key).toBe('test-key');
		});

		it('validates provider on update()', () => {
			expect(() => {
				configStore.update((state) => ({
					...state,
					// @ts-expect-error - Testing invalid input
					provider: 'invalid'
				}));
			}).toThrow('Invalid provider');
		});

		it('validates model on update()', () => {
			expect(() => {
				configStore.update((state) => ({
					...state,
					model: ''
				}));
			}).toThrow('Invalid model');
		});

		it('validates target_language on update()', () => {
			expect(() => {
				configStore.update((state) => ({
					...state,
					target_language: 'invalid'
				}));
			}).toThrow('Invalid target_language');
		});
	});

	describe('Error Handling', () => {
		it('handles localStorage errors gracefully on save', () => {
			// Mock setItem to throw error
			vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
				throw new Error('QuotaExceededError');
			});

			// Should not throw
			expect(() => {
				configStore.setProvider('anthropic');
			}).not.toThrow();
		});

		it('handles localStorage errors gracefully on reset', () => {
			// Mock removeItem to throw error
			vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
				throw new Error('Storage error');
			});

			// Should not throw
			expect(() => {
				configStore.reset();
			}).not.toThrow();
		});
	});
});
