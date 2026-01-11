/**
 * Configuration store for managing user settings.
 *
 * Follows ADR-003 (Client-Side Storage Strategy) and ADR-005 (Frontend State Management).
 *
 * - Configuration persisted to localStorage (excluding API key)
 * - API key stored in memory only for security
 * - Type-safe configuration interface
 * - SSR-compatible (checks for window)
 * - Validation on set operations
 */

import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

/**
 * Configuration state interface.
 */
export interface ConfigState {
	/** AI provider (e.g., 'openai', 'anthropic') */
	provider: 'openai' | 'anthropic';
	/** Model name (e.g., 'gpt-4', 'claude-3-opus') */
	model: string;
	/** Target language code (ISO 639-1 format: 'en', 'es', 'fr', etc.) */
	target_language: string;
	/** API key (memory-only, never persisted) */
	api_key: string;
}

/**
 * Default configuration values.
 */
const DEFAULT_CONFIG: ConfigState = {
	provider: 'openai',
	model: 'gpt-4',
	target_language: 'en',
	api_key: ''
};

/**
 * localStorage key for configuration persistence.
 */
const STORAGE_KEY = 'luminote_config';

/**
 * Validate provider value.
 */
function validateProvider(provider: string): provider is 'openai' | 'anthropic' {
	return provider === 'openai' || provider === 'anthropic';
}

/**
 * Validate model name (basic validation).
 */
function validateModel(model: string): boolean {
	return typeof model === 'string' && model.trim().length > 0;
}

/**
 * Validate language code (ISO 639-1: two lowercase letters).
 */
function validateLanguage(language: string): boolean {
	return /^[a-z]{2}$/.test(language);
}

/**
 * Load configuration from localStorage.
 * Returns default config if storage unavailable or invalid.
 */
function loadFromStorage(): ConfigState {
	// SSR compatibility: check for window
	if (typeof window === 'undefined') {
		return { ...DEFAULT_CONFIG };
	}

	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (!stored) {
			return { ...DEFAULT_CONFIG };
		}

		const parsed = JSON.parse(stored);

		// Validate parsed data
		if (!validateProvider(parsed.provider)) {
			console.warn('Invalid provider in stored config, using default');
			return { ...DEFAULT_CONFIG };
		}

		if (!validateModel(parsed.model)) {
			console.warn('Invalid model in stored config, using default');
			return { ...DEFAULT_CONFIG };
		}

		if (!validateLanguage(parsed.target_language)) {
			console.warn('Invalid target_language in stored config, using default');
			return { ...DEFAULT_CONFIG };
		}

		// Never load API key from localStorage (security)
		return {
			provider: parsed.provider,
			model: parsed.model,
			target_language: parsed.target_language,
			api_key: ''
		};
	} catch (error) {
		console.error('Error loading config from localStorage:', error);
		return { ...DEFAULT_CONFIG };
	}
}

/**
 * Save configuration to localStorage (excluding API key).
 */
function saveToStorage(state: ConfigState): void {
	// SSR compatibility: check for window
	if (typeof window === 'undefined') {
		return;
	}

	try {
		// Destructure to exclude api_key (never persist for security)
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		const { api_key, ...persistable } = state;
		localStorage.setItem(STORAGE_KEY, JSON.stringify(persistable));
	} catch (error) {
		console.error('Error saving config to localStorage:', error);
	}
}

/**
 * Create configuration store with persistence and validation.
 */
function createConfigStore(): Writable<ConfigState> & {
	setProvider: (provider: 'openai' | 'anthropic') => void;
	setModel: (model: string) => void;
	setTargetLanguage: (language: string) => void;
	setAPIKey: (key: string) => void;
	reset: () => void;
} {
	// Load initial state from localStorage
	const initialState = loadFromStorage();

	const { subscribe, set, update } = writable<ConfigState>(initialState);

	return {
		subscribe,
		set: (value: ConfigState) => {
			// Validate before setting
			if (!validateProvider(value.provider)) {
				throw new Error(`Invalid provider: ${value.provider}. Must be 'openai' or 'anthropic'.`);
			}
			if (!validateModel(value.model)) {
				throw new Error('Invalid model: must be a non-empty string.');
			}
			if (!validateLanguage(value.target_language)) {
				throw new Error(
					`Invalid target_language: ${value.target_language}. Must be ISO 639-1 format (e.g., 'en', 'es').`
				);
			}

			set(value);
			saveToStorage(value);
		},
		update: (updater: (state: ConfigState) => ConfigState) => {
			update((state) => {
				const newState = updater(state);

				// Validate before updating
				if (!validateProvider(newState.provider)) {
					throw new Error(
						`Invalid provider: ${newState.provider}. Must be 'openai' or 'anthropic'.`
					);
				}
				if (!validateModel(newState.model)) {
					throw new Error('Invalid model: must be a non-empty string.');
				}
				if (!validateLanguage(newState.target_language)) {
					throw new Error(
						`Invalid target_language: ${newState.target_language}. Must be ISO 639-1 format (e.g., 'en', 'es').`
					);
				}

				saveToStorage(newState);
				return newState;
			});
		},
		setProvider: (provider: 'openai' | 'anthropic') => {
			if (!validateProvider(provider)) {
				throw new Error(`Invalid provider: ${provider}. Must be 'openai' or 'anthropic'.`);
			}

			update((state) => {
				const newState = { ...state, provider };
				saveToStorage(newState);
				return newState;
			});
		},
		setModel: (model: string) => {
			if (!validateModel(model)) {
				throw new Error('Invalid model: must be a non-empty string.');
			}

			update((state) => {
				const newState = { ...state, model };
				saveToStorage(newState);
				return newState;
			});
		},
		setTargetLanguage: (target_language: string) => {
			if (!validateLanguage(target_language)) {
				throw new Error(
					`Invalid target_language: ${target_language}. Must be ISO 639-1 format (e.g., 'en', 'es').`
				);
			}

			update((state) => {
				const newState = { ...state, target_language };
				saveToStorage(newState);
				return newState;
			});
		},
		setAPIKey: (api_key: string) => {
			// API key is NOT validated (user-provided)
			// API key is NOT persisted (security)
			update((state) => ({ ...state, api_key }));
		},
		reset: () => {
			const defaultState = { ...DEFAULT_CONFIG };
			set(defaultState);

			// Remove from localStorage
			if (typeof window !== 'undefined') {
				try {
					localStorage.removeItem(STORAGE_KEY);
				} catch (error) {
					console.error('Error removing config from localStorage:', error);
				}
			}
		}
	};
}

/**
 * Configuration store singleton.
 */
export const configStore = createConfigStore();

/**
 * Export default config for testing.
 */
export const DEFAULT_CONFIG_EXPORT = DEFAULT_CONFIG;
