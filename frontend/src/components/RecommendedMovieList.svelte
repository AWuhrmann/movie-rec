<!-- RatedMovieList.svelte -->
<script lang="ts">
    import { getLocalStorage } from '$lib/movieStore';
    import { jobStatus, recommendations } from '$lib/recommendationStore';
    import StarRating from './StarRating.svelte';
    import type { Movie } from '../types/movie';
	import { onMount } from 'svelte';
    import { X } from 'lucide-svelte';
    import { Trash2 } from 'lucide-svelte';


</script>
<div class="w-64 p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Recommendations</h2>
      <button 
      on:click={() => {$recommendations = []}}
        class="text-gray-400 hover:text-red-500 transition-colors"
        aria-label="Clear recommendations"
      >
        <Trash2 size={20} />
      </button>
    </div>
    
    {#if $recommendations.length === 0}
        {#if $jobStatus !== ""}
        <p class="text-gray-500">{$jobStatus}</p>
        {:else}
        <p class="text-gray-500">No recommendations</p>
        {/if}
      {:else}
      <div class="space-y-4">
        {#each $recommendations as movie (movie.id)}
          <div class="rounded relative overflow-hidden group transition-shadow duration-200">
            <div class="relative z-10 bg-white rounded-lg shadow-md backdrop-blur-sm p-3 rounded transition-colors">
              <div class="flex justify-between items-start">
                <div>
                  <a
                    href={`https://www.imdb.com/title/${movie.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-gray-600 hover:text-blue-600"
                  >
                    <h3 class="font-medium">{movie.title}</h3>
                  </a>
                  <p class="text-sm text-gray-600">{movie.year}</p>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>