/**
 * Block ID Mapping Utility
 *
 * Maps source block IDs to translation block IDs for synchronization features
 * (hover, click, scroll). Provides O(1) lookup performance using Maps.
 *
 * Features:
 * - Forward mapping (source → translation)
 * - Reverse mapping (translation → source)
 * - O(1) lookup performance
 * - Handles unmapped blocks gracefully (returns null)
 * - TypeScript type-safe
 * - Immutable API (returns new instance on updates)
 *
 * @example
 * ```typescript
 * const mapping = new BlockMapping([
 *   ['source-1', 'translation-1'],
 *   ['source-2', 'translation-2']
 * ]);
 *
 * const translationId = mapping.map('source-1'); // 'translation-1'
 * const sourceId = mapping.reverseMap('translation-1'); // 'source-1'
 * const exists = mapping.has('source-1'); // true
 * ```
 */

/**
 * BlockMapping class for managing bidirectional block ID mappings.
 *
 * This class maintains two internal Maps for O(1) lookup performance in both directions.
 * All methods are designed to be immutable - they don't modify the existing instance.
 */
export class BlockMapping {
	/** Internal map from source IDs to translation IDs */
	private readonly sourceToTranslation: Map<string, string>;

	/** Internal map from translation IDs to source IDs (reverse lookup) */
	private readonly translationToSource: Map<string, string>;

	/**
	 * Create a new BlockMapping instance.
	 *
	 * @param entries - Optional array of [sourceId, translationId] tuples to initialize the mapping
	 *
	 * @example
	 * ```typescript
	 * // Empty mapping
	 * const emptyMapping = new BlockMapping();
	 *
	 * // Mapping with initial entries
	 * const mapping = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * ```
	 */
	constructor(entries?: Array<[string, string]>) {
		this.sourceToTranslation = new Map();
		this.translationToSource = new Map();

		if (entries) {
			for (const [sourceId, translationId] of entries) {
				this.sourceToTranslation.set(sourceId, translationId);
				this.translationToSource.set(translationId, sourceId);
			}
		}
	}

	/**
	 * Map a source block ID to its corresponding translation block ID.
	 *
	 * @param sourceId - The source block ID to look up
	 * @returns The corresponding translation block ID, or null if not found
	 *
	 * @example
	 * ```typescript
	 * const translationId = mapping.map('source-1');
	 * if (translationId) {
	 *   console.log(`Found translation: ${translationId}`);
	 * } else {
	 *   console.log('No translation found');
	 * }
	 * ```
	 */
	map(sourceId: string): string | null {
		return this.sourceToTranslation.get(sourceId) ?? null;
	}

	/**
	 * Reverse map a translation block ID to its corresponding source block ID.
	 *
	 * @param translationId - The translation block ID to look up
	 * @returns The corresponding source block ID, or null if not found
	 *
	 * @example
	 * ```typescript
	 * const sourceId = mapping.reverseMap('translation-1');
	 * if (sourceId) {
	 *   console.log(`Found source: ${sourceId}`);
	 * } else {
	 *   console.log('No source found');
	 * }
	 * ```
	 */
	reverseMap(translationId: string): string | null {
		return this.translationToSource.get(translationId) ?? null;
	}

	/**
	 * Check if a block ID exists in the mapping (checks both source and translation IDs).
	 *
	 * @param id - The block ID to check (can be either source or translation ID)
	 * @returns true if the ID exists in either direction, false otherwise
	 *
	 * @example
	 * ```typescript
	 * if (mapping.has('source-1')) {
	 *   // ID exists as source
	 * }
	 * if (mapping.has('translation-1')) {
	 *   // ID exists as translation
	 * }
	 * ```
	 */
	has(id: string): boolean {
		return this.sourceToTranslation.has(id) || this.translationToSource.has(id);
	}

	/**
	 * Create a new BlockMapping instance with an additional mapping.
	 * The original instance remains unchanged (immutable API).
	 * If the sourceId already exists, it will be replaced with the new mapping.
	 *
	 * @param sourceId - The source block ID
	 * @param translationId - The translation block ID
	 * @returns A new BlockMapping instance with the added mapping
	 *
	 * @example
	 * ```typescript
	 * const original = new BlockMapping([['block-1', 'trans-1']]);
	 * const updated = original.add('block-2', 'trans-2');
	 * // original is unchanged, updated has both mappings
	 * ```
	 */
	add(sourceId: string, translationId: string): BlockMapping {
		// Filter out existing mapping for this source ID to handle overwrites
		const entries = Array.from(this.sourceToTranslation.entries()).filter(
			([id]) => id !== sourceId
		);
		entries.push([sourceId, translationId]);
		return new BlockMapping(entries);
	}

	/**
	 * Create a new BlockMapping instance with a mapping removed.
	 * The original instance remains unchanged (immutable API).
	 *
	 * @param sourceId - The source block ID to remove
	 * @returns A new BlockMapping instance without the specified mapping
	 *
	 * @example
	 * ```typescript
	 * const original = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * const updated = original.remove('block-1');
	 * // original is unchanged, updated only has block-2 mapping
	 * ```
	 */
	remove(sourceId: string): BlockMapping {
		const entries = Array.from(this.sourceToTranslation.entries()).filter(
			([id]) => id !== sourceId
		);
		return new BlockMapping(entries);
	}

	/**
	 * Get the number of mappings in this instance.
	 *
	 * @returns The number of source→translation mappings
	 *
	 * @example
	 * ```typescript
	 * const mapping = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * console.log(mapping.size); // 2
	 * ```
	 */
	get size(): number {
		return this.sourceToTranslation.size;
	}

	/**
	 * Create a new empty BlockMapping instance.
	 * The original instance remains unchanged (immutable API).
	 *
	 * @returns A new empty BlockMapping instance
	 *
	 * @example
	 * ```typescript
	 * const mapping = new BlockMapping([['block-1', 'trans-1']]);
	 * const cleared = mapping.clear();
	 * // mapping is unchanged, cleared is empty
	 * ```
	 */
	clear(): BlockMapping {
		return new BlockMapping();
	}

	/**
	 * Get all source block IDs in this mapping.
	 *
	 * @returns Array of all source block IDs
	 *
	 * @example
	 * ```typescript
	 * const mapping = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * const sourceIds = mapping.getSourceIds(); // ['block-1', 'block-2']
	 * ```
	 */
	getSourceIds(): string[] {
		return Array.from(this.sourceToTranslation.keys());
	}

	/**
	 * Get all translation block IDs in this mapping.
	 *
	 * @returns Array of all translation block IDs
	 *
	 * @example
	 * ```typescript
	 * const mapping = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * const translationIds = mapping.getTranslationIds(); // ['trans-1', 'trans-2']
	 * ```
	 */
	getTranslationIds(): string[] {
		return Array.from(this.sourceToTranslation.values());
	}

	/**
	 * Get all mappings as an array of [sourceId, translationId] tuples.
	 *
	 * @returns Array of [sourceId, translationId] tuples
	 *
	 * @example
	 * ```typescript
	 * const mapping = new BlockMapping([
	 *   ['block-1', 'trans-1'],
	 *   ['block-2', 'trans-2']
	 * ]);
	 * const entries = mapping.entries();
	 * // [['block-1', 'trans-1'], ['block-2', 'trans-2']]
	 * ```
	 */
	entries(): Array<[string, string]> {
		return Array.from(this.sourceToTranslation.entries());
	}
}
