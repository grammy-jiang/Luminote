/**
 * Unit tests for BlockMapping utility.
 */

import { describe, it, expect } from 'vitest';
import { BlockMapping } from './block-mapping';

describe('BlockMapping', () => {
	describe('constructor', () => {
		it('should create an empty mapping when no entries provided', () => {
			const mapping = new BlockMapping();

			expect(mapping.size).toBe(0);
			expect(mapping.getSourceIds()).toEqual([]);
			expect(mapping.getTranslationIds()).toEqual([]);
		});

		it('should create mapping with initial entries', () => {
			const entries: Array<[string, string]> = [
				['source-1', 'translation-1'],
				['source-2', 'translation-2'],
				['source-3', 'translation-3']
			];
			const mapping = new BlockMapping(entries);

			expect(mapping.size).toBe(3);
			expect(mapping.getSourceIds()).toEqual(['source-1', 'source-2', 'source-3']);
			expect(mapping.getTranslationIds()).toEqual([
				'translation-1',
				'translation-2',
				'translation-3'
			]);
		});

		it('should handle empty entries array', () => {
			const mapping = new BlockMapping([]);

			expect(mapping.size).toBe(0);
		});
	});

	describe('map (forward mapping)', () => {
		it('should map source ID to translation ID', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			expect(mapping.map('source-1')).toBe('translation-1');
			expect(mapping.map('source-2')).toBe('translation-2');
		});

		it('should return null for unmapped source ID', () => {
			const mapping = new BlockMapping([['source-1', 'translation-1']]);

			expect(mapping.map('source-999')).toBeNull();
		});

		it('should return null for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.map('any-id')).toBeNull();
		});

		it('should handle special characters in IDs', () => {
			const mapping = new BlockMapping([
				['source-with-dash', 'translation-with-dash'],
				['source_with_underscore', 'translation_with_underscore'],
				['source.with.dot', 'translation.with.dot']
			]);

			expect(mapping.map('source-with-dash')).toBe('translation-with-dash');
			expect(mapping.map('source_with_underscore')).toBe('translation_with_underscore');
			expect(mapping.map('source.with.dot')).toBe('translation.with.dot');
		});
	});

	describe('reverseMap (reverse mapping)', () => {
		it('should reverse map translation ID to source ID', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			expect(mapping.reverseMap('translation-1')).toBe('source-1');
			expect(mapping.reverseMap('translation-2')).toBe('source-2');
		});

		it('should return null for unmapped translation ID', () => {
			const mapping = new BlockMapping([['source-1', 'translation-1']]);

			expect(mapping.reverseMap('translation-999')).toBeNull();
		});

		it('should return null for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.reverseMap('any-id')).toBeNull();
		});

		it('should handle special characters in translation IDs', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-with-dash'],
				['source-2', 'translation_with_underscore'],
				['source-3', 'translation.with.dot']
			]);

			expect(mapping.reverseMap('translation-with-dash')).toBe('source-1');
			expect(mapping.reverseMap('translation_with_underscore')).toBe('source-2');
			expect(mapping.reverseMap('translation.with.dot')).toBe('source-3');
		});
	});

	describe('has', () => {
		it('should return true for existing source ID', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			expect(mapping.has('source-1')).toBe(true);
			expect(mapping.has('source-2')).toBe(true);
		});

		it('should return true for existing translation ID', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			expect(mapping.has('translation-1')).toBe(true);
			expect(mapping.has('translation-2')).toBe(true);
		});

		it('should return false for non-existent ID', () => {
			const mapping = new BlockMapping([['source-1', 'translation-1']]);

			expect(mapping.has('source-999')).toBe(false);
			expect(mapping.has('translation-999')).toBe(false);
		});

		it('should return false for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.has('any-id')).toBe(false);
		});
	});

	describe('add (immutable)', () => {
		it('should return new mapping with added entry', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);

			const updated = original.add('source-2', 'translation-2');

			// Original unchanged
			expect(original.size).toBe(1);
			expect(original.map('source-2')).toBeNull();

			// Updated has both entries
			expect(updated.size).toBe(2);
			expect(updated.map('source-1')).toBe('translation-1');
			expect(updated.map('source-2')).toBe('translation-2');
		});

		it('should allow adding to empty mapping', () => {
			const original = new BlockMapping();

			const updated = original.add('source-1', 'translation-1');

			expect(original.size).toBe(0);
			expect(updated.size).toBe(1);
			expect(updated.map('source-1')).toBe('translation-1');
		});

		it('should allow overwriting existing mapping', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);

			const updated = original.add('source-1', 'translation-new');

			// Original unchanged
			expect(original.map('source-1')).toBe('translation-1');

			// Updated has new translation
			expect(updated.map('source-1')).toBe('translation-new');
			expect(updated.reverseMap('translation-1')).toBeNull();
			expect(updated.reverseMap('translation-new')).toBe('source-1');
		});
	});

	describe('remove (immutable)', () => {
		it('should return new mapping with entry removed', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			const updated = original.remove('source-1');

			// Original unchanged
			expect(original.size).toBe(2);
			expect(original.map('source-1')).toBe('translation-1');

			// Updated has entry removed
			expect(updated.size).toBe(1);
			expect(updated.map('source-1')).toBeNull();
			expect(updated.map('source-2')).toBe('translation-2');
		});

		it('should handle removing non-existent ID', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);

			const updated = original.remove('source-999');

			expect(original.size).toBe(1);
			expect(updated.size).toBe(1);
			expect(updated.map('source-1')).toBe('translation-1');
		});

		it('should handle removing from empty mapping', () => {
			const original = new BlockMapping();

			const updated = original.remove('any-id');

			expect(original.size).toBe(0);
			expect(updated.size).toBe(0);
		});
	});

	describe('clear (immutable)', () => {
		it('should return new empty mapping', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			const cleared = original.clear();

			// Original unchanged
			expect(original.size).toBe(2);
			expect(original.map('source-1')).toBe('translation-1');

			// Cleared is empty
			expect(cleared.size).toBe(0);
			expect(cleared.map('source-1')).toBeNull();
		});

		it('should handle clearing empty mapping', () => {
			const original = new BlockMapping();

			const cleared = original.clear();

			expect(original.size).toBe(0);
			expect(cleared.size).toBe(0);
		});
	});

	describe('size', () => {
		it('should return correct size for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.size).toBe(0);
		});

		it('should return correct size for non-empty mapping', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2'],
				['source-3', 'translation-3']
			]);

			expect(mapping.size).toBe(3);
		});

		it('should update size after add', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);
			const updated = original.add('source-2', 'translation-2');

			expect(original.size).toBe(1);
			expect(updated.size).toBe(2);
		});

		it('should update size after remove', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);
			const updated = original.remove('source-1');

			expect(original.size).toBe(2);
			expect(updated.size).toBe(1);
		});
	});

	describe('getSourceIds', () => {
		it('should return empty array for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.getSourceIds()).toEqual([]);
		});

		it('should return all source IDs', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2'],
				['source-3', 'translation-3']
			]);

			const sourceIds = mapping.getSourceIds();

			expect(sourceIds).toHaveLength(3);
			expect(sourceIds).toContain('source-1');
			expect(sourceIds).toContain('source-2');
			expect(sourceIds).toContain('source-3');
		});
	});

	describe('getTranslationIds', () => {
		it('should return empty array for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.getTranslationIds()).toEqual([]);
		});

		it('should return all translation IDs', () => {
			const mapping = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2'],
				['source-3', 'translation-3']
			]);

			const translationIds = mapping.getTranslationIds();

			expect(translationIds).toHaveLength(3);
			expect(translationIds).toContain('translation-1');
			expect(translationIds).toContain('translation-2');
			expect(translationIds).toContain('translation-3');
		});
	});

	describe('entries', () => {
		it('should return empty array for empty mapping', () => {
			const mapping = new BlockMapping();

			expect(mapping.entries()).toEqual([]);
		});

		it('should return all entries as tuples', () => {
			const entries: Array<[string, string]> = [
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			];
			const mapping = new BlockMapping(entries);

			const result = mapping.entries();

			expect(result).toEqual(entries);
		});

		it('should return entries that can reconstruct the mapping', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);

			const entries = original.entries();
			const reconstructed = new BlockMapping(entries);

			expect(reconstructed.size).toBe(original.size);
			expect(reconstructed.map('source-1')).toBe('translation-1');
			expect(reconstructed.map('source-2')).toBe('translation-2');
			expect(reconstructed.reverseMap('translation-1')).toBe('source-1');
			expect(reconstructed.reverseMap('translation-2')).toBe('source-2');
		});
	});

	describe('Performance (O(1) lookups)', () => {
		it('should handle large mappings efficiently', () => {
			// Create large mapping
			const largeEntries: Array<[string, string]> = [];
			for (let i = 0; i < 10000; i++) {
				largeEntries.push([`source-${i}`, `translation-${i}`]);
			}
			const mapping = new BlockMapping(largeEntries);

			// Test O(1) lookups - should be instant even with 10k entries
			const start = performance.now();

			expect(mapping.map('source-0')).toBe('translation-0');
			expect(mapping.map('source-5000')).toBe('translation-5000');
			expect(mapping.map('source-9999')).toBe('translation-9999');

			expect(mapping.reverseMap('translation-0')).toBe('source-0');
			expect(mapping.reverseMap('translation-5000')).toBe('source-5000');
			expect(mapping.reverseMap('translation-9999')).toBe('source-9999');

			expect(mapping.has('source-7500')).toBe(true);
			expect(mapping.has('translation-2500')).toBe(true);

			const end = performance.now();
			const duration = end - start;

			// All operations should complete in less than 10ms
			expect(duration).toBeLessThan(10);
		});
	});

	describe('Immutability', () => {
		it('should not mutate original when adding', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);
			const originalEntries = original.entries();

			original.add('source-2', 'translation-2');

			// Original should be unchanged
			expect(original.entries()).toEqual(originalEntries);
			expect(original.size).toBe(1);
		});

		it('should not mutate original when removing', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);
			const originalEntries = original.entries();

			original.remove('source-1');

			// Original should be unchanged
			expect(original.entries()).toEqual(originalEntries);
			expect(original.size).toBe(2);
		});

		it('should not mutate original when clearing', () => {
			const original = new BlockMapping([
				['source-1', 'translation-1'],
				['source-2', 'translation-2']
			]);
			const originalEntries = original.entries();

			original.clear();

			// Original should be unchanged
			expect(original.entries()).toEqual(originalEntries);
			expect(original.size).toBe(2);
		});

		it('should allow chaining immutable operations', () => {
			const original = new BlockMapping([['source-1', 'translation-1']]);

			const result = original
				.add('source-2', 'translation-2')
				.add('source-3', 'translation-3')
				.remove('source-1');

			// Original unchanged
			expect(original.size).toBe(1);
			expect(original.map('source-1')).toBe('translation-1');

			// Result has chained changes
			expect(result.size).toBe(2);
			expect(result.map('source-1')).toBeNull();
			expect(result.map('source-2')).toBe('translation-2');
			expect(result.map('source-3')).toBe('translation-3');
		});
	});

	describe('Edge Cases', () => {
		it('should handle empty string IDs', () => {
			const mapping = new BlockMapping([['', 'translation-empty']]);

			expect(mapping.map('')).toBe('translation-empty');
			expect(mapping.reverseMap('translation-empty')).toBe('');
			expect(mapping.has('')).toBe(true);
		});

		it('should handle numeric string IDs', () => {
			const mapping = new BlockMapping([
				['123', '456'],
				['789', '101112']
			]);

			expect(mapping.map('123')).toBe('456');
			expect(mapping.reverseMap('456')).toBe('123');
		});

		it('should handle UUID-like IDs', () => {
			const mapping = new BlockMapping([
				['550e8400-e29b-41d4-a716-446655440000', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890']
			]);

			expect(mapping.map('550e8400-e29b-41d4-a716-446655440000')).toBe(
				'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
			);
			expect(mapping.reverseMap('a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(
				'550e8400-e29b-41d4-a716-446655440000'
			);
		});

		it('should distinguish between similar IDs', () => {
			const mapping = new BlockMapping([
				['block', 'translation-1'],
				['block-1', 'translation-2'],
				['block-10', 'translation-3']
			]);

			expect(mapping.map('block')).toBe('translation-1');
			expect(mapping.map('block-1')).toBe('translation-2');
			expect(mapping.map('block-10')).toBe('translation-3');
		});
	});

	describe('Graceful handling of unmapped blocks', () => {
		it('should return null consistently for unmapped IDs', () => {
			const mapping = new BlockMapping([['source-1', 'translation-1']]);

			// Multiple calls should return null consistently
			expect(mapping.map('unmapped')).toBeNull();
			expect(mapping.map('unmapped')).toBeNull();
			expect(mapping.reverseMap('unmapped')).toBeNull();
			expect(mapping.reverseMap('unmapped')).toBeNull();
		});

		it('should not throw errors for unmapped IDs', () => {
			const mapping = new BlockMapping();

			// Should not throw
			expect(() => mapping.map('any-id')).not.toThrow();
			expect(() => mapping.reverseMap('any-id')).not.toThrow();
			expect(() => mapping.has('any-id')).not.toThrow();
		});
	});
});
