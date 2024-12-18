<!-- Recommendations.svelte -->
<script lang="ts">
  import { recommendations } from '$lib/recommendationStore';
  import type { AlgorithmParams } from '$lib/recommendationStore';
  import { selectedAlgorithm } from '$lib/recommendationStore';

  let isLoading = false;
  let error: string | null = null;
  let estimatedTime = '0';
  
  const algorithms = [
      { 
          id: 'knn_item', 
          name: 'kNN, item based',
          defaultParams: {
              k: 10,
              minCommonItems: 5
          }
      },
      { 
          id: 'knn_user', 
          name: 'kNN, user based',
          defaultParams: {
              k: 100,
              minCommonUsers: 30,
              moviesToConsider: 100
          }
      },
      { 
          id: 'content_based', 
          name: 'Content Based',
          defaultParams: {
              minSimilarity: 0.5
          }
      },
      { 
          id: 'svd', 
          name: 'SVD',
          defaultParams: {
              factors: 100,
              epochs: 20,
              learningRate: 0.005
          }
      },
  ];

  const defaultFixedReturns = 5;
  
  let algorithmParams: AlgorithmParams = {
      knn_item: algorithms[0].defaultParams,
      knn_user: algorithms[1].defaultParams,
      content_based: algorithms[2].defaultParams,
      svd: algorithms[3].defaultParams,
      fixedReturns: defaultFixedReturns
  };
  
  function calculateEstimatedTime(): string {
      // These are example calculations - adjust based on your actual algorithm performance
      const baseTime = {
          knn_item: 2,    // base 2 seconds
          knn_user: 3,    // base 3 seconds
          content_based: 1, // base 1 second
          svd: 5          // base 5 seconds
      };
  
      let multiplier = 1;
      
      switch($selectedAlgorithm) {
          case 'knn_item':
              multiplier = algorithmParams.knn_item.k * 0.1;
              break;
          case 'knn_user':
              multiplier = algorithmParams.knn_user.k * 0.15;
              break;
          case 'content_based':
              multiplier = 1 / algorithmParams.content_based.minSimilarity;
              break;
          case 'svd':
              multiplier = (algorithmParams.svd.factors * algorithmParams.svd.epochs) / 1000;
              break;
      }
  
      const estimatedSeconds = baseTime[$selectedAlgorithm] * multiplier;
      return estimatedSeconds.toFixed(1);
  }
  
  $: estimatedTime = calculateEstimatedTime();
  
  export async function generateRecommendations() {
      isLoading = true;
      error = null;
      try {
        const alg = $selectedAlgorithm;
          await recommendations.generateRecommendations(
              $selectedAlgorithm, 
              algorithmParams[alg]
          );
      } catch (e) {
          error = "Failed to generate recommendations";
      } finally {
          isLoading = false;
      }
  }
  
  function updateParams(paramKey: string, value: any) {
    const alg: string = $selectedAlgorithm;  
    algorithmParams[alg][paramKey] = value;
      algorithmParams = algorithmParams; // trigger reactivity
  }
  </script>
  
  <div class="w-96 bg-white rounded-lg shadow-md p-4">
      <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Recommendations</h2>
      </div>
  
      <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
          <select 
              bind:value={$selectedAlgorithm} 
              class="w-full p-2 border rounded"
          >
              {#each algorithms as algo}
                  <option value={algo.id}>{algo.name}</option>
              {/each}
          </select>
      </div>
  
      <!-- Dynamic Parameters Based on Selected Algorithm -->
      <div class="mb-4 space-y-3">

          {#if $selectedAlgorithm !== 'svd'}
          <h3 class="font-medium text-sm text-gray-700">Parameters</h3>
          {/if}

          
          {#if $selectedAlgorithm === 'knn_item'}
              <div class="space-y-2">

                <input 
                type="number" 
                bind:value={algorithmParams[$selectedAlgorithm].k}
                class="w-1/2 p-2 border rounded"
                min="1"
                max="100"
                />
                <span class="pl-2 text-sm text-gray-600 pt-2">Neighbors (1-100)</span>

                <input 
                type="number" 
                bind:value={algorithmParams[$selectedAlgorithm].minCommonItems}
                class="w-1/2 p-2 border rounded"
                min="0"
                max="1"
                step="0.1"
                />
                <span class="pl-2 text-sm text-gray-600 pt-2">Minimum common items</span>

                
              </div>
          {/if}

          {#if $selectedAlgorithm === 'knn_user'}
              <div class="space-y-2">

                <input 
                type="number" 
                bind:value={algorithmParams[$selectedAlgorithm].k}
                class="w-1/2 p-2 border rounded"
                min="1"
                max="100"
                />
                <span class="pl-2 text-sm text-gray-600 pt-2">Neighbors (1-100)</span>

                <input 
                type="number" 
                bind:value={algorithmParams[$selectedAlgorithm].moviesToConsider}
                class="w-1/4 p-2 border rounded"
                min="0"
                max="1"
                step="0.1"
                />
                <span class="pl-2 text-sm text-gray-600 pt-2">Number of movies to consider</span>

                <input 
                type="number" 
                bind:value={algorithmParams[$selectedAlgorithm].minCommonUsers}
                class="w-1/4 p-2 border rounded"
                min="0"
                max="{algorithmParams[$selectedAlgorithm].k}"
                step="0.1"
                />
                <span class="pl-2 text-sm text-gray-600 pt-2">For these movies, how many users ?</span>

                
              </div>
          {/if}
  
          

          {#if $selectedAlgorithm === 'content_based'}
              <div class="space-y-2">
                
                <input 
                    type="number" 
                    bind:value={algorithmParams[$selectedAlgorithm].minSimilarity}
                    class="w-1/4 p-2 border rounded"
                    min="0"
                    max="1"
                    step="0.1"
                />
                <span class="text-sm text-gray-600 pt-2">Minimum similarity (0 to ignore)</span>
              </div>
          {/if}
  
          {#if $selectedAlgorithm === 'svd'}

          {/if}
          <h3 class="font-medium text-sm text-gray-700">Movies to return (n)</h3>

                  <input 
                      type="number" 
                      bind:value={algorithmParams[$selectedAlgorithm].fixedReturns}
                      class="w-full p-2 border rounded"
                      min="1"
                      max="100"
                  />
      </div>
  
      <div class="text-sm text-gray-600 mb-4">
          Estimated processing time: {estimatedTime} seconds
      </div>
  
      <button
          on:click={generateRecommendations}
          class="w-full bg-blue-500 text-white p-2 rounded disabled:opacity-50"
          disabled={isLoading}
      >
          {isLoading ? 'Generating...' : 'Generate Recommendations'}
      </button>
  
      {#if error}
          <div class="text-red-500 text-sm mt-4">{error}</div>
      {/if}
  
      {#if isLoading}
          <div class="space-y-4 mt-4">
              {#each Array(3) as _}
                  <div class="p-2 bg-gray-50 rounded animate-pulse">
                      <div class="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                      <div class="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
              {/each}
          </div>
      {:else if $recommendations.length === 0}
          <p class="text-gray-500 mt-4">Click generate to see recommendations</p>
      {:else}
          <div class="space-y-4 mt-4">
            {#each $recommendations as movie (movie.id)}
                <div class="p-2 bg-gray-50 rounded">
                    <a 
                        href={`https://www.imdb.com/title/${movie.id}`} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        class="hover:text-blue-600"
                    >
                        <h3 class="font-medium">{movie.title}</h3>
                        <p class="text-sm text-gray-600">{movie.year}</p>
                    </a>
                </div>
            {/each}
          </div>
      {/if}
  </div>