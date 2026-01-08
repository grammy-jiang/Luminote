<script lang="ts">
	import { onMount } from 'svelte';

	let mounted = false;

	onMount(() => {
		mounted = true;
	});
</script>

<div
	class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4"
>
	<div class="max-w-4xl w-full">
		<div class="bg-white rounded-2xl shadow-xl p-8 md:p-12">
			<h1
				class="text-4xl md:text-5xl font-bold text-center mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"
			>
				Luminote Frontend
			</h1>

			<p class="text-lg text-gray-600 text-center mb-8">
				AI-powered two-pane translation workbench for fast, accurate understanding
			</p>

			<div class="space-y-4">
				<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
					<h2 class="font-semibold text-blue-900 mb-2">✅ SvelteKit Initialized</h2>
					<p class="text-blue-800 text-sm">TypeScript, Vite, and routing configured</p>
				</div>

				<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
					<h2 class="font-semibold text-green-900 mb-2">✅ Tailwind CSS Working</h2>
					<p class="text-green-800 text-sm">Styling system active and responsive</p>
				</div>

				<div class="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
					<h2 class="font-semibold text-purple-900 mb-2">✅ Development Tools Ready</h2>
					<p class="text-purple-800 text-sm">ESLint, Prettier, and Vitest configured</p>
				</div>

				{#if mounted}
					<div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
						<h2 class="font-semibold text-yellow-900 mb-2">✅ Client-side Rendering</h2>
						<p class="text-yellow-800 text-sm">Svelte reactive features working</p>
					</div>
				{/if}
			</div>

			<div class="mt-8 pt-8 border-t border-gray-200">
				<p class="text-sm text-gray-500 text-center">Ready to build Phase 1 features</p>
			</div>
		</div>
	</div>
</div>
