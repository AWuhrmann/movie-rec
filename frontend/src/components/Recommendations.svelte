<!-- Recommendations.svelte -->
<script lang="ts">
  import { recommendations } from '$lib/recommendationStore';
  
  let selectedAlgorithm = 'collaborative';
  let isLoading = false;
  let error: string | null = null;

  const algorithms = [
    { id: 'collaborative', name: 'Collaborative Filtering' },
    { id: 'content_based', name: 'Content Based' },
    { id: 'hybrid', name: 'Hybrid' }
  ];

  async function generateRecommendations() {
    isLoading = true;
    error = null;
    try {
      await recommendations.generateRecommendations(selectedAlgorithm);
    } catch (e) {
      error = "Failed to generate recommendations";
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="w-64 bg-white rounded-lg shadow-md p-4">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold">Recommendations</h2>
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Algorithm
      </label>
      <select
        bind:value={selectedAlgorithm}
        class="w-full p-2 border rounded"
      >
        {#each algorithms as algo}
          <option value={algo.id}>{algo.name}</option>
        {/each}
      </select>
    </div>
  
    <button
      on:click={generateRecommendations}
      class="w-full bg-blue-500 text-white p-2 rounded disabled:opacity-50"
      disabled={isLoading}
    >
      {isLoading ? 'Generating...' : 'Generate Recommendations'}
    </button>
  </div>

  {#if error}
    <div class="text-red-500 text-sm mb-4">{error}</div>
  {/if}

  {#if isLoading}
    <div class="space-y-4">
      {#each Array(3) as _}
        <div class="p-2 bg-gray-50 rounded animate-pulse">
          <div class="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      {/each}
    </div>
  {:else if $recommendations.length === 0}
    <p class="text-gray-500">Click generate to see recommendations</p>
  {:else}
    <div class="space-y-4">
      {#each $recommendations as movie (movie.id)}
        <div class="p-2 bg-gray-50 rounded">
          <h3 class="font-medium">{movie.title}</h3>
          <p class="text-sm text-gray-600">{movie.year}</p>
          {#if movie.imdbRating !== "N/A"}
            <p class="text-sm text-yellow-600">⭐ {movie.imdbRating}</p>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>