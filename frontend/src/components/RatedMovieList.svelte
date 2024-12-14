<!-- RatedMovieList.svelte -->
<script lang="ts">
    import { movies, getLocalStorage } from '$lib/movieStore';
    import StarRating from './StarRating.svelte';
    import type { Movie } from '../types/movie';
	import { onMount } from 'svelte';
  
    $: ratedMovies = $movies.filter(movie => movie.rating > 0);
  
    function handleRemove(movieId: string) {
      movies.removeRating(movieId);
    }

    onMount(() => {
      getLocalStorage();
      movies.set([]);
    });

  </script>
  
  <div class="w-64 bg-white rounded-lg shadow-md p-4">
    <h2 class="text-xl font-semibold mb-4">Rated Movies</h2>
    
    {#if ratedMovies.length === 0}
      <p class="text-gray-500">No rated movies yet</p>
    {:else}
      <div class="space-y-4">
        {#each ratedMovies as movie (movie.id)}
          <div 
            class="p-2 rounded relative overflow-hidden group hover:shadow-lg transition-shadow duration-200"
            style="min-height: 120px;"
          >
            {#if movie.poster && movie.poster !== "N/A"}
              <div 
                class="absolute inset-0 bg-cover bg-center z-0"
                style="background-image: url('{movie.poster}'); opacity: 0.65;"
              ></div>
            {/if}
            <div class="relative z-10 bg-gray-50/80 backdrop-blur-sm p-3 rounded transition-colors group-hover:bg-gray-50/90">
              <div class="flex justify-between items-start">
                <h3 class="font-medium text-gray-900">{movie.title}</h3>
                <button
                  on:click={() => handleRemove(movie.id)}
                  class="text-red-500 hover:text-red-700 transition-colors"
                  aria-label="Remove rating"
                >
                  ×
                </button>
              </div>
              <p class="text-sm text-gray-600">{movie.year}</p>
              <div class="mt-2">
                <StarRating movieId={movie.id} rating={movie.rating} />
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>