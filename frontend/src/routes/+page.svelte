<script lang="ts">
	import DualPaneLayout from '$lib/components/DualPaneLayout.svelte';
	import SourcePane from '$lib/components/SourcePane.svelte';
	import TranslationPane from '$lib/components/TranslationPane.svelte';
	import type { ContentBlock } from '$lib/types/api';
	import { onMount } from 'svelte';

	let mounted = false;
	let splitRatio = 50;

	// Sample content blocks for demonstration
	const sourceBlocks: ContentBlock[] = [
		{
			id: 'h1',
			type: 'heading',
			text: 'Keyboard Navigation Guide',
			metadata: { level: 1 }
		},
		{
			id: 'p1',
			type: 'paragraph',
			text: 'Welcome to Luminote! This demo shows the keyboard navigation features. Try using your keyboard to navigate through the content blocks below.',
			metadata: {}
		},
		{
			id: 'h2',
			type: 'heading',
			text: 'Navigation Keys',
			metadata: { level: 2 }
		},
		{
			id: 'list1',
			type: 'list',
			text: '- Arrow Up/Down: Navigate between blocks\n- Tab: Switch between panes\n- Enter: Jump to corresponding block\n- Home/End: Jump to first/last block',
			metadata: { ordered: false }
		},
		{
			id: 'h3',
			type: 'heading',
			text: 'Try It Out',
			metadata: { level: 2 }
		},
		{
			id: 'p2',
			type: 'paragraph',
			text: 'Click on this paragraph to focus it, then use Arrow Down to navigate to the next block. Press Enter to jump to the corresponding block in the translation pane.',
			metadata: {}
		},
		{
			id: 'quote1',
			type: 'quote',
			text: 'Power users need keyboard-only navigation through blocks for efficiency.',
			metadata: {}
		},
		{
			id: 'code1',
			type: 'code',
			text: 'function navigate() {\n  console.log("Using keyboard!");\n}',
			metadata: { language: 'javascript' }
		},
		{
			id: 'p3',
			type: 'paragraph',
			text: 'All keyboard navigation works with screen readers and follows WCAG 2.1 accessibility guidelines.',
			metadata: {}
		}
	];

	const translationBlocks: ContentBlock[] = [
		{
			id: 'h1',
			type: 'heading',
			text: '键盘导航指南',
			metadata: { level: 1 }
		},
		{
			id: 'p1',
			type: 'paragraph',
			text: '欢迎使用 Luminote！此演示展示了键盘导航功能。请尝试使用键盘浏览下面的内容块。',
			metadata: {}
		},
		{
			id: 'h2',
			type: 'heading',
			text: '导航键',
			metadata: { level: 2 }
		},
		{
			id: 'list1',
			type: 'list',
			text: '- 方向键上/下：在块之间导航\n- Tab键：切换窗格\n- Enter键：跳转到对应块\n- Home/End键：跳转到第一个/最后一个块',
			metadata: { ordered: false }
		},
		{
			id: 'h3',
			type: 'heading',
			text: '试一试',
			metadata: { level: 2 }
		},
		{
			id: 'p2',
			type: 'paragraph',
			text: '点击此段落使其获得焦点，然后使用向下箭头键导航到下一个块。按Enter键跳转到源窗格中的对应块。',
			metadata: {}
		},
		{
			id: 'quote1',
			type: 'quote',
			text: '高级用户需要纯键盘导航来提高效率。',
			metadata: {}
		},
		{
			id: 'code1',
			type: 'code',
			text: 'function navigate() {\n  console.log("使用键盘！");\n}',
			metadata: { language: 'javascript' }
		},
		{
			id: 'p3',
			type: 'paragraph',
			text: '所有键盘导航功能都支持屏幕阅读器，并遵循WCAG 2.1无障碍指南。',
			metadata: {}
		}
	];

	onMount(() => {
		mounted = true;
	});

	function handleSplitChange(event: CustomEvent<{ leftWidth: number; rightWidth: number }>) {
		splitRatio = event.detail.leftWidth;
	}
</script>

<DualPaneLayout
	leftLabel="Source Content"
	rightLabel="Translation"
	on:splitChange={handleSplitChange}
>
	<!-- Left pane: Source content with keyboard navigation -->
	<div slot="left">
		<SourcePane blocks={sourceBlocks} />
	</div>

	<!-- Right pane: Translation with keyboard navigation -->
	<div slot="right">
		<TranslationPane blocks={translationBlocks} />
	</div>
</DualPaneLayout>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		height: 100vh;
		overflow: hidden;
	}
</style>
