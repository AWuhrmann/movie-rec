<!-- MovieSearch.svelte -->
<script lang="ts">
  import { movies } from '../lib/movieStore';
  import { searchMovies } from '../lib/api/imdb';
  import type { Movie } from '../types/movie';
	import { onDestroy } from 'svelte';
  import { Search, Settings, Trash } from 'lucide-svelte';
	import { isLoading } from '$lib/recommendationStore';
  
  let searchTerm = '';
  let previousSearchTerm = ''; // Track previous search to avoid duplicate calls
  let allMovies: Movie[] = [];
  let isSearching = false;
  let searchError = '';
  let ratedMovies: Movie[] = [];
  let searchTimeout: ReturnType<typeof setTimeout>;

  movies.subscribe((value: Movie[]) => {
    if (!searchTerm) {
      allMovies = value;
    }
    ratedMovies = value.filter(movie => movie.rating > 0);
  });

  async function handleSearch() {
    const trimmedSearch = searchTerm.trim();

    console.log(movies);
    
    // Don't search if:
    // 1. Empty search term (reset to all movies instead)
    // 2. Search term hasn't changed
    // 3. Search term is less than 2 characters
    if (!trimmedSearch) {
      const combinedResults = [
        // ...ratedMovies,
        ...allMovies.filter(movie => !ratedMovies.some(rated => rated.id === movie.id))
      ];
      movies.set(combinedResults);
      previousSearchTerm = '';
      return;
    }

    if (trimmedSearch === previousSearchTerm || trimmedSearch.length < 2) {
      return;
    }

    isSearching = true;
    searchError = '';
    
    try {
      const results = await searchMovies(trimmedSearch);
      if (results.length === 0) {
        searchError = 'No movies found';
      }
      
      const combinedResults = [
        //...ratedMovies,
        ...results.filter(movie => !ratedMovies.some(rated => rated.id === movie.id))
      ];
      
      movies.set(combinedResults);
      previousSearchTerm = trimmedSearch;
    } catch (error) {
      console.error('Error searching movies:', error);
      searchError = 'Error searching movies';
    } finally {
      isSearching = false;
    }
  }

  function debounceSearch() {
    clearTimeout(searchTimeout);
    // Increased debounce time to 500ms
    searchTimeout = setTimeout(handleSearch, 500);
  }

  // Use $: to watch searchTerm changes
  // $: if (searchTerm !== previousSearchTerm) {
  //   if (searchTerm) {
  //     debounceSearch();
  //   } else {
  //     clearTimeout(searchTimeout);
  //     handleSearch(); // Will reset to all movies when empty
  //   }
  // }

  // Cleanup on component destroy
  onDestroy(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
  });

  export let onParameter: () => void;
  export let onRecommend: () => void;
</script>


<div class="flex gap-2">
  <div class="flex-1">
    <input
    bind:value={searchTerm}
      type="text"
      placeholder="Search movies..."
      class="w-full p-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    />
  </div>
  
  <button 
    on:click={handleSearch}
    disabled={isSearching}
    class="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-600 text-white px-6 py-2 rounded-lg flex items-center gap-2"
  >
  {#if isSearching}
    Searching...
    {:else}
    <Search size={20} />
    Search
    {/if}  
  </button>
  
  <button 
  on:click={onRecommend}
    class="bg-green-500 hover:bg-green-600 disabled:bg-green-600 text-white px-6 py-2 rounded-lg"
    disabled={$isLoading}
  >
    {#if $isLoading}
    Loading...
    {:else}
    Recommended
    {/if}
  </button>
  
  <button
    on:click={onParameter}
    class="p-2 rounded-lg"
  >
    <Settings size={24} class="text-gray-400 hover:text-gray-600 transition-colors" />
  </button>
</div>