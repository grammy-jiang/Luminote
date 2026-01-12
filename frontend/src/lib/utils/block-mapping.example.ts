/**
 * Example usage of BlockMapping utility
 *
 * This file demonstrates how to use the BlockMapping class for
 * synchronizing source and translation blocks in the dual-pane layout.
 */

import { BlockMapping } from './block-mapping';

/**
 * Example 1: Creating a mapping from translation results
 */
function createMappingFromTranslation() {
	// Assume we have translation results
	const translationResults = [
		{ id: 'trans-1', sourceId: 'source-1', text: 'Hola mundo' },
		{ id: 'trans-2', sourceId: 'source-2', text: 'Este es un párrafo' },
		{ id: 'trans-3', sourceId: 'source-3', text: 'Otro bloque' }
	];

	// Create mapping entries
	const entries: Array<[string, string]> = translationResults.map((result) => [
		result.sourceId,
		result.id
	]);

	// Create the mapping
	const mapping = new BlockMapping(entries);

	console.log('Mapping created with', mapping.size, 'entries');
	return mapping;
}

/**
 * Example 2: Using the mapping for hover synchronization
 */
function handleSourceBlockHover(sourceBlockId: string, mapping: BlockMapping) {
	// When user hovers over a source block, highlight the corresponding translation
	const translationId = mapping.map(sourceBlockId);

	if (translationId) {
		console.log(`Highlighting translation block: ${translationId}`);
		// In real code: document.getElementById(translationId)?.classList.add('highlight');
	} else {
		console.log('No translation found for this block');
	}
}

/**
 * Example 3: Using reverse mapping for translation block clicks
 */
function handleTranslationBlockClick(translationBlockId: string, mapping: BlockMapping) {
	// When user clicks a translation block, scroll to the source
	const sourceId = mapping.reverseMap(translationBlockId);

	if (sourceId) {
		console.log(`Scrolling to source block: ${sourceId}`);
		// In real code: document.getElementById(sourceId)?.scrollIntoView();
	} else {
		console.log('No source found for this translation');
	}
}

/**
 * Example 4: Immutable updates - adding new translations progressively
 */
function progressiveTranslation() {
	// Start with empty mapping
	let mapping = new BlockMapping();

	// As translations arrive, add them immutably
	mapping = mapping.add('source-1', 'trans-1');
	console.log('After first translation:', mapping.size); // 1

	mapping = mapping.add('source-2', 'trans-2');
	console.log('After second translation:', mapping.size); // 2

	mapping = mapping.add('source-3', 'trans-3');
	console.log('After third translation:', mapping.size); // 3

	// Each operation returns a new mapping, original is unchanged
	return mapping;
}

/**
 * Example 5: Handling partial translations
 */
function handlePartialTranslations() {
	const mapping = new BlockMapping([
		['source-1', 'trans-1'],
		['source-2', 'trans-2']
		// source-3 not translated yet
	]);

	// Check before using
	if (mapping.has('source-3')) {
		console.log('Translation available');
	} else {
		console.log('Translation not yet available');
	}

	// Graceful handling of unmapped blocks
	const translationId = mapping.map('source-3');
	if (translationId === null) {
		console.log('Block not yet translated, showing placeholder');
	}
}

/**
 * Example 6: Re-translation scenario
 */
function handleRetranslation() {
	// Initial mapping
	let mapping = new BlockMapping([
		['source-1', 'trans-1'],
		['source-2', 'trans-2']
	]);

	// User requests re-translation of source-1
	// Remove old mapping
	mapping = mapping.remove('source-1');

	// Add new translation when it arrives
	mapping = mapping.add('source-1', 'trans-new-1');

	console.log('Updated mapping:', mapping.entries());
}

/**
 * Example 7: Bulk operations with performance
 */
function bulkOperations() {
	// Create mapping with many entries
	const entries: Array<[string, string]> = [];
	for (let i = 0; i < 1000; i++) {
		entries.push([`source-${i}`, `trans-${i}`]);
	}

	const mapping = new BlockMapping(entries);

	// O(1) lookups even with 1000 entries
	console.time('lookup');
	const result1 = mapping.map('source-0');
	const result2 = mapping.map('source-500');
	const result3 = mapping.map('source-999');
	console.timeEnd('lookup'); // Should be < 1ms

	console.log('Lookups found:', result1, result2, result3);
}

// Run examples
console.log('=== Example 1: Creating mapping ===');
const mapping = createMappingFromTranslation();

console.log('\n=== Example 2: Hover synchronization ===');
handleSourceBlockHover('source-1', mapping);
handleSourceBlockHover('source-999', mapping);

console.log('\n=== Example 3: Click synchronization ===');
handleTranslationBlockClick('trans-2', mapping);
handleTranslationBlockClick('trans-999', mapping);

console.log('\n=== Example 4: Progressive translation ===');
progressiveTranslation();

console.log('\n=== Example 5: Partial translations ===');
handlePartialTranslations();

console.log('\n=== Example 6: Re-translation ===');
handleRetranslation();

console.log('\n=== Example 7: Bulk operations ===');
bulkOperations();
