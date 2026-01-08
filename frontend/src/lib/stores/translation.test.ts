/**
 * Unit tests for translation store.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { translationStore, canTranslate } from './translation';

describe('Translation Store', () => {
	beforeEach(() => {
		// Reset store before each test
		translationStore.reset();
	});

	it('initializes with default values', () => {
		const state = get(translationStore);

		expect(state.sourceText).toBe('');
		expect(state.translatedText).toBe('');
		expect(state.sourceLanguage).toBe('en');
		expect(state.targetLanguage).toBe('es');
		expect(state.isLoading).toBe(false);
		expect(state.error).toBeNull();
	});

	it('sets source text', () => {
		translationStore.setSourceText('Hello, world!');
		const state = get(translationStore);

		expect(state.sourceText).toBe('Hello, world!');
		expect(state.error).toBeNull();
	});

	it('sets translated text', () => {
		translationStore.setTranslatedText('¡Hola, mundo!');
		const state = get(translationStore);

		expect(state.translatedText).toBe('¡Hola, mundo!');
	});

	it('sets source language', () => {
		translationStore.setSourceLanguage('fr');
		const state = get(translationStore);

		expect(state.sourceLanguage).toBe('fr');
		expect(state.error).toBeNull();
	});

	it('sets target language', () => {
		translationStore.setTargetLanguage('de');
		const state = get(translationStore);

		expect(state.targetLanguage).toBe('de');
		expect(state.error).toBeNull();
	});

	it('sets loading state', () => {
		translationStore.setLoading(true);
		let state = get(translationStore);
		expect(state.isLoading).toBe(true);

		translationStore.setLoading(false);
		state = get(translationStore);
		expect(state.isLoading).toBe(false);
	});

	it('sets error and clears loading state', () => {
		translationStore.setLoading(true);
		translationStore.setError('Test error');
		const state = get(translationStore);

		expect(state.error).toBe('Test error');
		expect(state.isLoading).toBe(false);
	});

	it('clears error when setting source text', () => {
		translationStore.setError('Previous error');
		translationStore.setSourceText('New text');
		const state = get(translationStore);

		expect(state.sourceText).toBe('New text');
		expect(state.error).toBeNull();
	});

	it('resets to initial state', () => {
		translationStore.setSourceText('Some text');
		translationStore.setTranslatedText('Translated text');
		translationStore.setSourceLanguage('fr');
		translationStore.setTargetLanguage('de');
		translationStore.setLoading(true);
		translationStore.setError('Error');

		translationStore.reset();
		const state = get(translationStore);

		expect(state.sourceText).toBe('');
		expect(state.translatedText).toBe('');
		expect(state.sourceLanguage).toBe('en');
		expect(state.targetLanguage).toBe('es');
		expect(state.isLoading).toBe(false);
		expect(state.error).toBeNull();
	});

	describe('canTranslate derived store', () => {
		it('returns false when source text is empty', () => {
			expect(get(canTranslate)).toBe(false);
		});

		it('returns false when source text is only whitespace', () => {
			translationStore.setSourceText('   ');
			expect(get(canTranslate)).toBe(false);
		});

		it('returns false when loading', () => {
			translationStore.setSourceText('Hello');
			translationStore.setLoading(true);
			expect(get(canTranslate)).toBe(false);
		});

		it('returns true when source text exists and not loading', () => {
			translationStore.setSourceText('Hello');
			expect(get(canTranslate)).toBe(true);
		});
	});

	it('maintains state across multiple updates', () => {
		translationStore.setSourceText('Hello');
		translationStore.setSourceLanguage('en');
		translationStore.setTargetLanguage('es');
		translationStore.setLoading(true);

		const state = get(translationStore);

		expect(state.sourceText).toBe('Hello');
		expect(state.sourceLanguage).toBe('en');
		expect(state.targetLanguage).toBe('es');
		expect(state.isLoading).toBe(true);
	});
});
