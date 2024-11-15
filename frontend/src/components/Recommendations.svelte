<script lang="ts">
    import { recommendations } from '$lib/recommendationStore';
    import type { Movie } from '../types/movie';
  
    function generateRecommendations() {
      recommendations.generateRecommendations();
    }
  </script>
  
  <div class="w-64 bg-white rounded-lg shadow-md p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Recommendations</h2>
      <button
        on:click={generateRecommendations}
        class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-sm"
      >
        Generate
      </button>
    </div>
  
    {#if $recommendations.length === 0}
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