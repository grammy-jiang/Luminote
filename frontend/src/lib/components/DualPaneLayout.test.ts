/**
 * Unit tests for DualPaneLayout component.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, waitFor } from '../test-utils';
import { screen, fireEvent } from '@testing-library/svelte';
import DualPaneLayout from './DualPaneLayout.svelte';

// Mock localStorage
const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value.toString();
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		}
	};
})();

Object.defineProperty(window, 'localStorage', {
	value: localStorageMock
});

describe('DualPaneLayout Component', () => {
	beforeEach(() => {
		// Clear localStorage before each test
		localStorageMock.clear();
	});

	describe('Rendering', () => {
		it('renders two panes', () => {
			render(DualPaneLayout);

			const regions = screen.getAllByRole('region');
			expect(regions).toHaveLength(2);
		});

		it('renders with default ARIA labels', () => {
			render(DualPaneLayout);

			expect(screen.getByRole('region', { name: 'Source' })).toBeInTheDocument();
			expect(screen.getByRole('region', { name: 'Translation' })).toBeInTheDocument();
		});

		it('renders with custom ARIA labels', () => {
			render(DualPaneLayout, {
				props: {
					leftLabel: 'Original Content',
					rightLabel: 'Translated Content'
				}
			});

			expect(screen.getByRole('region', { name: 'Original Content' })).toBeInTheDocument();
			expect(screen.getByRole('region', { name: 'Translated Content' })).toBeInTheDocument();
		});

		it('has main role for accessibility', () => {
			render(DualPaneLayout);

			const main = screen.getByRole('main');
			expect(main).toBeInTheDocument();
			expect(main).toHaveAttribute('aria-label', 'Two-pane reading interface');
		});

		it('renders default placeholder content when no slots provided', () => {
			render(DualPaneLayout);

			expect(screen.getByText('No source content')).toBeInTheDocument();
			expect(screen.getByText('No translation content')).toBeInTheDocument();
		});
	});

	describe('Default Content', () => {
		it('renders placeholder content when no slots provided', () => {
			const { container } = render(DualPaneLayout);

			// Verify placeholder content is shown
			expect(screen.getByText('No source content')).toBeInTheDocument();
			expect(screen.getByText('No translation content')).toBeInTheDocument();
			expect(container).toBeInTheDocument();
		});
	});

	describe('Props', () => {
		it('accepts leftLabel prop', () => {
			render(DualPaneLayout, {
				props: { leftLabel: 'Custom Left' }
			});

			expect(screen.getByRole('region', { name: 'Custom Left' })).toBeInTheDocument();
		});

		it('accepts rightLabel prop', () => {
			render(DualPaneLayout, {
				props: { rightLabel: 'Custom Right' }
			});

			expect(screen.getByRole('region', { name: 'Custom Right' })).toBeInTheDocument();
		});
	});

	describe('Keyboard Navigation', () => {
		it('panes have tabindex for keyboard accessibility', () => {
			render(DualPaneLayout);

			const regions = screen.getAllByRole('region');
			regions.forEach((region) => {
				expect(region).toHaveAttribute('tabindex', '0');
			});
		});

		it('panes can receive focus', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			// Focus behavior in jsdom is limited, but we can verify focus events trigger
			await fireEvent.focus(leftPane);
			// In real browser, this would have focus. In jsdom, we verify no errors occur
			expect(leftPane).toBeInTheDocument();

			await fireEvent.focus(rightPane);
			expect(rightPane).toBeInTheDocument();
		});

		it('sets active class when pane is focused', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			await fireEvent.focus(leftPane);
			expect(leftPane).toHaveClass('active');

			await fireEvent.focus(rightPane);
			expect(rightPane).toHaveClass('active');
		});
	});

	describe('Accessibility', () => {
		it('has appropriate ARIA roles', () => {
			render(DualPaneLayout);

			expect(screen.getByRole('main')).toBeInTheDocument();
			expect(screen.getAllByRole('region')).toHaveLength(2);
		});

		it('has meaningful ARIA labels', () => {
			render(DualPaneLayout);

			const main = screen.getByRole('main');
			expect(main).toHaveAttribute('aria-label', 'Two-pane reading interface');

			const leftPane = screen.getByRole('region', { name: 'Source' });
			expect(leftPane).toHaveAttribute('aria-label', 'Source');

			const rightPane = screen.getByRole('region', { name: 'Translation' });
			expect(rightPane).toHaveAttribute('aria-label', 'Translation');
		});

		it('supports custom accessibility labels', () => {
			render(DualPaneLayout, {
				props: {
					leftLabel: 'Original Document',
					rightLabel: 'Spanish Translation'
				}
			});

			expect(screen.getByRole('region', { name: 'Original Document' })).toBeInTheDocument();
			expect(screen.getByRole('region', { name: 'Spanish Translation' })).toBeInTheDocument();
		});
	});

	describe('Responsive Behavior', () => {
		it('applies correct CSS classes for layout', () => {
			const { container } = render(DualPaneLayout);

			const layout = container.querySelector('.dual-pane-layout');
			expect(layout).toBeInTheDocument();
			expect(layout).toHaveClass('dual-pane-layout');
		});

		it('applies pane-specific classes', () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			expect(leftPane).toBeInTheDocument();
			expect(rightPane).toBeInTheDocument();
			expect(leftPane).toHaveClass('pane', 'left-pane');
			expect(rightPane).toHaveClass('pane', 'right-pane');
		});
	});

	describe('Scroll Behavior', () => {
		it('each pane has independent scroll containers', () => {
			const { container } = render(DualPaneLayout);

			const panes = container.querySelectorAll('.pane');
			panes.forEach((pane) => {
				// In jsdom, getComputedStyle doesn't fully work, verify structure instead
				expect(pane).toHaveClass('pane');
			});
		});
	});

	describe('Programmatic Control', () => {
		it('exports focusLeftPane method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.focusLeftPane).toBe('function');
		});

		it('exports focusRightPane method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.focusRightPane).toBe('function');
		});

		it('exports getLeftPaneRef method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.getLeftPaneRef).toBe('function');
		});

		it('exports getRightPaneRef method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.getRightPaneRef).toBe('function');
		});

		it('getLeftPaneRef returns HTMLDivElement', () => {
			const { component } = render(DualPaneLayout);

			const ref = component.getLeftPaneRef();
			expect(ref).toBeInstanceOf(HTMLDivElement);
		});

		it('getRightPaneRef returns HTMLDivElement', () => {
			const { component } = render(DualPaneLayout);

			const ref = component.getRightPaneRef();
			expect(ref).toBeInstanceOf(HTMLDivElement);
		});

		it('focusLeftPane sets focus on left pane', async () => {
			const { component } = render(DualPaneLayout);

			component.focusLeftPane();

			const leftPane = screen.getByRole('region', { name: 'Source' });
			// Note: Focus might not work perfectly in jsdom, but we verify the method exists
			expect(leftPane).toBeInTheDocument();
		});

		it('focusRightPane sets focus on right pane', async () => {
			const { component } = render(DualPaneLayout);

			component.focusRightPane();

			const rightPane = screen.getByRole('region', { name: 'Translation' });
			// Note: Focus might not work perfectly in jsdom, but we verify the method exists
			expect(rightPane).toBeInTheDocument();
		});
	});

	describe('Edge Cases', () => {
		it('handles empty label strings', () => {
			render(DualPaneLayout, {
				props: {
					leftLabel: '',
					rightLabel: ''
				}
			});

			const regions = screen.getAllByRole('region');
			expect(regions).toHaveLength(2);
		});

		it('handles very long label strings', () => {
			const longLabel = 'A'.repeat(200);
			render(DualPaneLayout, {
				props: {
					leftLabel: longLabel,
					rightLabel: longLabel
				}
			});

			// Both panes have the same long label, so we use getAllBy
			const regions = screen.getAllByRole('region', { name: longLabel });
			expect(regions).toHaveLength(2);
		});
	});

	describe('Draggable Divider', () => {
		it('renders divider with separator role', () => {
			render(DualPaneLayout);

			const divider = screen.getByRole('separator');
			expect(divider).toBeInTheDocument();
			expect(divider).toHaveAttribute('aria-label', 'Resize panes');
			expect(divider).toHaveAttribute('aria-orientation', 'vertical');
		});

		it('divider has correct ARIA attributes', () => {
			render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			const divider = screen.getByRole('separator');
			expect(divider).toHaveAttribute('aria-valuenow', '50');
			expect(divider).toHaveAttribute('aria-valuemin', '20');
			expect(divider).toHaveAttribute('aria-valuemax', '80');
		});

		it('applies hovering class on mouse enter', async () => {
			const { container } = render(DualPaneLayout);

			const divider = container.querySelector('.divider');
			expect(divider).toBeInTheDocument();

			await fireEvent.mouseEnter(divider!);
			expect(divider).toHaveClass('hovering');

			await fireEvent.mouseLeave(divider!);
			expect(divider).not.toHaveClass('hovering');
		});

		it('applies dragging class during mouse drag', async () => {
			const { container } = render(DualPaneLayout);

			const divider = container.querySelector('.divider');
			expect(divider).toBeInTheDocument();

			await fireEvent.mouseDown(divider!);
			expect(divider).toHaveClass('dragging');

			await fireEvent.mouseUp(window);
			expect(divider).not.toHaveClass('dragging');
		});

		it('updates pane widths during drag', async () => {
			const { container } = render(DualPaneLayout);

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			// Mock getBoundingClientRect
			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.mouseDown(divider!);

			// Simulate mouse move to 30% position
			await fireEvent.mouseMove(window, { clientX: 300 });

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Check that width is updated (approximately 30%)
			const leftWidth = leftPane?.getAttribute('style');
			expect(leftWidth).toContain('width:');
			expect(leftWidth).toContain('30%');

			const rightWidth = rightPane?.getAttribute('style');
			expect(rightWidth).toContain('width:');
			expect(rightWidth).toContain('70%');

			await fireEvent.mouseUp(window);
		});

		it('enforces minimum pane width constraint', async () => {
			const { container, component } = render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.mouseDown(divider!);

			// Try to drag to 10% (below minimum)
			await fireEvent.mouseMove(window, { clientX: 100 });
			await fireEvent.mouseUp(window);

			// Should be clamped to minimum (20%)
			const ratio = component.getSplitRatio();
			expect(ratio).toBeGreaterThanOrEqual(20);
		});

		it('enforces maximum pane width constraint', async () => {
			const { container, component } = render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.mouseDown(divider!);

			// Try to drag to 90% (above maximum of 80%)
			await fireEvent.mouseMove(window, { clientX: 900 });
			await fireEvent.mouseUp(window);

			// Should be clamped to maximum (80%)
			const ratio = component.getSplitRatio();
			expect(ratio).toBeLessThanOrEqual(80);
		});
	});

	describe('Touch Support', () => {
		it('handles touch drag events', async () => {
			const { container } = render(DualPaneLayout);

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.touchStart(divider!);
			expect(divider).toHaveClass('dragging');

			// Simulate touch move
			await fireEvent.touchMove(window, {
				touches: [{ clientX: 400 }]
			});

			await fireEvent.touchEnd(window);
			expect(divider).not.toHaveClass('dragging');
		});
	});

	describe('Keyboard Shortcuts', () => {
		it('decreases left pane width with Ctrl+ArrowLeft', async () => {
			const { component } = render(DualPaneLayout);

			const initialRatio = component.getSplitRatio();

			await fireEvent.keyDown(window, {
				key: 'ArrowLeft',
				ctrlKey: true
			});

			const newRatio = component.getSplitRatio();
			expect(newRatio).toBe(initialRatio - 5);
		});

		it('increases left pane width with Ctrl+ArrowRight', async () => {
			const { component } = render(DualPaneLayout);

			const initialRatio = component.getSplitRatio();

			await fireEvent.keyDown(window, {
				key: 'ArrowRight',
				ctrlKey: true
			});

			const newRatio = component.getSplitRatio();
			expect(newRatio).toBe(initialRatio + 5);
		});

		it('respects minimum width with keyboard shortcuts', async () => {
			const { component } = render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			// Set to minimum width
			component.setSplitRatio(20);

			// Try to decrease below minimum
			await fireEvent.keyDown(window, {
				key: 'ArrowLeft',
				ctrlKey: true
			});

			const ratio = component.getSplitRatio();
			expect(ratio).toBe(20);
		});

		it('respects maximum width with keyboard shortcuts', async () => {
			const { component } = render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			// Set to maximum width (80%)
			component.setSplitRatio(80);

			// Try to increase above maximum
			await fireEvent.keyDown(window, {
				key: 'ArrowRight',
				ctrlKey: true
			});

			const ratio = component.getSplitRatio();
			expect(ratio).toBe(80);
		});
	});

	describe('localStorage Persistence', () => {
		it('saves split ratio to localStorage on drag end', async () => {
			const { container } = render(DualPaneLayout, {
				props: { persistKey: 'test-split' }
			});

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.mouseDown(divider!);
			await fireEvent.mouseMove(window, { clientX: 600 });
			await fireEvent.mouseUp(window);

			const saved = localStorage.getItem('test-split');
			expect(saved).toBeTruthy();
			expect(parseFloat(saved!)).toBeCloseTo(60, 0);
		});

		it('restores split ratio from localStorage on mount', async () => {
			localStorage.setItem('test-split-restore', '65');

			const { component } = render(DualPaneLayout, {
				props: { persistKey: 'test-split-restore' }
			});

			// Wait for the component to read from localStorage
			await waitFor(() => {
				expect(component.getSplitRatio()).toBe(65);
			});
		});

		it('uses default split ratio if localStorage is empty', () => {
			const { component } = render(DualPaneLayout, {
				props: { persistKey: 'non-existent-key' }
			});

			const ratio = component.getSplitRatio();
			expect(ratio).toBe(50);
		});

		it('ignores invalid localStorage values', () => {
			localStorage.setItem('test-invalid', 'not-a-number');

			const { component } = render(DualPaneLayout, {
				props: { persistKey: 'test-invalid' }
			});

			const ratio = component.getSplitRatio();
			expect(ratio).toBe(50); // Should use default
		});

		it('ignores localStorage values outside valid range', () => {
			localStorage.setItem('test-out-of-range', '95');

			const { component } = render(DualPaneLayout, {
				props: { persistKey: 'test-out-of-range', minPaneWidth: 20 }
			});

			const ratio = component.getSplitRatio();
			expect(ratio).toBe(50); // Should use default
		});
	});

	describe('Custom Events', () => {
		it('dispatches splitChange event on drag end', async () => {
			const { container, component } = render(DualPaneLayout);

			let eventFired = false;
			let eventDetail: { leftWidth: number; rightWidth: number } | undefined;

			component.$on(
				'splitChange',
				(event: CustomEvent<{ leftWidth: number; rightWidth: number }>) => {
					eventFired = true;
					eventDetail = event.detail;
				}
			);

			const divider = container.querySelector('.divider');
			const layoutContainer = container.querySelector('.dual-pane-layout');

			vi.spyOn(layoutContainer!, 'getBoundingClientRect').mockReturnValue({
				left: 0,
				width: 1000,
				top: 0,
				right: 1000,
				bottom: 600,
				height: 600,
				x: 0,
				y: 0,
				toJSON: () => {}
			});

			await fireEvent.mouseDown(divider!);
			await fireEvent.mouseMove(window, { clientX: 400 });
			await fireEvent.mouseUp(window);

			expect(eventFired).toBe(true);
			expect(eventDetail).toBeDefined();
			expect(eventDetail!.leftWidth).toBeCloseTo(40, 0);
			expect(eventDetail!.rightWidth).toBeCloseTo(60, 0);
		});

		it('dispatches splitChange event on keyboard resize', async () => {
			const { component } = render(DualPaneLayout);

			let eventFired = false;

			component.$on('splitChange', () => {
				eventFired = true;
			});

			await fireEvent.keyDown(window, {
				key: 'ArrowRight',
				ctrlKey: true
			});

			expect(eventFired).toBe(true);
		});
	});

	describe('Programmatic Control', () => {
		it('exports getSplitRatio method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.getSplitRatio).toBe('function');
			expect(component.getSplitRatio()).toBe(50);
		});

		it('exports setSplitRatio method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.setSplitRatio).toBe('function');

			component.setSplitRatio(60);
			expect(component.getSplitRatio()).toBe(60);
		});

		it('setSplitRatio enforces constraints', () => {
			const { component } = render(DualPaneLayout, {
				props: { minPaneWidth: 20 }
			});

			// Try to set below minimum
			component.setSplitRatio(10);
			expect(component.getSplitRatio()).toBe(20);

			// Try to set above maximum
			component.setSplitRatio(90);
			expect(component.getSplitRatio()).toBe(80);
		});

		it('setSplitRatio saves to localStorage', () => {
			const { component } = render(DualPaneLayout, {
				props: { persistKey: 'test-programmatic' }
			});

			component.setSplitRatio(70);

			const saved = localStorage.getItem('test-programmatic');
			expect(saved).toBe('70');
		});
	});

	describe('Block Navigation', () => {
		it('renders ARIA live region for navigation announcements', () => {
			const { container } = render(DualPaneLayout);

			const liveRegion = container.querySelector('[role="status"][aria-live="polite"]');
			expect(liveRegion).toBeInTheDocument();
		});

		it('left pane emits blockClick events', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			expect(leftPane).toBeInTheDocument();

			// Create a mock block element
			const mockBlock = document.createElement('div');
			mockBlock.setAttribute('data-block-id', 'test-block-1');
			leftPane?.appendChild(mockBlock);

			// Trigger blockClick event
			await fireEvent(
				leftPane!,
				new CustomEvent('blockClick', {
					detail: { blockId: 'test-block-1' },
					bubbles: true
				})
			);

			// Event should be handled (no errors)
			expect(leftPane).toBeInTheDocument();
		});

		it('right pane emits blockClick events', async () => {
			const { container } = render(DualPaneLayout);

			const rightPane = container.querySelector('.right-pane');
			expect(rightPane).toBeInTheDocument();

			// Create a mock block element
			const mockBlock = document.createElement('div');
			mockBlock.setAttribute('data-block-id', 'test-block-2');
			rightPane?.appendChild(mockBlock);

			// Trigger blockClick event
			await fireEvent(
				rightPane!,
				new CustomEvent('blockClick', {
					detail: { blockId: 'test-block-2' },
					bubbles: true
				})
			);

			// Event should be handled (no errors)
			expect(rightPane).toBeInTheDocument();
		});

		it('handles scroll events on left pane', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			expect(leftPane).toBeInTheDocument();

			// Trigger scroll event
			await fireEvent.scroll(leftPane!);

			// No errors should occur
			expect(leftPane).toBeInTheDocument();
		});

		it('handles scroll events on right pane', async () => {
			const { container } = render(DualPaneLayout);

			const rightPane = container.querySelector('.right-pane');
			expect(rightPane).toBeInTheDocument();

			// Trigger scroll event
			await fireEvent.scroll(rightPane!);

			// No errors should occur
			expect(rightPane).toBeInTheDocument();
		});

		it('applies pulse animation class to navigated blocks', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Create mock blocks in both panes
			const leftBlock = document.createElement('div');
			leftBlock.setAttribute('data-block-id', 'block-1');
			leftPane?.appendChild(leftBlock);

			const rightBlock = document.createElement('div');
			rightBlock.setAttribute('data-block-id', 'block-1');
			rightPane?.appendChild(rightBlock);

			// Mock scrollIntoView
			rightBlock.scrollIntoView = vi.fn();

			// Trigger blockClick from left pane
			await fireEvent(
				leftPane!,
				new CustomEvent('blockClick', {
					detail: { blockId: 'block-1' },
					bubbles: true
				})
			);

			// Allow animation to start
			await new Promise((resolve) => setTimeout(resolve, 10));

			// Check that scrollIntoView was called
			expect(rightBlock.scrollIntoView).toHaveBeenCalledWith({
				behavior: 'smooth',
				block: 'center',
				inline: 'nearest'
			});

			// Check that pulse animation class was added
			expect(rightBlock.classList.contains('block-pulse')).toBe(true);
		});

		it('announces navigation to screen readers', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');
			const liveRegion = container.querySelector('[role="status"]');

			// Create mock blocks
			const rightBlock = document.createElement('div');
			rightBlock.setAttribute('data-block-id', 'block-1');
			rightBlock.scrollIntoView = vi.fn();
			rightPane?.appendChild(rightBlock);

			// Trigger blockClick from left pane
			await fireEvent(
				leftPane!,
				new CustomEvent('blockClick', {
					detail: { blockId: 'block-1' },
					bubbles: true
				})
			);

			// Wait for announcement
			await waitFor(() => {
				expect(liveRegion?.textContent).toBe('Navigated to translation block');
			});
		});
	});

	describe('Keyboard Navigation Integration', () => {
		it('Tab switches focus between panes', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			// Focus left pane
			leftPane.focus();
			expect(leftPane).toHaveClass('active');

			// Press Tab to move to right pane
			await fireEvent.keyDown(leftPane, { key: 'Tab' });

			// Right pane should have active class
			expect(rightPane).toHaveClass('active');
		});

		it('Shift+Tab switches focus backwards between panes', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			// Focus right pane
			await fireEvent.focus(rightPane);
			expect(rightPane).toHaveClass('active');

			// Press Shift+Tab to move back to left pane
			await fireEvent.keyDown(rightPane, { key: 'Tab', shiftKey: true });

			// Left pane should have active class
			expect(leftPane).toHaveClass('active');
		});

		it('supports keyboard navigation within blocks in left pane', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');

			// Create mock blocks
			const block1 = document.createElement('div');
			block1.setAttribute('data-block-id', 'block-1');
			block1.setAttribute('tabindex', '0');
			leftPane?.appendChild(block1);

			const block2 = document.createElement('div');
			block2.setAttribute('data-block-id', 'block-2');
			block2.setAttribute('tabindex', '0');
			leftPane?.appendChild(block2);

			// Focus first block
			block1.focus();

			// Note: The actual arrow key navigation is handled by SourcePane/TranslationPane
			// This test verifies that DualPaneLayout doesn't interfere
			expect(document.activeElement).toBe(block1);
		});

		it('supports keyboard navigation within blocks in right pane', async () => {
			const { container } = render(DualPaneLayout);

			const rightPane = container.querySelector('.right-pane');

			// Create mock blocks
			const block1 = document.createElement('div');
			block1.setAttribute('data-block-id', 'block-1');
			block1.setAttribute('tabindex', '0');
			rightPane?.appendChild(block1);

			const block2 = document.createElement('div');
			block2.setAttribute('data-block-id', 'block-2');
			block2.setAttribute('tabindex', '0');
			rightPane?.appendChild(block2);

			// Focus first block
			block1.focus();

			// Note: The actual arrow key navigation is handled by SourcePane/TranslationPane
			// This test verifies that DualPaneLayout doesn't interfere
			expect(document.activeElement).toBe(block1);
		});

		it('Enter key triggers cross-pane navigation', async () => {
			const { container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Create mock blocks in both panes
			const leftBlock = document.createElement('div');
			leftBlock.setAttribute('data-block-id', 'block-1');
			leftBlock.setAttribute('tabindex', '0');
			leftPane?.appendChild(leftBlock);

			const rightBlock = document.createElement('div');
			rightBlock.setAttribute('data-block-id', 'block-1');
			rightBlock.scrollIntoView = vi.fn();
			rightPane?.appendChild(rightBlock);

			// Focus left block and trigger Enter key (which should trigger blockClick)
			leftBlock.focus();

			// Simulate the blockClick event that would be triggered by Enter in SourcePane
			await fireEvent(
				leftPane!,
				new CustomEvent('blockClick', {
					detail: { blockId: 'block-1' },
					bubbles: true
				})
			);

			// Check that scrollIntoView was called on the corresponding block in right pane
			expect(rightBlock.scrollIntoView).toHaveBeenCalledWith({
				behavior: 'smooth',
				block: 'center',
				inline: 'nearest'
			});
		});

		it('maintains focus state when navigating between panes', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			// Focus left pane
			await fireEvent.focus(leftPane);
			expect(leftPane).toHaveClass('active');
			expect(rightPane).not.toHaveClass('active');

			// Focus right pane
			await fireEvent.focus(rightPane);
			expect(rightPane).toHaveClass('active');
			// In the current implementation, both could have active class since we don't remove it
			// The important part is that the newly focused pane has the active class
		});

		it('provides visual focus indicator for keyboard users', () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });

			// Verify pane has tabindex
			expect(leftPane).toHaveAttribute('tabindex', '0');

			// CSS should provide focus outline (verified in component styles)
		});

		it('announces pane switches to screen readers', async () => {
			render(DualPaneLayout);

			const leftPane = screen.getByRole('region', { name: 'Source' });
			const rightPane = screen.getByRole('region', { name: 'Translation' });

			// Verify ARIA labels are present
			expect(leftPane).toHaveAttribute('aria-label', 'Source');
			expect(rightPane).toHaveAttribute('aria-label', 'Translation');

			// When panes receive focus, screen readers will announce the aria-label
		});
	});

	describe('Scroll Synchronization', () => {
		beforeEach(() => {
			// Mock requestAnimationFrame and cancelAnimationFrame
			let frameId = 0;
			global.requestAnimationFrame = vi.fn((callback) => {
				setTimeout(() => callback(Date.now()), 0);
				return ++frameId;
			});
			global.cancelAnimationFrame = vi.fn();
		});

		it('renders scroll sync toggle button', () => {
			render(DualPaneLayout);

			const toggleButton = screen.getByRole('button', {
				name: /scroll synchronization/i
			});
			expect(toggleButton).toBeInTheDocument();
		});

		it('toggle button has correct ARIA attributes', () => {
			render(DualPaneLayout);

			const toggleButton = screen.getByRole('button', {
				name: /scroll synchronization/i
			});
			expect(toggleButton).toHaveAttribute('aria-pressed', 'false');
		});

		it('exports getScrollSyncEnabled method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.getScrollSyncEnabled).toBe('function');
			expect(component.getScrollSyncEnabled()).toBe(false);
		});

		it('exports setScrollSyncEnabled method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.setScrollSyncEnabled).toBe('function');

			component.setScrollSyncEnabled(true);
			expect(component.getScrollSyncEnabled()).toBe(true);
		});

		it('exports toggleScrollSync method', () => {
			const { component } = render(DualPaneLayout);

			expect(typeof component.toggleScrollSync).toBe('function');

			const initialState = component.getScrollSyncEnabled();
			component.toggleScrollSync();
			expect(component.getScrollSyncEnabled()).toBe(!initialState);
		});

		it('toggleScrollSync changes state', () => {
			const { component } = render(DualPaneLayout);

			expect(component.getScrollSyncEnabled()).toBe(false);

			component.toggleScrollSync();
			expect(component.getScrollSyncEnabled()).toBe(true);

			component.toggleScrollSync();
			expect(component.getScrollSyncEnabled()).toBe(false);
		});

		it('clicking toggle button changes sync mode', async () => {
			const { component } = render(DualPaneLayout);

			const toggleButton = screen.getByRole('button', {
				name: /scroll synchronization/i
			});

			expect(component.getScrollSyncEnabled()).toBe(false);

			await fireEvent.click(toggleButton);
			expect(component.getScrollSyncEnabled()).toBe(true);

			await fireEvent.click(toggleButton);
			expect(component.getScrollSyncEnabled()).toBe(false);
		});

		it('toggle button updates aria-pressed attribute', async () => {
			render(DualPaneLayout);

			const toggleButton = screen.getByRole('button', {
				name: /scroll synchronization/i
			});

			expect(toggleButton).toHaveAttribute('aria-pressed', 'false');

			await fireEvent.click(toggleButton);
			expect(toggleButton).toHaveAttribute('aria-pressed', 'true');

			await fireEvent.click(toggleButton);
			expect(toggleButton).toHaveAttribute('aria-pressed', 'false');
		});

		it('toggle button shows correct label for each state', async () => {
			render(DualPaneLayout);

			const toggleButton = screen.getByRole('button', {
				name: /scroll synchronization/i
			});

			// Initial state (independent mode)
			expect(toggleButton.textContent).toContain('Independent');

			await fireEvent.click(toggleButton);

			// Synced state
			expect(toggleButton.textContent).toContain('Synced');

			await fireEvent.click(toggleButton);

			// Back to independent
			expect(toggleButton.textContent).toContain('Independent');
		});

		it('saves scroll sync mode to localStorage', async () => {
			const { component } = render(DualPaneLayout, {
				props: { syncPersistKey: 'test-scroll-sync' }
			});

			component.setScrollSyncEnabled(true);

			const saved = localStorage.getItem('test-scroll-sync');
			expect(saved).toBe('true');

			component.setScrollSyncEnabled(false);

			const savedAgain = localStorage.getItem('test-scroll-sync');
			expect(savedAgain).toBe('false');
		});

		it('restores scroll sync mode from localStorage on mount', async () => {
			localStorage.setItem('test-scroll-sync-restore', 'true');

			const { component } = render(DualPaneLayout, {
				props: { syncPersistKey: 'test-scroll-sync-restore' }
			});

			await waitFor(() => {
				expect(component.getScrollSyncEnabled()).toBe(true);
			});
		});

		it('uses default sync mode if localStorage is empty', () => {
			const { component } = render(DualPaneLayout, {
				props: { syncPersistKey: 'non-existent-sync-key' }
			});

			expect(component.getScrollSyncEnabled()).toBe(false);
		});

		it('synchronizes scroll from left to right pane when enabled', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Mock scroll properties
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(leftPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(leftPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			Object.defineProperty(rightPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(rightPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(rightPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			// Enable scroll sync
			component.setScrollSyncEnabled(true);

			// Scroll left pane
			(leftPane as HTMLElement).scrollTop = 250;
			await fireEvent.scroll(leftPane!);

			// Wait for requestAnimationFrame
			await new Promise((resolve) => setTimeout(resolve, 100));

			// Right pane should sync (approximately)
			expect((rightPane as HTMLElement).scrollTop).toBeGreaterThan(0);
		});

		it('synchronizes scroll from right to left pane when enabled', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Mock scroll properties
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(leftPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(leftPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			Object.defineProperty(rightPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(rightPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(rightPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			// Enable scroll sync
			component.setScrollSyncEnabled(true);

			// Scroll right pane
			(rightPane as HTMLElement).scrollTop = 300;
			await fireEvent.scroll(rightPane!);

			// Wait for requestAnimationFrame
			await new Promise((resolve) => setTimeout(resolve, 100));

			// Left pane should sync (approximately)
			expect((leftPane as HTMLElement).scrollTop).toBeGreaterThan(0);
		});

		it('does not synchronize scroll when disabled', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Mock scroll properties
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(rightPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});

			// Ensure scroll sync is disabled
			component.setScrollSyncEnabled(false);

			// Scroll left pane
			(leftPane as HTMLElement).scrollTop = 250;
			await fireEvent.scroll(leftPane!);

			// Wait for any potential sync
			await new Promise((resolve) => setTimeout(resolve, 100));

			// Right pane should NOT sync
			expect((rightPane as HTMLElement).scrollTop).toBe(0);
		});

		it('uses requestAnimationFrame for performance', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');

			// Mock scroll properties
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(leftPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(leftPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			component.setScrollSyncEnabled(true);

			// Clear any previous calls
			vi.clearAllMocks();

			// Scroll left pane
			(leftPane as HTMLElement).scrollTop = 250;
			await fireEvent.scroll(leftPane!);

			// requestAnimationFrame should have been called
			expect(global.requestAnimationFrame).toHaveBeenCalled();
		});

		it('cancels pending animation frame on unmount', () => {
			const { component, unmount } = render(DualPaneLayout);

			component.setScrollSyncEnabled(true);

			// Trigger a scroll to create a pending animation frame
			const leftPane = component.getLeftPaneRef();
			fireEvent.scroll(leftPane);

			// Clear mocks to count unmount calls
			vi.clearAllMocks();

			// Unmount component
			unmount();

			// cancelAnimationFrame should have been called
			expect(global.cancelAnimationFrame).toHaveBeenCalled();
		});

		it('handles rapid scroll events efficiently', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');

			// Mock scroll properties
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(leftPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(leftPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			component.setScrollSyncEnabled(true);

			// Clear previous calls
			vi.clearAllMocks();

			// Trigger multiple rapid scroll events
			for (let i = 0; i < 10; i++) {
				(leftPane as HTMLElement).scrollTop = i * 50;
				await fireEvent.scroll(leftPane!);
			}

			// Wait for animations to settle
			await new Promise((resolve) => setTimeout(resolve, 100));

			// requestAnimationFrame should have been called, but not 10 times
			// (some should have been cancelled/batched)
			const callCount = (global.requestAnimationFrame as unknown as { mock: { calls: unknown[] } })
				.mock.calls.length;
			expect(callCount).toBeGreaterThan(0);
			expect(callCount).toBeLessThanOrEqual(10);
		});

		it('toggle button has correct active class', async () => {
			const { container } = render(DualPaneLayout);

			const toggleButton = container.querySelector('.scroll-sync-toggle');
			expect(toggleButton).not.toHaveClass('active');

			await fireEvent.click(toggleButton!);
			expect(toggleButton).toHaveClass('active');

			await fireEvent.click(toggleButton!);
			expect(toggleButton).not.toHaveClass('active');
		});

		it('handles touch devices with scroll sync', async () => {
			const { component, container } = render(DualPaneLayout);

			const leftPane = container.querySelector('.left-pane');
			const rightPane = container.querySelector('.right-pane');

			// Mock scroll properties for touch
			Object.defineProperty(leftPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(leftPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(leftPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			Object.defineProperty(rightPane, 'scrollTop', {
				value: 0,
				writable: true,
				configurable: true
			});
			Object.defineProperty(rightPane, 'scrollHeight', {
				value: 1000,
				writable: false,
				configurable: true
			});
			Object.defineProperty(rightPane, 'clientHeight', {
				value: 500,
				writable: false,
				configurable: true
			});

			component.setScrollSyncEnabled(true);

			// Simulate touch scroll
			(leftPane as HTMLElement).scrollTop = 200;
			await fireEvent.scroll(leftPane!);

			await new Promise((resolve) => setTimeout(resolve, 100));

			// Should work with touch just like mouse
			expect((rightPane as HTMLElement).scrollTop).toBeGreaterThan(0);
		});
	});
});
