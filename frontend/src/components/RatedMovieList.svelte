<!-- RatedMovieList.svelte -->
<script lang="ts">
    import { movies, getLocalStorage } from '$lib/movieStore';
    import StarRating from './StarRating.svelte';
    import type { Movie } from '../types/movie';
	import { onMount } from 'svelte';
  import { Trash2, X } from 'lucide-svelte';
  
    $: ratedMovies = $movies.filter(movie => movie.rating > 0);
  
    function handleRemove(movieId: string) {
      movies.removeRating(movieId);
    }

    onMount(() => {
      getLocalStorage();
      movies.set([]);
    });

  </script>
  
  <div class="w-64 p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Rated Movies</h2>
      <button 
      on:click={() => {ratedMovies = []}}
      class="text-gray-400 hover:text-red-500 transition-colors"
      aria-label="Clear rated movies"
      >
      <Trash2 size={20} />
    </button>
  </div>
    {#if ratedMovies.length === 0}
      <p class="text-gray-500">No rated movies yet</p>
    {:else}
      <div class="space-y-1">
        {#each ratedMovies as movie (movie.id)}
        <div class="rounded relative overflow-hidden group transition-shadow duration-200" style="min-height: 120px;">
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
                <div class="mt-0">
                  <StarRating movieId={movie.id} rating={movie.rating} />
                </div>
              </div>
              
              <button
                on:click={() => handleRemove(movie.id)}
                class="text-red-500 hover:text-red-700 transition-colors"
                aria-label="Remove rating"
              >
                <X size={24} class="text-gray-600" />
              </button>
            </div>
          </div>
        </div>
        {/each}
      </div>
    {/if}
  </div>