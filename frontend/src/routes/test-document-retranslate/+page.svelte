<script lang="ts">
/**
 * Test page for DocumentRetranslate component
 *
 * Demonstrates the full document retranslation UI with:
 * - "Re-translate All" button
 * - Document retranslation modal
 * - Progress indicator
 * - Preview and accept/discard workflow
 */

import DualPaneLayout from '$lib/components/DualPaneLayout.svelte';
import SourcePane from '$lib/components/SourcePane.svelte';
import TranslationPane from '$lib/components/TranslationPane.svelte';
import DocumentRetranslate from '$lib/components/DocumentRetranslate.svelte';
import type { ContentBlock } from '$lib/types/api';

// Sample source blocks
const originalBlocks: ContentBlock[] = [
{
id: 'h1',
type: 'heading',
text: 'Advanced Translation Features',
metadata: { level: 1 }
},
{
id: 'p1',
type: 'paragraph',
text: 'This demonstration shows the full document retranslation feature. Click the "Re-translate All" button to retranslate all content blocks at once with custom prompts.',
metadata: {}
},
{
id: 'h2',
type: 'heading',
text: 'Key Features',
metadata: { level: 2 }
},
{
id: 'list1',
type: 'list',
text: '- Batch translation of all content blocks\n- Custom prompt support for refinement\n- Progress indicator during translation\n- Preview changes before accepting\n- Cancel mid-process if needed',
metadata: { ordered: false }
},
{
id: 'p2',
type: 'paragraph',
text: 'The retranslation process maintains document structure and formatting while applying your custom instructions to improve translation quality.',
metadata: {}
},
{
id: 'quote1',
type: 'quote',
text: 'Full document retranslation enables iterative refinement of translations without re-fetching source content.',
metadata: {}
}
];

// Sample translation blocks (initial translation)
let translationBlocks: ContentBlock[] = [
{
id: 'h1',
type: 'heading',
text: '高级翻译功能',
metadata: { level: 1 }
},
{
id: 'p1',
type: 'paragraph',
text: '此演示展示了完整的文档重新翻译功能。点击"重新翻译全部"按钮，使用自定义提示一次性重新翻译所有内容块。',
metadata: {}
},
{
id: 'h2',
type: 'heading',
text: '主要特点',
metadata: { level: 2 }
},
{
id: 'list1',
type: 'list',
text: '- 批量翻译所有内容块\n- 支持自定义提示进行优化\n- 翻译过程中显示进度指示器\n- 接受前预览更改\n- 如需要可以中途取消',
metadata: { ordered: false }
},
{
id: 'p2',
type: 'paragraph',
text: '重新翻译过程保持文档结构和格式，同时应用您的自定义指令以提高翻译质量。',
metadata: {}
},
{
id: 'quote1',
type: 'quote',
text: '完整文档重新翻译可以迭代改进翻译，而无需重新获取源内容。',
metadata: {}
}
];

// Modal state
let showDocumentRetranslateModal = false;

/**
 * Open the document retranslation modal
 */
function handleRetranslateAll() {
showDocumentRetranslateModal = true;
}

/**
 * Handle accepting new translations
 */
function handleAcceptTranslations(event: CustomEvent<{ translations: Map<string, string> }>) {
const { translations } = event.detail;

// Update translation blocks with new translations
translationBlocks = translationBlocks.map((block) => {
const newText = translations.get(block.id);
if (newText) {
return { ...block, text: newText };
}
return block;
});

showDocumentRetranslateModal = false;
console.log('Accepted new translations:', translations);
}

/**
 * Handle discarding translations
 */
function handleDiscardTranslations() {
showDocumentRetranslateModal = false;
console.log('Discarded retranslation');
}

/**
 * Handle modal close
 */
function handleCloseModal() {
showDocumentRetranslateModal = false;
}
</script>

<svelte:head>
<title>Document Retranslation Test - Luminote</title>
</svelte:head>

<div class="page-container">
<!-- Toolbar -->
<div class="toolbar">
<h1 class="toolbar-title">Document Retranslation Demo</h1>
<button
class="btn btn-primary retranslate-all-btn"
on:click={handleRetranslateAll}
data-testid="retranslate-all-button"
>
<svg
class="icon"
width="20"
height="20"
viewBox="0 0 24 24"
fill="none"
stroke="currentColor"
stroke-width="2"
stroke-linecap="round"
stroke-linejoin="round"
>
<path d="M21.5 2v6h-6" />
<path d="M2.5 22v-6h6" />
<path
d="M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"
/>
</svg>
Re-translate All
</button>
</div>

<!-- Dual Pane Layout -->
<div class="content-container">
<DualPaneLayout leftLabel="Source Content" rightLabel="Translation">
<!-- Left pane: Source content -->
<div slot="left">
<SourcePane blocks={originalBlocks} />
</div>

<!-- Right pane: Translation -->
<div slot="right">
<TranslationPane blocks={translationBlocks} originalBlocks={originalBlocks} />
</div>
</DualPaneLayout>
</div>
</div>

<!-- Document Retranslation Modal -->
{#if showDocumentRetranslateModal}
<DocumentRetranslate
blocks={translationBlocks}
originalBlocks={originalBlocks}
on:accept={handleAcceptTranslations}
on:discard={handleDiscardTranslations}
on:close={handleCloseModal}
/>
{/if}

<style>
.page-container {
display: flex;
flex-direction: column;
height: 100vh;
overflow: hidden;
}

.toolbar {
display: flex;
align-items: center;
justify-content: space-between;
padding: 1rem 1.5rem;
background-color: white;
border-bottom: 1px solid #e5e7eb;
flex-shrink: 0;
}

.toolbar-title {
font-size: 1.25rem;
font-weight: 600;
color: #1f2937;
margin: 0;
}

.content-container {
flex: 1;
overflow: hidden;
}

.btn {
display: inline-flex;
align-items: center;
gap: 0.5rem;
padding: 0.625rem 1.25rem;
font-size: 0.9375rem;
font-weight: 500;
border-radius: 0.375rem;
cursor: pointer;
transition: all 0.2s;
border: 1px solid transparent;
}

.btn-primary {
background-color: #3b82f6;
color: white;
border-color: #3b82f6;
}

.btn-primary:hover {
background-color: #2563eb;
border-color: #2563eb;
}

.btn-primary:focus {
outline: 2px solid #3b82f6;
outline-offset: 2px;
}

.icon {
flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
.toolbar {
flex-direction: column;
gap: 1rem;
align-items: stretch;
}

.toolbar-title {
text-align: center;
}

.retranslate-all-btn {
width: 100%;
justify-content: center;
}
}
</style>
