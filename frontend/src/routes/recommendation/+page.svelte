<script lang="ts">
    import MovieSearch from '../../components/MovieSearch.svelte';
    import MovieCard from '../../components/MovieCard.svelte';
    import RatedMovieList from '../../components/RatedMovieList.svelte';
    import Recommendations from '../../components/Recommendations.svelte';
    import ResetRatings from '../../components/ResetRatings.svelte';
    import { movies } from '$lib/movieStore';
  
    $: unratedMovies = $movies.filter(movie => movie.rating === 0);
  </script>
  
  <main class="container mx-auto p-4 border border-gray-300 p-4 rounded">
    <div class="flex justify-between items-center mb-6 ">
      <h1 class="text-3xl font-bold">Movie Ratings</h1>
      <ResetRatings />
    </div>
    
    <MovieSearch />
    
    <div class="flex gap-6 mt-6">
      <!-- Left column - Rated Movies -->
      <div class="flex-none">
        <RatedMovieList />
      </div>
  
      <!-- Center column - Movie Cards -->
      <div class="flex-1">
        <div class="grid gap-4">
          {#each unratedMovies as movie (movie.id)}
            <MovieCard {movie} />
          {/each}
        </div>
      </div>
  
      <!-- Right column - Recommendations -->
      <div class="flex-none">
        <Recommendations />
      </div>
    </div>
  </main>
  
  <style>
    :global(body) {
      @apply bg-gray-50 m-0 p-0;
    }
    .container {
      @apply max-w-7xl;
    }
  </style>