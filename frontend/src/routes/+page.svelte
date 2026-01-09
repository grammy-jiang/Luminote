<script lang="ts">
	import DualPaneLayout from '$lib/components/DualPaneLayout.svelte';
	import { onMount } from 'svelte';

	let mounted = false;

	onMount(() => {
		mounted = true;
	});
</script>

<DualPaneLayout leftLabel="Source Content" rightLabel="Translation">
	<!-- Left pane: Source content -->
	<div slot="left" class="p-6 space-y-6">
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Luminote</h1>
			<p class="text-lg text-gray-600">AI-powered two-pane translation workbench</p>
		</div>

		<div class="prose max-w-none">
			<h2 class="text-2xl font-semibold text-gray-800 mb-4">Welcome to Luminote</h2>

			<p class="text-gray-700 mb-4">
				This is the source content pane. In a real application, this would display the extracted
				content from a webpage in reader mode.
			</p>

			<h3 class="text-xl font-semibold text-gray-800 mb-3">Key Features:</h3>

			<ul class="list-disc list-inside space-y-2 text-gray-700 mb-4">
				<li>Two-pane layout with independent scrolling</li>
				<li>Responsive design (stacks vertically on mobile)</li>
				<li>Keyboard navigation (Tab to switch panes)</li>
				<li>Accessible with ARIA labels</li>
				<li>Configurable split ratio</li>
			</ul>

			<p class="text-gray-700 mb-4">
				Try scrolling this pane independently from the right pane. Press Tab to switch focus between
				panes.
			</p>

			<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded my-4">
				<h4 class="font-semibold text-blue-900 mb-2">✅ SvelteKit Initialized</h4>
				<p class="text-blue-800 text-sm">TypeScript, Vite, and routing configured</p>
			</div>

			<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded my-4">
				<h4 class="font-semibold text-green-900 mb-2">✅ Tailwind CSS Working</h4>
				<p class="text-green-800 text-sm">Styling system active and responsive</p>
			</div>

			<div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded my-4">
				<h4 class="font-semibold text-purple-900 mb-2">✅ Development Tools Ready</h4>
				<p class="text-purple-800 text-sm">ESLint, Prettier, and Vitest configured</p>
			</div>

			{#if mounted}
				<div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded my-4">
					<h4 class="font-semibold text-yellow-900 mb-2">✅ Client-side Rendering</h4>
					<p class="text-yellow-800 text-sm">Svelte reactive features working</p>
				</div>
			{/if}

			<p class="text-gray-700 mt-4">
				Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut
				labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
				laboris nisi ut aliquip ex ea commodo consequat.
			</p>
		</div>
	</div>

	<!-- Right pane: Translation -->
	<div slot="right" class="p-6 space-y-6">
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Luminote</h1>
			<p class="text-lg text-gray-600">
				AI驱动的双窗格翻译工作台 (AI-powered two-pane translation workbench)
			</p>
		</div>

		<div class="prose max-w-none">
			<h2 class="text-2xl font-semibold text-gray-800 mb-4">欢迎使用 Luminote</h2>

			<p class="text-gray-700 mb-4">
				这是翻译内容窗格。在实际应用中，这里会显示从网页提取的内容的翻译版本。
			</p>

			<h3 class="text-xl font-semibold text-gray-800 mb-3">主要特点：</h3>

			<ul class="list-disc list-inside space-y-2 text-gray-700 mb-4">
				<li>独立滚动的双窗格布局</li>
				<li>响应式设计（移动端垂直堆叠）</li>
				<li>键盘导航（Tab键切换窗格）</li>
				<li>带有ARIA标签的无障碍访问</li>
				<li>可配置的分割比例</li>
			</ul>

			<p class="text-gray-700 mb-4">尝试独立于左侧窗格滚动此窗格。按Tab键在窗格之间切换焦点。</p>

			<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded my-4">
				<h4 class="font-semibold text-blue-900 mb-2">✅ SvelteKit 已初始化</h4>
				<p class="text-blue-800 text-sm">TypeScript、Vite和路由已配置</p>
			</div>

			<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded my-4">
				<h4 class="font-semibold text-green-900 mb-2">✅ Tailwind CSS 工作正常</h4>
				<p class="text-green-800 text-sm">样式系统活跃且响应式</p>
			</div>

			<div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded my-4">
				<h4 class="font-semibold text-purple-900 mb-2">✅ 开发工具就绪</h4>
				<p class="text-purple-800 text-sm">ESLint、Prettier和Vitest已配置</p>
			</div>

			{#if mounted}
				<div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded my-4">
					<h4 class="font-semibold text-yellow-900 mb-2">✅ 客户端渲染</h4>
					<p class="text-yellow-800 text-sm">Svelte响应式功能工作正常</p>
				</div>
			{/if}

			<p class="text-gray-700 mt-4">
				这是一些填充文本，用于演示独立滚动功能。在实际应用中，这里会显示翻译后的内容，与左侧的源内容相对应。
			</p>
		</div>
	</div>
</DualPaneLayout>
