/**
 * Keyboard navigation utilities for content blocks.
 *
 * Provides reusable functions for navigating between content blocks
 * using keyboard shortcuts (Arrow keys, Home/End).
 */

import type { ContentBlock } from '$lib/types/api';

/**
 * Navigate to the adjacent block (next or previous).
 *
 * @param blocks - Array of content blocks
 * @param currentBlockId - ID of the currently focused block
 * @param direction - Direction to navigate ('next' or 'previous')
 * @returns void
 */
export function navigateToAdjacentBlock(
	blocks: ContentBlock[],
	currentBlockId: string,
	direction: 'next' | 'previous'
): void {
	const currentIndex = blocks.findIndex((block) => block.id === currentBlockId);
	if (currentIndex === -1) return;

	const targetIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
	if (targetIndex >= 0 && targetIndex < blocks.length) {
		const targetBlock = blocks[targetIndex];
		focusBlock(targetBlock.id);
	}
}

/**
 * Navigate to the first block.
 *
 * @param blocks - Array of content blocks
 * @returns void
 */
export function navigateToFirstBlock(blocks: ContentBlock[]): void {
	if (blocks.length > 0) {
		focusBlock(blocks[0].id);
	}
}

/**
 * Navigate to the last block.
 *
 * @param blocks - Array of content blocks
 * @returns void
 */
export function navigateToLastBlock(blocks: ContentBlock[]): void {
	if (blocks.length > 0) {
		focusBlock(blocks[blocks.length - 1].id);
	}
}

/**
 * Focus a specific block by its ID.
 *
 * Uses setTimeout to ensure DOM is updated before focusing.
 * Scrolls the block into view with smooth behavior.
 *
 * @param blockId - ID of the block to focus
 * @returns void
 */
export function focusBlock(blockId: string): void {
	// Use setTimeout to ensure DOM is updated
	setTimeout(() => {
		const blockElement = document.querySelector(`[data-block-id="${blockId}"]`) as HTMLElement;
		if (blockElement) {
			blockElement.focus();
			// Scroll into view if needed (check if function exists for test compatibility)
			if (typeof blockElement.scrollIntoView === 'function') {
				blockElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
			}
		}
	}, 0);
}
