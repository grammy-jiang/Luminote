/**
 * Central export for all Svelte stores.
 *
 * Makes importing stores cleaner:
 * ```typescript
 * import { configStore, translationStore } from '$lib/stores';
 * ```
 */

export { configStore, type ConfigState, DEFAULT_CONFIG_EXPORT } from './config';
export { translationStore, canTranslate, type TranslationState } from './translation';
