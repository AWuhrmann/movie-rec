<script lang="ts">
    import MovieSearch from './components/MovieSearch.svelte';
    import MovieCard from './components/MovieCard.svelte';
    import { movies } from './lib/movieStore';
    import type { Movie } from './types/movie';
  </script>
  
  <main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Movie Ratings</h1>
    <MovieSearch />
    <div class="grid gap-4">
      {#each $movies as movie (movie.id)}
        <MovieCard {movie} />
      {/each}
    </div>
  </main>
  
  <style>
    :global(body) {
      @apply bg-gray-50 m-0 p-0;
    }
    .container {
      @apply max-w-3xl;
    }
  </style>