/**
 * Translation store for managing translation state.
 */

import { writable, derived } from 'svelte/store';

export interface TranslationState {
	sourceText: string;
	translatedText: string;
	sourceLanguage: string;
	targetLanguage: string;
	isLoading: boolean;
	error: string | null;
}

const initialState: TranslationState = {
	sourceText: '',
	translatedText: '',
	sourceLanguage: 'en',
	targetLanguage: 'es',
	isLoading: false,
	error: null
};

function createTranslationStore() {
	const { subscribe, set, update } = writable<TranslationState>(initialState);

	return {
		subscribe,
		setSourceText: (text: string) =>
			update((state) => ({ ...state, sourceText: text, error: null })),
		setTranslatedText: (text: string) => update((state) => ({ ...state, translatedText: text })),
		setSourceLanguage: (lang: string) =>
			update((state) => ({ ...state, sourceLanguage: lang, error: null })),
		setTargetLanguage: (lang: string) =>
			update((state) => ({ ...state, targetLanguage: lang, error: null })),
		setLoading: (loading: boolean) => update((state) => ({ ...state, isLoading: loading })),
		setError: (error: string | null) => update((state) => ({ ...state, error, isLoading: false })),
		reset: () => set(initialState)
	};
}

export const translationStore = createTranslationStore();

// Derived store to check if translation is ready
export const canTranslate = derived(
	translationStore,
	($store) => $store.sourceText.trim().length > 0 && !$store.isLoading
);
