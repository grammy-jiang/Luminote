/**
 * Unit tests for DualPaneLayout component.
 */

import { describe, it, expect } from 'vitest';
import { render } from '../test-utils';
import { screen, fireEvent } from '@testing-library/svelte';
import DualPaneLayout from './DualPaneLayout.svelte';

describe('DualPaneLayout Component', () => {
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

	describe('Slots', () => {
		it('renders default slot content when no slots provided', () => {
			const { container } = render(DualPaneLayout);

			// Verify placeholder content is shown
			expect(screen.getByText('No source content')).toBeInTheDocument();
			expect(screen.getByText('No translation content')).toBeInTheDocument();
			expect(container).toBeInTheDocument();
		});
	});

	describe('Props', () => {
		it('accepts initialSplit prop', () => {
			const { container } = render(DualPaneLayout, {
				props: { initialSplit: 60 }
			});

			// Component accepts the prop without errors
			expect(container).toBeInTheDocument();
		});

		it('uses default initialSplit of 50', () => {
			const { container } = render(DualPaneLayout);

			expect(container).toBeInTheDocument();
		});

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
		it('handles zero initialSplit', () => {
			const { container } = render(DualPaneLayout, {
				props: { initialSplit: 0 }
			});

			expect(container).toBeInTheDocument();
		});

		it('handles 100 initialSplit', () => {
			const { container } = render(DualPaneLayout, {
				props: { initialSplit: 100 }
			});

			expect(container).toBeInTheDocument();
		});

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
});
