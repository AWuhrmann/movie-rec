<script lang="ts">
    import { movies } from '$lib/movieStore';
    
    export let movieId: string;
    export let rating: number;
  
    function handleRating(value: number): void {
      movies.updateRating(movieId, value);
    }
  </script>
  
  <div class="flex gap-1">
    {#each Array(5) as _, i}
      <button
        on:click={() => handleRating(i + 1)}
        class="text-2xl hover:scale-110 transition-transform focus:outline-none focus:ring-2 focus:ring-yellow-400 rounded"
        type="button"
        aria-label="Rate {i + 1} stars"
      >
        {#if i < rating}
          <span class="text-yellow-400">★</span>
        {:else}
          <span class="text-gray-300 hover:text-yellow-200">☆</span>
        {/if}
      </button>
    {/each}
  </div>