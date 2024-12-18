<script lang="ts">
    import MovieSearch from '../../components/MovieSearch.svelte';
    import MovieCard from '../../components/MovieCard.svelte';
    import RatedMovieList from '../../components/RatedMovieList.svelte';
    import ResetRatings from '../../components/ResetRatings.svelte';
    import { movies } from '$lib/movieStore';
	import ParametersPanel from '../../components/ParametersPanel.svelte';
	import { isLoading, algorithmParams, recommendations, selectedAlgorithm, type AlgorithmParams } from '$lib/recommendationStore';
	import RecommendedMovieList from '../../components/RecommendedMovieList.svelte';

  let showParams: boolean = false;

  let error: string | null = "";

  async function generateRecommendations() {
      console.log($selectedAlgorithm);
      console.log($algorithmParams);
        $isLoading = true;
        error = null;
        try {
          
            await recommendations.generateRecommendations(
                $selectedAlgorithm, 
                $algorithmParams[$selectedAlgorithm]
            );
        } catch (e) {
          console.log(e);
            error = "Failed to generate recommendations";
        } finally {
            $isLoading = false;
        }
    }

    $: unratedMovies = $movies.filter(movie => movie.rating === 0);
  </script>
  
  <main class="container mx-auto p-4 border border-gray-300 p-4 rounded">
    <div class="flex justify-between items-center mb-6 ">
      <h1 class="text-3xl font-bold">Movie Ratings</h1>
    </div>
    
    <MovieSearch onRecommend={generateRecommendations} onParameter={() => showParams = (!showParams)}/>
    
    <div class="flex gap-6 mt-6">
      <!-- Left column - Rated Movies -->
      <div class="flex-1">
        <RatedMovieList />
      </div>
  
      <!-- Center column - Movie Cards -->
      <div class="flex-3">
        <div class="grid gap-4">
          {#each unratedMovies as movie (movie.id)}
            <MovieCard {movie} />
          {/each}
        </div>
      </div>

      <div class="flex-2">
        <div class="grid gap-4">
          {#if error}
            <div class="text-red-500 text-sm mt-4">{error}</div>
        {/if}
    
          <RecommendedMovieList></RecommendedMovieList>
          </div>
      </div>
  
      <!-- Right column - Recommendations -->
      <div class="flex-none">
        {#if showParams}
          <ParametersPanel
            onClose={() => showParams = false}
          />
        {/if}
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