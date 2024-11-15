<script lang="ts">
    import StarRating from './StarRating.svelte';
    import { movies } from '$lib/movieStore';
    import type { Movie } from '../types/movie';
    
    export let movie: Movie;
  
    function getRecommendations(currentMovie: Movie): Movie[] {
      return $movies.filter((m) => 
        m.id !== currentMovie.id && 
        (m.genre.includes(currentMovie.genre) || m.year === currentMovie.year)
      ).slice(0, 3);
    }
  
    $: recommendations = getRecommendations(movie);
  </script>
  
  <div class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow duration-200">
    <div class="flex gap-4">
      {#if movie.poster && movie.poster !== "N/A"}
        <img
          src={movie.poster}
          alt={`${movie.title} poster`}
          class="w-32 h-48 object-cover rounded shadow-sm hover:scale-105 transition-transform duration-200"
          loading="lazy"
        />
      {:else}
        <div class="w-32 h-48 bg-gray-200 rounded flex items-center justify-center">
          <span class="text-gray-400">No poster</span>
        </div>
      {/if}
      
      <div class="flex-1">
        <h2 class="text-xl font-semibold">{movie.title}</h2>
        <p class="text-gray-600">{movie.year}</p>
        <p class="text-sm text-gray-500 mt-1">{movie.genre}</p>
        {#if movie.imdbRating !== "N/A"}
          <p class="text-sm text-yellow-600 mt-1">IMDB: ⭐ {movie.imdbRating}</p>
        {/if}
        <p class="text-sm text-gray-600 mt-2 line-clamp-3">{movie.plot}</p>
        
        <div class="mt-4">
          <StarRating 
            movieId={movie.id} 
            rating={movie.rating}
          />
        </div>
  
        {#if movie.rating > 0 && recommendations.length > 0}
          <div class="mt-4">
            <h3 class="font-medium mb-2">Recommended:</h3>
            <ul class="text-sm text-gray-600">
              {#each recommendations as rec}
                <li>{rec.title} ({rec.year})</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    </div>
  </div>