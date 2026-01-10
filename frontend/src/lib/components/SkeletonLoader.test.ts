/**
 * Unit tests for SkeletonLoader component.
 */

import { describe, it, expect } from 'vitest';
import { render } from '../test-utils';
import { screen } from '@testing-library/svelte';
import SkeletonLoader from './SkeletonLoader.svelte';

describe('SkeletonLoader Component', () => {
	describe('Rendering', () => {
		it('renders with default props', () => {
			render(SkeletonLoader);

			const loader = screen.getByRole('status');
			expect(loader).toBeInTheDocument();
		});

		it('renders default 5 skeleton blocks', () => {
			const { container } = render(SkeletonLoader);

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(5);
		});

		it('renders custom number of skeleton blocks', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 8 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(8);
		});

		it('renders single skeleton block', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 1 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(1);
		});

		it('renders light variant by default', () => {
			const { container } = render(SkeletonLoader);

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toHaveClass('light');
			expect(loader).not.toHaveClass('dark');
		});

		it('renders dark variant when specified', () => {
			const { container } = render(SkeletonLoader, {
				props: { variant: 'dark' }
			});

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toHaveClass('dark');
			expect(loader).not.toHaveClass('light');
		});

		it('renders light variant when explicitly specified', () => {
			const { container } = render(SkeletonLoader, {
				props: { variant: 'light' }
			});

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toHaveClass('light');
			expect(loader).not.toHaveClass('dark');
		});
	});

	describe('Varying Block Heights', () => {
		it('applies different heights to skeleton blocks', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 5 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			const heights = Array.from(blocks).map((block) => {
				const style = (block as HTMLElement).getAttribute('style');
				return style;
			});

			// Check that blocks have varying heights
			expect(heights[0]).toContain('height: 80px');
			expect(heights[1]).toContain('height: 120px');
			expect(heights[2]).toContain('height: 100px');
			expect(heights[3]).toContain('height: 140px');
			expect(heights[4]).toContain('height: 90px');
		});

		it('cycles through heights for more blocks', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 7 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');

			// Check that heights cycle
			expect((blocks[5] as HTMLElement).getAttribute('style')).toContain('height: 80px'); // Same as block 0
			expect((blocks[6] as HTMLElement).getAttribute('style')).toContain('height: 120px'); // Same as block 1
		});
	});

	describe('Accessibility', () => {
		it('has status role for screen readers', () => {
			render(SkeletonLoader);

			const loader = screen.getByRole('status');
			expect(loader).toBeInTheDocument();
		});

		it('has aria-live="polite" attribute', () => {
			render(SkeletonLoader);

			const loader = screen.getByRole('status');
			expect(loader).toHaveAttribute('aria-live', 'polite');
		});

		it('has aria-busy="true" attribute', () => {
			render(SkeletonLoader);

			const loader = screen.getByRole('status');
			expect(loader).toHaveAttribute('aria-busy', 'true');
		});

		it('has aria-label describing loading state', () => {
			render(SkeletonLoader);

			const loader = screen.getByRole('status');
			expect(loader).toHaveAttribute('aria-label', 'Loading content');
		});

		it('has screen reader only text', () => {
			const { container } = render(SkeletonLoader);

			const srText = container.querySelector('.sr-only');
			expect(srText).toBeInTheDocument();
			expect(srText).toHaveTextContent('Loading content, please wait...');
		});

		it('skeleton blocks are hidden from screen readers', () => {
			const { container } = render(SkeletonLoader);

			const blocks = container.querySelectorAll('.skeleton-block');
			blocks.forEach((block) => {
				expect(block).toHaveAttribute('aria-hidden', 'true');
			});
		});

		it('is not focusable by default', () => {
			const { container } = render(SkeletonLoader);

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).not.toHaveAttribute('tabindex');

			const blocks = container.querySelectorAll('.skeleton-block');
			blocks.forEach((block) => {
				expect(block).not.toHaveAttribute('tabindex');
			});
		});
	});

	describe('Styling and CSS Classes', () => {
		it('applies skeleton-loader class', () => {
			const { container } = render(SkeletonLoader);

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toBeInTheDocument();
			expect(loader).toHaveClass('skeleton-loader');
		});

		it('applies skeleton-block class to each block', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 3 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(3);
			blocks.forEach((block) => {
				expect(block).toHaveClass('skeleton-block');
			});
		});
	});

	describe('Edge Cases', () => {
		it('handles zero blocks', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 0 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(0);
		});

		it('handles large number of blocks', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 50 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(50);
		});
	});

	describe('Component Props', () => {
		it('accepts blocks prop as number', () => {
			const { container } = render(SkeletonLoader, {
				props: { blocks: 10 }
			});

			const blocks = container.querySelectorAll('.skeleton-block');
			expect(blocks).toHaveLength(10);
		});

		it('accepts variant prop as "light"', () => {
			const { container } = render(SkeletonLoader, {
				props: { variant: 'light' }
			});

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toHaveClass('light');
		});

		it('accepts variant prop as "dark"', () => {
			const { container } = render(SkeletonLoader, {
				props: { variant: 'dark' }
			});

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toHaveClass('dark');
		});
	});

	describe('Responsive Design', () => {
		it('renders without errors', () => {
			const { container } = render(SkeletonLoader);

			const loader = container.querySelector('.skeleton-loader');
			expect(loader).toBeInTheDocument();
		});

		it('maintains structure with different block counts', () => {
			const { container: container1 } = render(SkeletonLoader, { props: { blocks: 3 } });
			const { container: container2 } = render(SkeletonLoader, { props: { blocks: 10 } });

			expect(container1.querySelector('.skeleton-loader')).toBeInTheDocument();
			expect(container2.querySelector('.skeleton-loader')).toBeInTheDocument();
		});
	});
});
