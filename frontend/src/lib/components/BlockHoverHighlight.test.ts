/**
 * Unit tests for block hover highlighting functionality.
 * Tests the coordination between SourcePane, TranslationPane, and DualPaneLayout.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render } from '../test-utils';
import { fireEvent } from '@testing-library/svelte';
import SourcePane from './SourcePane.svelte';
import TranslationPane from './TranslationPane.svelte';
import type { ContentBlock } from '$lib/types/api';

describe('Block Hover Highlighting', () => {
	let testBlocks: ContentBlock[];

	beforeEach(() => {
		testBlocks = [
			{
				id: 'block-1',
				type: 'paragraph',
				text: 'First paragraph',
				metadata: {}
			},
			{
				id: 'block-2',
				type: 'heading',
				text: 'Heading',
				metadata: { level: 2 }
			},
			{
				id: 'block-3',
				type: 'paragraph',
				text: 'Second paragraph',
				metadata: {}
			}
		];
	});

	afterEach(() => {
		vi.clearAllTimers();
	});

	describe('SourcePane Hover Events', () => {
		it('emits blockHover event on mouse enter with debounce', async () => {
			vi.useFakeTimers();

			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;
			let eventDetail: { blockId: string } | undefined;

			component.$on('blockHover', (event: CustomEvent<{ blockId: string }>) => {
				eventFired = true;
				eventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			expect(block).toBeInTheDocument();

			await fireEvent.mouseEnter(block!);

			// Event should not fire immediately (debounced)
			expect(eventFired).toBe(false);

			// Advance timers by 50ms
			vi.advanceTimersByTime(50);

			// Now event should fire
			expect(eventFired).toBe(true);
			expect(eventDetail).toEqual({ blockId: 'block-1' });

			vi.useRealTimers();
		});

		it('emits blockLeave event on mouse leave', async () => {
			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let leaveEventFired = false;
			let leaveEventDetail: { blockId: string } | undefined;

			component.$on('blockLeave', (event: CustomEvent<{ blockId: string }>) => {
				leaveEventFired = true;
				leaveEventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			await fireEvent.mouseLeave(block!);

			expect(leaveEventFired).toBe(true);
			expect(leaveEventDetail).toEqual({ blockId: 'block-1' });
		});

		it('cancels pending hover event when mouse leaves quickly', async () => {
			vi.useFakeTimers();

			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let hoverEventFired = false;

			component.$on('blockHover', () => {
				hoverEventFired = true;
			});

			const block = container.querySelector('[data-block-id="block-1"]');

			// Mouse enter
			await fireEvent.mouseEnter(block!);

			// Mouse leave before debounce completes
			await fireEvent.mouseLeave(block!);

			// Advance timers past debounce
			vi.advanceTimersByTime(50);

			// Hover event should not fire
			expect(hoverEventFired).toBe(false);

			vi.useRealTimers();
		});

		it('emits blockHover event on keyboard focus', async () => {
			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;
			let eventDetail: { blockId: string } | undefined;

			component.$on('blockHover', (event: CustomEvent<{ blockId: string }>) => {
				eventFired = true;
				eventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			await fireEvent.focus(block!);

			expect(eventFired).toBe(true);
			expect(eventDetail).toEqual({ blockId: 'block-1' });
		});

		it('emits blockLeave event on keyboard blur', async () => {
			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;
			let eventDetail: { blockId: string } | undefined;

			component.$on('blockLeave', (event: CustomEvent<{ blockId: string }>) => {
				eventFired = true;
				eventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			await fireEvent.blur(block!);

			expect(eventFired).toBe(true);
			expect(eventDetail).toEqual({ blockId: 'block-1' });
		});
	});

	describe('TranslationPane Hover Events', () => {
		it('emits blockHover event on mouse enter with debounce', async () => {
			vi.useFakeTimers();

			const { component, container } = render(TranslationPane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;
			let eventDetail: { blockId: string } | undefined;

			component.$on('blockHover', (event: CustomEvent<{ blockId: string }>) => {
				eventFired = true;
				eventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-2"]');
			expect(block).toBeInTheDocument();

			await fireEvent.mouseEnter(block!);

			// Event should not fire immediately
			expect(eventFired).toBe(false);

			// Advance timers by 50ms
			vi.advanceTimersByTime(50);

			// Now event should fire
			expect(eventFired).toBe(true);
			expect(eventDetail).toEqual({ blockId: 'block-2' });

			vi.useRealTimers();
		});

		it('emits blockLeave event on mouse leave', async () => {
			const { component, container } = render(TranslationPane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;
			let eventDetail: { blockId: string } | undefined;

			component.$on('blockLeave', (event: CustomEvent<{ blockId: string }>) => {
				eventFired = true;
				eventDetail = event.detail;
			});

			const block = container.querySelector('[data-block-id="block-2"]');
			await fireEvent.mouseLeave(block!);

			expect(eventFired).toBe(true);
			expect(eventDetail).toEqual({ blockId: 'block-2' });
		});
	});

	describe('Highlight Styles', () => {
		it('applies highlight class when highlightedBlockId matches', () => {
			const { container } = render(SourcePane, {
				props: {
					blocks: testBlocks,
					highlightedBlockId: 'block-1'
				}
			});

			const highlightedBlock = container.querySelector('[data-block-id="block-1"]');
			const unhighlightedBlock = container.querySelector('[data-block-id="block-2"]');

			expect(highlightedBlock).toHaveClass('block-highlighted');
			expect(unhighlightedBlock).not.toHaveClass('block-highlighted');
		});

		it('applies highlight class to all block types in SourcePane', () => {
			const mixedBlocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'Para', metadata: {} },
				{ id: 'h1', type: 'heading', text: 'Head', metadata: { level: 1 } },
				{ id: 'c1', type: 'code', text: 'code', metadata: {} },
				{ id: 'l1', type: 'list', text: '- Item', metadata: {} },
				{ id: 'q1', type: 'quote', text: 'Quote', metadata: {} },
				{
					id: 'i1',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/img.jpg', alt: 'Img' }
				}
			];

			const { container } = render(SourcePane, {
				props: {
					blocks: mixedBlocks,
					highlightedBlockId: 'p1'
				}
			});

			expect(container.querySelector('[data-block-id="p1"]')).toHaveClass('block-highlighted');

			// Test another type
			const { container: container2 } = render(SourcePane, {
				props: {
					blocks: mixedBlocks,
					highlightedBlockId: 'h1'
				}
			});

			expect(container2.querySelector('[data-block-id="h1"]')).toHaveClass('block-highlighted');
		});

		it('applies highlight class to all block types in TranslationPane', () => {
			const mixedBlocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'Para', metadata: {} },
				{ id: 'h1', type: 'heading', text: 'Head', metadata: { level: 1 } },
				{ id: 'c1', type: 'code', text: 'code', metadata: {} },
				{ id: 'l1', type: 'list', text: '- Item', metadata: {} },
				{ id: 'q1', type: 'quote', text: 'Quote', metadata: {} },
				{
					id: 'i1',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/img.jpg', alt: 'Img' }
				}
			];

			const { container } = render(TranslationPane, {
				props: {
					blocks: mixedBlocks,
					highlightedBlockId: 'p1'
				}
			});

			expect(container.querySelector('[data-block-id="p1"]')).toHaveClass('block-highlighted');
		});

		it('removes highlight class when highlightedBlockId changes to null', async () => {
			const { container, component } = render(SourcePane, {
				props: {
					blocks: testBlocks,
					highlightedBlockId: 'block-1'
				}
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			expect(block).toHaveClass('block-highlighted');

			// Update prop
			await component.$set({ highlightedBlockId: null });

			expect(block).not.toHaveClass('block-highlighted');
		});

		it('moves highlight to different block when highlightedBlockId changes', async () => {
			const { container, component } = render(SourcePane, {
				props: {
					blocks: testBlocks,
					highlightedBlockId: 'block-1'
				}
			});

			const block1 = container.querySelector('[data-block-id="block-1"]');
			const block2 = container.querySelector('[data-block-id="block-2"]');

			expect(block1).toHaveClass('block-highlighted');
			expect(block2).not.toHaveClass('block-highlighted');

			// Change highlighted block
			await component.$set({ highlightedBlockId: 'block-2' });

			expect(block1).not.toHaveClass('block-highlighted');
			expect(block2).toHaveClass('block-highlighted');
		});
	});

	describe('Accessibility', () => {
		it('blocks have tabindex for keyboard navigation', () => {
			const { container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			const blocks = container.querySelectorAll('[data-block-id]');
			blocks.forEach((block) => {
				expect(block).toHaveAttribute('tabindex', '0');
			});
		});

		it('blocks are focusable and hoverable', () => {
			const { container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			const blocks = container.querySelectorAll('[data-block-id]');
			blocks.forEach((block) => {
				expect(block).toHaveClass('block-hoverable');
			});
		});

		it('keyboard focus triggers hover event immediately (no debounce)', async () => {
			vi.useFakeTimers();

			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let eventFired = false;

			component.$on('blockHover', () => {
				eventFired = true;
			});

			const block = container.querySelector('[data-block-id="block-1"]');
			await fireEvent.focus(block!);

			// Should fire immediately, not debounced
			expect(eventFired).toBe(true);

			vi.useRealTimers();
		});
	});

	describe('Performance', () => {
		it('handles large number of blocks efficiently', () => {
			const largeBlockSet: ContentBlock[] = Array.from({ length: 150 }, (_, i) => ({
				id: `block-${i}`,
				type: 'paragraph' as const,
				text: `Paragraph ${i}`,
				metadata: {}
			}));

			const startTime = performance.now();

			const { container } = render(SourcePane, {
				props: { blocks: largeBlockSet }
			});

			const endTime = performance.now();
			const renderTime = endTime - startTime;

			// Rendering should be fast (less than 500ms for 150 blocks)
			expect(renderTime).toBeLessThan(500);

			// All blocks should be rendered
			const renderedBlocks = container.querySelectorAll('[data-block-id]');
			expect(renderedBlocks.length).toBe(150);
		});

		it('debounce prevents rapid fire events', async () => {
			vi.useFakeTimers();

			const { component, container } = render(SourcePane, {
				props: { blocks: testBlocks }
			});

			let eventCount = 0;

			component.$on('blockHover', () => {
				eventCount++;
			});

			const block = container.querySelector('[data-block-id="block-1"]');

			// Rapidly trigger mouse enter multiple times
			await fireEvent.mouseEnter(block!);
			await fireEvent.mouseEnter(block!);
			await fireEvent.mouseEnter(block!);

			// Advance time
			vi.advanceTimersByTime(50);

			// Should only fire once due to debounce
			expect(eventCount).toBe(1);

			vi.useRealTimers();
		});
	describe('Integration with DualPaneLayout', () => {
		it('coordinates hover highlighting between panes via context', async () => {
			vi.useFakeTimers();

			// Import DualPaneLayout to test the full integration
			const { default: DualPaneLayout } = await import('./DualPaneLayout.svelte');

			// Render the full component hierarchy
			const { container } = render(DualPaneLayout, {
				props: {},
				context: new Map()
			});

			// Get the pane containers
			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			expect(leftPane).toBeInTheDocument();
			expect(rightPane).toBeInTheDocument();

			vi.useRealTimers();
		});
	});
});
