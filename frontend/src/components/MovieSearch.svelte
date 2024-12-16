<!-- MovieSearch.svelte -->
<script lang="ts">
  import { movies } from '../lib/movieStore';
  import { searchMovies } from '../lib/api/imdb';
  import type { Movie } from '../types/movie';
	import { onDestroy } from 'svelte';
  
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

    console.log(ratedMovies);
    
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
  $: if (searchTerm !== previousSearchTerm) {
    if (searchTerm) {
      debounceSearch();
    } else {
      clearTimeout(searchTimeout);
      handleSearch(); // Will reset to all movies when empty
    }
  }

  // Cleanup on component destroy
  onDestroy(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
  });
</script>

<div class="search-container mb-6 relative">
  <input
    type="text"
    bind:value={searchTerm}
    placeholder="Search movies... (type at least 2 characters)"
    class="w-full p-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  />
  {#if isSearching}
    <div class="absolute right-2 top-2">
      <div class="w-6 h-6 border-t-2 border-blue-500 rounded-full animate-spin"></div>
    </div>
  {/if}
</div>

{#if searchError}
  <div class="text-red-500 mb-4">{searchError}</div>
{/if}