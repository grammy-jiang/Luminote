/**
 * Unit tests for TranslationPane component.
 */

import { describe, it, expect } from 'vitest';
import { render } from '../test-utils';
import { screen } from '@testing-library/svelte';
import TranslationPane from './TranslationPane.svelte';
import type { ContentBlock } from '$lib/types/api';

describe('TranslationPane Component', () => {
	describe('Empty State', () => {
		it('renders empty state when no blocks provided', () => {
			render(TranslationPane, { props: { blocks: [] } });

			expect(screen.getByText('No translated content to display')).toBeInTheDocument();
		});

		it('renders loading state when loading is true and no blocks', () => {
			render(TranslationPane, { props: { blocks: [], loading: true } });

			expect(screen.getByText('Translating content...')).toBeInTheDocument();
		});

		it('has article role for accessibility', () => {
			render(TranslationPane, { props: { blocks: [] } });

			const article = screen.getByRole('article');
			expect(article).toBeInTheDocument();
			expect(article).toHaveAttribute('aria-label', 'Translation content');
		});
	});

	describe('Paragraph Blocks', () => {
		it('renders paragraph block with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Esta es una traducción.',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toBeInTheDocument();
			expect(paragraph).toHaveTextContent('Esta es una traducción.');
			expect(paragraph).toHaveAttribute('data-block-type', 'paragraph');
			expect(paragraph).toHaveAttribute('id', 'p1');
		});

		it('applies auto text direction by default', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Hello world',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toHaveAttribute('dir', 'auto');
		});

		it('applies RTL direction for Arabic language', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'مرحبا بالعالم',
					metadata: { language: 'ar' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('applies RTL direction for Hebrew language', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'שלום עולם',
					metadata: { language: 'he' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('applies LTR direction for English language', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Hello world',
					metadata: { language: 'en' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="p1"]');
			expect(paragraph).toHaveAttribute('dir', 'ltr');
		});

		it('shows loading indicator for loading block', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Translating...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const wrapper = container.querySelector('.block-wrapper');
			expect(wrapper).toHaveClass('block-loading');
			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});

		it('renders multiple paragraph blocks', () => {
			const blocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'First paragraph.', metadata: {} },
				{ id: 'p2', type: 'paragraph', text: 'Second paragraph.', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

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
					text: 'Título Principal',
					metadata: { level: 1 }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const heading = container.querySelector('h1[data-block-id="h1"]');
			expect(heading).toBeInTheDocument();
			expect(heading).toHaveTextContent('Título Principal');
			expect(heading).toHaveAttribute('data-block-type', 'heading');
		});

		it('applies RTL direction to RTL language headings', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h1',
					type: 'heading',
					text: 'عنوان رئيسي',
					metadata: { level: 1, language: 'ar' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const heading = container.querySelector('h1[data-block-id="h1"]');
			expect(heading).toHaveAttribute('dir', 'rtl');
		});

		it('renders all heading levels (h1-h6)', () => {
			const blocks: ContentBlock[] = [
				{ id: 'h1', type: 'heading', text: 'H1', metadata: { level: 1 } },
				{ id: 'h2', type: 'heading', text: 'H2', metadata: { level: 2 } },
				{ id: 'h3', type: 'heading', text: 'H3', metadata: { level: 3 } },
				{ id: 'h4', type: 'heading', text: 'H4', metadata: { level: 4 } },
				{ id: 'h5', type: 'heading', text: 'H5', metadata: { level: 5 } },
				{ id: 'h6', type: 'heading', text: 'H6', metadata: { level: 6 } }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('h1[data-block-id="h1"]')).toBeInTheDocument();
			expect(container.querySelector('h2[data-block-id="h2"]')).toBeInTheDocument();
			expect(container.querySelector('h3[data-block-id="h3"]')).toBeInTheDocument();
			expect(container.querySelector('h4[data-block-id="h4"]')).toBeInTheDocument();
			expect(container.querySelector('h5[data-block-id="h5"]')).toBeInTheDocument();
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

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('h2[data-block-id="h-default"]')).toBeInTheDocument();
		});

		it('shows loading indicator for loading heading', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'h1',
					type: 'heading',
					text: 'Loading...',
					metadata: { level: 1, loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});
	});

	describe('Code Blocks', () => {
		it('renders code block with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code1',
					type: 'code',
					text: 'console.log("Hola");',
					metadata: { language: 'javascript' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const pre = container.querySelector('pre[data-block-id="code1"]');
			expect(pre).toBeInTheDocument();
			expect(pre).toHaveAttribute('data-block-type', 'code');

			const code = pre?.querySelector('code');
			expect(code).toBeInTheDocument();
			expect(code).toHaveTextContent('console.log("Hola");');
		});

		it('applies language class for syntax highlighting', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code2',
					type: 'code',
					text: 'def hola(): pasar',
					metadata: { language: 'python' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const code = container.querySelector('code');
			expect(code).toHaveClass('language-python');
		});

		it('defaults to plaintext when language is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code3',
					type: 'code',
					text: 'algún código',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

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

			const { container } = render(TranslationPane, { props: { blocks } });

			const pre = container.querySelector('pre');
			expect(pre).toHaveAttribute('aria-label', 'Code block in typescript');
		});

		it('shows loading indicator for loading code block', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code1',
					type: 'code',
					text: 'Translating...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});
	});

	describe('List Blocks', () => {
		it('renders unordered list when ordered is false', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list1',
					type: 'list',
					text: '- Ítem 1\n- Ítem 2\n- Ítem 3',
					metadata: { ordered: false }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const ul = container.querySelector('ul[data-block-id="list1"]');
			expect(ul).toBeInTheDocument();
			expect(ul).toHaveAttribute('data-block-type', 'list');

			const items = ul?.querySelectorAll('li');
			expect(items).toHaveLength(3);
			expect(items?.[0]).toHaveTextContent('Ítem 1');
			expect(items?.[1]).toHaveTextContent('Ítem 2');
			expect(items?.[2]).toHaveTextContent('Ítem 3');
		});

		it('renders ordered list when ordered is true', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list2',
					type: 'list',
					text: '1. Primero\n2. Segundo\n3. Tercero',
					metadata: { ordered: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const ol = container.querySelector('ol[data-block-id="list2"]');
			expect(ol).toBeInTheDocument();

			const items = ol?.querySelectorAll('li');
			expect(items).toHaveLength(3);
			expect(items?.[0]).toHaveTextContent('Primero');
			expect(items?.[1]).toHaveTextContent('Segundo');
			expect(items?.[2]).toHaveTextContent('Tercero');
		});

		it('applies RTL direction to RTL language lists', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list1',
					type: 'list',
					text: '- عنصر ١\n- عنصر ٢',
					metadata: { ordered: false, language: 'ar' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const ul = container.querySelector('ul[data-block-id="list1"]');
			expect(ul).toHaveAttribute('dir', 'rtl');
		});

		it('defaults to unordered list when ordered is missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list3',
					type: 'list',
					text: '- Ítem A\n- Ítem B',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('ul[data-block-id="list3"]')).toBeInTheDocument();
		});

		it('shows loading indicator for loading list', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'list1',
					type: 'list',
					text: '- Loading...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});
	});

	describe('Quote Blocks', () => {
		it('renders blockquote with text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'quote1',
					type: 'quote',
					text: 'Esta es una cita famosa.',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const blockquote = container.querySelector('blockquote[data-block-id="quote1"]');
			expect(blockquote).toBeInTheDocument();
			expect(blockquote).toHaveTextContent('Esta es una cita famosa.');
			expect(blockquote).toHaveAttribute('data-block-type', 'quote');
		});

		it('applies RTL direction to RTL language quotes', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'quote1',
					type: 'quote',
					text: 'اقتباس شهير',
					metadata: { language: 'ar' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const blockquote = container.querySelector('blockquote[data-block-id="quote1"]');
			expect(blockquote).toHaveAttribute('dir', 'rtl');
		});

		it('renders multiple quotes', () => {
			const blocks: ContentBlock[] = [
				{ id: 'q1', type: 'quote', text: 'Primera cita', metadata: {} },
				{ id: 'q2', type: 'quote', text: 'Segunda cita', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('blockquote[data-block-id="q1"]')).toBeInTheDocument();
			expect(container.querySelector('blockquote[data-block-id="q2"]')).toBeInTheDocument();
		});

		it('shows loading indicator for loading quote', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'quote1',
					type: 'quote',
					text: 'Loading...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});
	});

	describe('Image Blocks', () => {
		it('renders image with src from metadata', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img1',
					type: 'image',
					text: 'Subtítulo de imagen',
					metadata: {
						src: 'https://example.com/image.jpg',
						alt: 'Imagen de ejemplo'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const figure = container.querySelector('figure[data-block-id="img1"]');
			expect(figure).toBeInTheDocument();
			expect(figure).toHaveAttribute('data-block-type', 'image');

			const img = figure?.querySelector('img');
			expect(img).toBeInTheDocument();
			expect(img).toHaveAttribute('src', 'https://example.com/image.jpg');
			expect(img).toHaveAttribute('alt', 'Imagen de ejemplo');
			expect(img).toHaveAttribute('loading', 'lazy');
		});

		it('defaults alt to "Translated image" when missing', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img3',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/no-alt.jpg' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('alt', 'Translated image');
		});

		it('renders figcaption with RTL direction', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img4',
					type: 'image',
					text: 'منظر طبيعي جميل',
					metadata: {
						src: 'https://example.com/landscape.jpg',
						alt: 'Landscape',
						language: 'ar'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const figcaption = container.querySelector('figcaption');
			expect(figcaption).toBeInTheDocument();
			expect(figcaption).toHaveAttribute('dir', 'rtl');
		});

		it('applies lazy loading attribute', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img6',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/lazy.jpg', alt: 'Carga diferida' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('loading', 'lazy');
		});

		it('shows loading indicator for loading image', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'img1',
					type: 'image',
					text: 'Loading...',
					metadata: {
						src: 'https://example.com/image.jpg',
						loading: true
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('.block-loading-overlay')).toBeInTheDocument();
		});
	});

	describe('Mixed Content', () => {
		it('renders multiple block types in order', () => {
			const blocks: ContentBlock[] = [
				{ id: 'h1', type: 'heading', text: 'Título', metadata: { level: 1 } },
				{ id: 'p1', type: 'paragraph', text: 'Párrafo de introducción.', metadata: {} },
				{ id: 'code1', type: 'code', text: 'console.log()', metadata: { language: 'js' } },
				{ id: 'list1', type: 'list', text: '- Ítem 1\n- Ítem 2', metadata: { ordered: false } },
				{ id: 'quote1', type: 'quote', text: 'Una cita', metadata: {} },
				{
					id: 'img1',
					type: 'image',
					text: 'Subtítulo',
					metadata: { src: 'https://example.com/test.jpg', alt: 'Prueba' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('h1[data-block-id="h1"]')).toBeInTheDocument();
			expect(container.querySelector('p[data-block-id="p1"]')).toBeInTheDocument();
			expect(container.querySelector('pre[data-block-id="code1"]')).toBeInTheDocument();
			expect(container.querySelector('ul[data-block-id="list1"]')).toBeInTheDocument();
			expect(container.querySelector('blockquote[data-block-id="quote1"]')).toBeInTheDocument();
			expect(container.querySelector('figure[data-block-id="img1"]')).toBeInTheDocument();
		});

		it('renders mix of loading and loaded blocks', () => {
			const blocks: ContentBlock[] = [
				{ id: 'p1', type: 'paragraph', text: 'Loaded paragraph', metadata: {} },
				{
					id: 'p2',
					type: 'paragraph',
					text: 'Loading paragraph',
					metadata: { loading: true }
				},
				{ id: 'p3', type: 'paragraph', text: 'Another loaded', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const wrappers = container.querySelectorAll('.block-wrapper');
			expect(wrappers).toHaveLength(3);

			// Only middle one should have loading class
			expect(wrappers[0]).not.toHaveClass('block-loading');
			expect(wrappers[1]).toHaveClass('block-loading');
			expect(wrappers[2]).not.toHaveClass('block-loading');
		});
	});

	describe('Block IDs and Data Attributes', () => {
		it('maintains block ID on each element', () => {
			const blocks: ContentBlock[] = [
				{ id: 'unique-456', type: 'paragraph', text: 'Prueba', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const element = container.querySelector('[data-block-id="unique-456"]');
			expect(element).toBeInTheDocument();
			expect(element).toHaveAttribute('id', 'unique-456');
		});

		it('sets data-block-type attribute correctly', () => {
			const blocks: ContentBlock[] = [
				{ id: '1', type: 'paragraph', text: 'P', metadata: {} },
				{ id: '2', type: 'heading', text: 'H', metadata: { level: 1 } },
				{ id: '3', type: 'code', text: 'C', metadata: {} },
				{ id: '4', type: 'list', text: '- L', metadata: {} },
				{ id: '5', type: 'quote', text: 'Q', metadata: {} },
				{
					id: '6',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/i.jpg', alt: 'I' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

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

			const { container } = render(TranslationPane, { props: { blocks } });

			expect(container.querySelector('p')).toBeInTheDocument();
			expect(container.querySelector('h1')).toBeInTheDocument();
			expect(container.querySelector('blockquote')).toBeInTheDocument();
		});

		it('provides aria-label for code blocks', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'c1',
					type: 'code',
					text: 'código',
					metadata: { language: 'javascript' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const pre = container.querySelector('pre');
			expect(pre).toHaveAttribute('aria-label');
		});

		it('provides alt text for images', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'i1',
					type: 'image',
					text: '',
					metadata: { src: 'https://example.com/test.jpg', alt: 'Imagen de prueba' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toHaveAttribute('alt', 'Imagen de prueba');
		});
	});

	describe('RTL Language Support', () => {
		it('supports Arabic (ar) as RTL', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'مرحبا',
					metadata: { language: 'ar' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('supports Hebrew (he) as RTL', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'שלום',
					metadata: { language: 'he' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('supports Persian (fa) as RTL', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'سلام',
					metadata: { language: 'fa' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('supports Urdu (ur) as RTL', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'ہیلو',
					metadata: { language: 'ur' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('supports Yiddish (yi) as RTL', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'העלא',
					metadata: { language: 'yi' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			expect(paragraph).toHaveAttribute('dir', 'rtl');
		});

		it('treats LTR languages as LTR', () => {
			const ltrLanguages = ['en', 'es', 'fr', 'de', 'ja', 'zh'];

			ltrLanguages.forEach((lang) => {
				const blocks: ContentBlock[] = [
					{
						id: 'p1',
						type: 'paragraph',
						text: 'Test',
						metadata: { language: lang }
					}
				];

				const { container } = render(TranslationPane, { props: { blocks } });

				const paragraph = container.querySelector('p');
				expect(paragraph).toHaveAttribute('dir', 'ltr');
			});
		});
	});

	describe('Loading States', () => {
		it('shows spinner in empty state when loading', () => {
			render(TranslationPane, { props: { blocks: [], loading: true } });

			const spinner = document.querySelector('.spinner');
			expect(spinner).toBeInTheDocument();
		});

		it('shows loading overlay on individual blocks', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Loading...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const overlay = container.querySelector('.block-loading-overlay');
			expect(overlay).toBeInTheDocument();

			const spinner = overlay?.querySelector('.spinner-small');
			expect(spinner).toBeInTheDocument();
		});

		it('applies opacity to loading blocks', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'p1',
					type: 'paragraph',
					text: 'Loading...',
					metadata: { loading: true }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const wrapper = container.querySelector('.block-wrapper');
			expect(wrapper).toHaveClass('block-loading');
		});
	});

	describe('Edge Cases', () => {
		it('handles empty text in blocks', () => {
			const blocks: ContentBlock[] = [{ id: 'empty', type: 'paragraph', text: '', metadata: {} }];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="empty"]');
			expect(paragraph).toBeInTheDocument();
			expect(paragraph).toHaveTextContent('');
		});

		it('handles missing metadata gracefully', () => {
			const blocks: ContentBlock[] = [
				{ id: 'no-meta', type: 'heading', text: 'Título', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			// Should default to h2
			expect(container.querySelector('h2[data-block-id="no-meta"]')).toBeInTheDocument();
		});

		it('handles invalid language codes gracefully', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'invalid-lang',
					type: 'paragraph',
					text: 'Test',
					metadata: { language: 'invalid' }
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p');
			// Should default to auto for language codes that are not exactly 2 characters long
			expect(paragraph).toHaveAttribute('dir', 'auto');
		});
	});

	describe('Security', () => {
		it('blocks javascript: URLs in image src', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'xss1',
					type: 'image',
					text: 'XSS attempt',
					metadata: {
						src: 'javascript:alert("XSS")',
						alt: 'Malicious image'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			// Image should not be rendered with javascript: URL
			const img = container.querySelector('img');
			expect(img).not.toBeInTheDocument();
		});

		it('blocks data: URLs in image src', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'xss2',
					type: 'image',
					text: 'Data URL attempt',
					metadata: {
						src: 'data:text/html,<script>alert("XSS")</script>',
						alt: 'Data URL image'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			// Image should not be rendered with data: URL
			const img = container.querySelector('img');
			expect(img).not.toBeInTheDocument();
		});

		it('allows valid https URLs in image src', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'safe2',
					type: 'image',
					text: 'Safe image',
					metadata: {
						src: 'https://example.com/image.jpg',
						alt: 'Safe HTTPS image'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const img = container.querySelector('img');
			expect(img).toBeInTheDocument();
			expect(img).toHaveAttribute('src', 'https://example.com/image.jpg');
		});

		it('sanitizes code language to prevent class injection', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'code-xss',
					type: 'code',
					text: 'console.log("test")',
					metadata: {
						language: 'javascript malicious-class" onload="alert(1)'
					}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const code = container.querySelector('code');
			expect(code).toBeInTheDocument();
			// Should default to plaintext for invalid language
			expect(code).toHaveClass('language-plaintext');
		});

		it('escapes HTML in paragraph text', () => {
			const blocks: ContentBlock[] = [
				{
					id: 'html-escape',
					type: 'paragraph',
					text: '<script>alert("XSS")</script>',
					metadata: {}
				}
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const paragraph = container.querySelector('p[data-block-id="html-escape"]');
			expect(paragraph).toBeInTheDocument();
			// Text should be escaped, not executed
			expect(paragraph?.textContent?.trim()).toBe('<script>alert("XSS")</script>');
			// No script tag should be in DOM
			expect(container.querySelector('script')).not.toBeInTheDocument();
		});
	});

	describe('Keyboard Navigation', () => {
		it('navigates to next block with ArrowDown', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} },
				{ id: 'block-3', type: 'paragraph', text: 'Third block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;
			const secondBlock = container.querySelector('[data-block-id="block-2"]') as HTMLElement;

			expect(firstBlock).toBeInTheDocument();
			expect(secondBlock).toBeInTheDocument();

			// Focus first block and press ArrowDown
			firstBlock.focus();
			await firstBlock.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true })
			);

			// Wait for focus to be set
			await new Promise((resolve) => setTimeout(resolve, 50));

			// Second block should be focused
			expect(document.activeElement).toBe(secondBlock);
		});

		it('navigates to previous block with ArrowUp', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} },
				{ id: 'block-3', type: 'paragraph', text: 'Third block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;
			const secondBlock = container.querySelector('[data-block-id="block-2"]') as HTMLElement;

			// Focus second block and press ArrowUp
			secondBlock.focus();
			await secondBlock.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true })
			);

			// Wait for focus to be set
			await new Promise((resolve) => setTimeout(resolve, 50));

			// First block should be focused
			expect(document.activeElement).toBe(firstBlock);
		});

		it('does not navigate beyond first block with ArrowUp', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;

			// Focus first block and press ArrowUp
			firstBlock.focus();
			await firstBlock.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true })
			);

			// Wait for potential focus change
			await new Promise((resolve) => setTimeout(resolve, 50));

			// Should remain on first block (no error thrown)
			expect(container.querySelector('[data-block-id="block-1"]')).toBeInTheDocument();
		});

		it('does not navigate beyond last block with ArrowDown', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const secondBlock = container.querySelector('[data-block-id="block-2"]') as HTMLElement;

			// Focus last block and press ArrowDown
			secondBlock.focus();
			await secondBlock.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true })
			);

			// Wait for potential focus change
			await new Promise((resolve) => setTimeout(resolve, 50));

			// Should remain on last block (no error thrown)
			expect(container.querySelector('[data-block-id="block-2"]')).toBeInTheDocument();
		});

		it('navigates to first block with Home key', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} },
				{ id: 'block-3', type: 'paragraph', text: 'Third block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;
			const thirdBlock = container.querySelector('[data-block-id="block-3"]') as HTMLElement;

			// Focus third block and press Home
			thirdBlock.focus();
			await thirdBlock.dispatchEvent(new KeyboardEvent('keydown', { key: 'Home', bubbles: true }));

			// Wait for focus to be set
			await new Promise((resolve) => setTimeout(resolve, 50));

			// First block should be focused
			expect(document.activeElement).toBe(firstBlock);
		});

		it('navigates to last block with End key', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} },
				{ id: 'block-3', type: 'paragraph', text: 'Third block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;
			const thirdBlock = container.querySelector('[data-block-id="block-3"]') as HTMLElement;

			// Focus first block and press End
			firstBlock.focus();
			await firstBlock.dispatchEvent(new KeyboardEvent('keydown', { key: 'End', bubbles: true }));

			// Wait for focus to be set
			await new Promise((resolve) => setTimeout(resolve, 50));

			// Last block should be focused
			expect(document.activeElement).toBe(thirdBlock);
		});

		it('prevents default behavior for navigation keys', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First block', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Second block', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;

			// Create events and check if preventDefault was called
			const arrowDownEvent = new KeyboardEvent('keydown', {
				key: 'ArrowDown',
				bubbles: true,
				cancelable: true
			});
			const homeEvent = new KeyboardEvent('keydown', {
				key: 'Home',
				bubbles: true,
				cancelable: true
			});
			const endEvent = new KeyboardEvent('keydown', {
				key: 'End',
				bubbles: true,
				cancelable: true
			});

			firstBlock.dispatchEvent(arrowDownEvent);
			expect(arrowDownEvent.defaultPrevented).toBe(true);

			firstBlock.dispatchEvent(homeEvent);
			expect(homeEvent.defaultPrevented).toBe(true);

			firstBlock.dispatchEvent(endEvent);
			expect(endEvent.defaultPrevented).toBe(true);
		});

		it('works with different block types', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'h1', type: 'heading', text: 'Título', metadata: { level: 1 } },
				{ id: 'p1', type: 'paragraph', text: 'Párrafo', metadata: {} },
				{ id: 'c1', type: 'code', text: 'código', metadata: { language: 'js' } },
				{ id: 'l1', type: 'list', text: '- Elemento 1\n- Elemento 2', metadata: { ordered: false } }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const heading = container.querySelector('[data-block-id="h1"]') as HTMLElement;
			const paragraph = container.querySelector('[data-block-id="p1"]') as HTMLElement;

			// Navigate from heading to paragraph
			heading.focus();
			await heading.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true })
			);

			await new Promise((resolve) => setTimeout(resolve, 50));
			expect(document.activeElement).toBe(paragraph);
		});

		it('works with loading blocks', async () => {
			const blocks: ContentBlock[] = [
				{ id: 'block-1', type: 'paragraph', text: 'First', metadata: {} },
				{ id: 'block-2', type: 'paragraph', text: 'Loading...', metadata: { loading: true } },
				{ id: 'block-3', type: 'paragraph', text: 'Third', metadata: {} }
			];

			const { container } = render(TranslationPane, { props: { blocks } });

			const firstBlock = container.querySelector('[data-block-id="block-1"]') as HTMLElement;
			const secondBlock = container.querySelector('[data-block-id="block-2"]') as HTMLElement;

			// Navigate to loading block
			firstBlock.focus();
			await firstBlock.dispatchEvent(
				new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true })
			);

			await new Promise((resolve) => setTimeout(resolve, 50));
			expect(document.activeElement).toBe(secondBlock);
		});
	});
});
