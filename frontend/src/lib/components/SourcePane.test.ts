/**
 * Unit tests for SourcePane component.
 */

import { describe, it, expect } from 'vitest';
import { render } from '../test-utils';
import { screen } from '@testing-library/svelte';
import SourcePane from './SourcePane.svelte';
import type { ContentBlock } from '$lib/types/api';

describe('SourcePane Component', () => {
	describe('Empty State', () => {
		it('renders empty state when no blocks provided', () => {
			render(SourcePane, { props: { blocks: [] } });

			expect(screen.getByText('No content blocks to display')).toBeInTheDocument();
		});

		it('has article role for accessibility', () => {
			render(SourcePane, { props: { blocks: [] } });

			const article = screen.getByRole('article');
			expect(article).toBeInTheDocument();
			expect(article).toHaveAttribute('aria-label', 'Source content');
		});
	});

	describe('Paragraph Blocks', () => {
		it('renders paragraph block with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'This is a paragraph.',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toBeInTheDocument();
			expect(paragraph).toHaveTextContent('This is a paragraph.');
			expect(paragraph).toHaveAttribute('data-block-type', 'paragraph');
			expect(paragraph).toHaveAttribute('id', 'p1');
		});

		it('renders multiple paragraph blocks', () => {
			const blocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'First paragraph.', metadata: {} },
				{ id: 'p2', type: 'paragraph', text: 'Second paragraph.', metadata: {} }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('p[data-block-id="p1"]')).toBeInTheDocument();
			expect(container.querySelector('p[data-block-id="p2"]')).toBeInTheDocument();
		});
	});

	describe('Heading Blocks', () => {
		it('renders h1 heading when level is 1', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h1',
					type: 'heading',
					text: 'Main Title',
					metadata: { level: 1 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const heading = container.querySelector('h1[data-block-id="h1"]');
			expect(heading).toBeInTheDocument();
			expect(heading).toHaveTextContent('Main Title');
			expect(heading).toHaveAttribute('data-block-type', 'heading');
		});

		it('renders h2 heading when level is 2', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h2',
					type: 'heading',
					text: 'Section Title',
					metadata: { level: 2 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h2[data-block-id="h2"]')).toBeInTheDocument();
		});

		it('renders h3 heading when level is 3', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h3',
					type: 'heading',
					text: 'Subsection',
					metadata: { level: 3 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h3[data-block-id="h3"]')).toBeInTheDocument();
		});

		it('renders h4 heading when level is 4', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h4',
					type: 'heading',
					text: 'Sub-subsection',
					metadata: { level: 4 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h4[data-block-id="h4"]')).toBeInTheDocument();
		});

		it('renders h5 heading when level is 5', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h5',
					type: 'heading',
					text: 'Minor heading',
					metadata: { level: 5 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h5[data-block-id="h5"]')).toBeInTheDocument();
		});

		it('renders h6 heading when level is 6', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h6',
					type: 'heading',
					text: 'Smallest heading',
					metadata: { level: 6 }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h6[data-block-id="h6"]')).toBeInTheDocument();
		});

		it('defaults to h2 when level is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h-default',
					type: 'heading',
					text: 'Default heading',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h2[data-block-id="h-default"]')).toBeInTheDocument();
		});

		it('defaults to h2 when level is invalid', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h-invalid',
					type: 'heading',
					text: 'Invalid level',
					metadata: { level: 'invalid' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h2[data-block-id="h-invalid"]')).toBeInTheDocument();
		});

		it('renders correct heading hierarchy', () => {
			const blocks: ContentBlock[] = [
				{ id: 'h1', type: 'heading', text: 'Title', metadata: { level: 1 } },
				{ id: 'h2', type: 'heading', text: 'Section', metadata: { level: 2 } },
				{ id: 'h3', type: 'heading', text: 'Subsection', metadata: { level: 3 } }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h1[data-block-id="h1"]')).toBeInTheDocument();
			expect(container.querySelector('h2[data-block-id="h2"]')).toBeInTheDocument();
			expect(container.querySelector('h3[data-block-id="h3"]')).toBeInTheDocument();
		});
	});

	describe('Code Blocks', () => {
		it('renders code block with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code1',
					type: 'code',
					text: 'console.log("Hello");',
					metadata: { language: 'javascript' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const pre = container.querySelector('pre[data-block-id="code1"]');
			expect(pre).toBeInTheDocument();
			expect(pre).toHaveAttribute('data-block-type', 'code');

			const code = pre?.querySelector('code');
			expect(code).toBeInTheDocument();
			expect(code).toHaveTextContent('console.log("Hello");');
		});

		it('applies language class for syntax highlighting', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code2',
					type: 'code',
					text: 'def hello(): pass',
					metadata: { language: 'python' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const code = container.querySelector('code');
			expect(code).toHaveClass('language-python');
		});

		it('defaults to plaintext when language is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code3',
					type: 'code',
					text: 'some code',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const code = container.querySelector('code');
			expect(code).toHaveClass('language-plaintext');
		});

		it('has proper aria-label for accessibility', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code4',
					type: 'code',
					text: 'code content',
					metadata: { language: 'typescript' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const pre = container.querySelector('pre');
			expect(pre).toHaveAttribute('aria-label', 'Code block in typescript');
		});

		it('has basic aria-label when no language specified', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code5',
					type: 'code',
					text: 'code content',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const pre = container.querySelector('pre');
			expect(pre).toHaveAttribute('aria-label', 'Code block');
		});
	});

	describe('List Blocks', () => {
		it('renders unordered list when ordered is false', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list1',
					type: 'list',
					text: '- Item 1\n- Item 2\n- Item 3',
					metadata: { ordered: false }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const ul = container.querySelector('ul[data-block-id="list1"]');
			expect(ul).toBeInTheDocument();
			expect(ul).toHaveAttribute('data-block-type', 'list');

			const items = ul?.querySelectorAll('li');
			expect(items).toHaveLength(3);
			expect(items?.[0]).toHaveTextContent('Item 1');
			expect(items?.[1]).toHaveTextContent('Item 2');
			expect(items?.[2]).toHaveTextContent('Item 3');
		});

		it('renders ordered list when ordered is true', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list2',
					type: 'list',
					text: '1. First\n2. Second\n3. Third',
					metadata: { ordered: true }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const ol = container.querySelector('ol[data-block-id="list2"]');
			expect(ol).toBeInTheDocument();

			const items = ol?.querySelectorAll('li');
			expect(items).toHaveLength(3);
			expect(items?.[0]).toHaveTextContent('First');
			expect(items?.[1]).toHaveTextContent('Second');
			expect(items?.[2]).toHaveTextContent('Third');
		});

		it('defaults to unordered list when ordered is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list3',
					type: 'list',
					text: '- Item A\n- Item B',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('ul[data-block-id="list3"]')).toBeInTheDocument();
		});

		it('handles list with asterisk markers', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list4',
					type: 'list',
					text: '* Item 1\n* Item 2',
					metadata: { ordered: false }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const ul = container.querySelector('ul');
			const items = ul?.querySelectorAll('li');
			expect(items).toHaveLength(2);
			expect(items?.[0]).toHaveTextContent('Item 1');
		});

		it('handles empty lines in list text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list5',
					type: 'list',
					text: '- Item 1\n\n- Item 2\n',
					metadata: { ordered: false }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const ul = container.querySelector('ul');
			const items = ul?.querySelectorAll('li');
			expect(items).toHaveLength(2);
		});
	});

	describe('Quote Blocks', () => {
		it('renders blockquote with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'quote1',
					type: 'quote',
					text: 'This is a famous quote.',
					metadata: {}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const blockquote = container.querySelector('blockquote[data-block-id="quote1"]');
			expect(blockquote).toBeInTheDocument();
			expect(blockquote).toHaveTextContent('This is a famous quote.');
			expect(blockquote).toHaveAttribute('data-block-type', 'quote');
		});

		it('renders multiple quotes', () => {
			const blocks: ContentBlock[] = [
				{ id: 'q1', type: 'quote', text: 'First quote', metadata: {} },
				{ id: 'q2', type: 'quote', text: 'Second quote', metadata: {} }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('blockquote[data-block-id="q1"]')).toBeInTheDocument();
			expect(container.querySelector('blockquote[data-block-id="q2"]')).toBeInTheDocument();
		});
	});

	describe('Image Blocks', () => {
		it('renders image with src from metadata', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img1',
					type: 'image',
					text: 'Image caption',
					metadata: {
						src: 'https://example.com/image.jpg',
						alt: 'Example image'
					}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const figure = container.querySelector('figure[data-block-id="img1"]');
			expect(figure).toBeInTheDocument();
			expect(figure).toHaveAttribute('data-block-type', 'image');

			const img = figure?.querySelector('img');
			expect(img).toBeInTheDocument();
			expect(img).toHaveAttribute('src', 'https://example.com/image.jpg');
			expect(img).toHaveAttribute('alt', 'Example image');
			expect(img).toHaveAttribute('loading', 'lazy');
		});

		it('uses text as src when metadata.src is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img2',
					type: 'image',
					text: 'https://example.com/fallback.jpg',
					metadata: { alt: 'Fallback image' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('src', 'https://example.com/fallback.jpg');
		});

		it('defaults alt to "Image" when missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img3',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/no-alt.jpg' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('alt', 'Image');
		});

		it('renders figcaption when text differs from src', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img4',
					type: 'image',
					text: 'A beautiful landscape',
					metadata: {
						src: 'https://example.com/landscape.jpg',
						alt: 'Landscape'
					}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const figcaption = container.querySelector('figcaption');
			expect(figcaption).toBeInTheDocument();
			expect(figcaption).toHaveTextContent('A beautiful landscape');
		});

		it('does not render figcaption when text equals src', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img5',
					type: 'image',
					text: 'https://example.com/image.jpg',
					metadata: {
						src: 'https://example.com/image.jpg',
						alt: 'Image'
					}
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const figcaption = container.querySelector('figcaption');
			expect(figcaption).not.toBeInTheDocument();
		});

		it('applies lazy loading attribute', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img6',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/lazy.jpg', alt: 'Lazy loaded' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('loading', 'lazy');
		});
	});

	describe('Mixed Content', () => {
		it('renders multiple block types in order', () => {
			const blocks: ContentBlock[] = [
				{ id: 'h1', type: 'heading', text: 'Title', metadata: { level: 1 } },
				{ id: 'p1', type: 'paragraph', text: 'Introduction paragraph.', metadata: {} },
				{ id: 'code1', type: 'code', text: 'console.log()', metadata: { language: 'js' } },
				{ id: 'list1', type: 'list', text: '- Item 1\n- Item 2', metadata: { ordered: false } },
				{ id: 'quote1', type: 'quote', text: 'A quote', metadata: {} },
				{
					id: 'img1',
					type: 'image',
					text: 'Caption',
					metadata: { src: 'test.jpg', alt: 'Test' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('h1[data-block-id="h1"]')).toBeInTheDocument();
			expect(container.querySelector('p[data-block-id="p1"]')).toBeInTheDocument();
			expect(container.querySelector('pre[data-block-id="code1"]')).toBeInTheDocument();
			expect(container.querySelector('ul[data-block-id="list1"]')).toBeInTheDocument();
			expect(container.querySelector('blockquote[data-block-id="quote1"]')).toBeInTheDocument();
			expect(container.querySelector('figure[data-block-id="img1"]')).toBeInTheDocument();
		});
	});

	describe('Block IDs and Data Attributes', () => {
		it('maintains block ID on each element', () => {
			const blocks: ContentBlock[] = [
				{ id: 'unique-123', type: 'paragraph', text: 'Test', metadata: {} }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const element = container.querySelector('[data-block-id="unique-123"]');
			expect(element).toBeInTheDocument();
			expect(element).toHaveAttribute('id', 'unique-123');
		});

		it('sets data-block-type attribute correctly', () => {
			const blocks: ContentBlock[] = [
				{ id: '1', type: 'paragraph', text: 'P', metadata: {} },
				{ id: '2', type: 'heading', text: 'H', metadata: { level: 1 } },
				{ id: '3', type: 'code', text: 'C', metadata: {} },
				{ id: '4', type: 'list', text: '- L', metadata: {} },
				{ id: '5', type: 'quote', text: 'Q', metadata: {} },
				{ id: '6', type: 'image', text: '', metadata: { src: 'i.jpg', alt: 'I' } }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('[data-block-id="1"]')).toHaveAttribute(
				'data-block-type',
				'paragraph'
			);
			expect(container.querySelector('[data-block-id="2"]')).toHaveAttribute(
				'data-block-type',
				'heading'
			);
			expect(container.querySelector('[data-block-id="3"]')).toHaveAttribute(
				'data-block-type',
				'code'
			);
			expect(container.querySelector('[data-block-id="4"]')).toHaveAttribute(
				'data-block-type',
				'list'
			);
			expect(container.querySelector('[data-block-id="5"]')).toHaveAttribute(
				'data-block-type',
				'quote'
			);
			expect(container.querySelector('[data-block-id="6"]')).toHaveAttribute(
				'data-block-type',
				'image'
			);
		});
	});

	describe('Accessibility', () => {
		it('uses semantic HTML elements', () => {
			const blocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'Para', metadata: {} },
				{ id: 'h1', type: 'heading', text: 'Head', metadata: { level: 1 } },
				{ id: 'q1', type: 'quote', text: 'Quote', metadata: {} }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			expect(container.querySelector('p')).toBeInTheDocument();
			expect(container.querySelector('h1')).toBeInTheDocument();
			expect(container.querySelector('blockquote')).toBeInTheDocument();
		});

		it('provides aria-label for code blocks', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'c1',
					type: 'code',
					text: 'code',
					metadata: { language: 'javascript' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const pre = container.querySelector('pre');
			expect(pre).toHaveAttribute('aria-label');
		});

		it('provides alt text for images', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'i1',
					type: 'image',
					text: '',
					metadata: { src: 'test.jpg', alt: 'Test image' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('alt', 'Test image');
		});
	});

	describe('Edge Cases', () => {
		it('handles empty text in blocks', () => {
			const blocks: ContentBlock[] = [{ id: 'empty', type: 'paragraph', text: '', metadata: {} }];

			const { container } = render(SourcePane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="empty"]');
			expect(paragraph).toBeInTheDocument();
			expect(paragraph).toHaveTextContent('');
		});

		it('handles missing metadata gracefully', () => {
			const blocks: ContentBlock[] = [
				{ id: 'no-meta', type: 'heading', text: 'Title', metadata: {} }
			];

			const { container } = render(SourcePane, { props: { blocks } });

			// Should default to h2
			expect(container.querySelector('h2[data-block-id="no-meta"]')).toBeInTheDocument();
		});

		it('handles invalid metadata types gracefully', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'invalid',
					type: 'heading',
					text: 'Title',
					metadata: { level: 'not-a-number' }
				}
			];

			const { container } = render(SourcePane, { props: { blocks } });

			// Should default to h2
			expect(container.querySelector('h2[data-block-id="invalid"]')).toBeInTheDocument();
		});
	});
});
