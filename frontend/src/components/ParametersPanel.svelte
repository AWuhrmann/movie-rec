<!-- Recommendations.svelte -->
<script lang="ts">
    import type { AlgorithmParams } from '$lib/recommendationStore';
    import { selectedAlgorithm, algorithmParams } from '$lib/recommendationStore';
	import { Trash2 } from 'lucide-svelte';
	import { onMount } from 'svelte';
    
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
            }
        },
    ];
  
    const defaultFixedReturns = 5;
    export let onClose: () => void;

    // Close on escape key
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      onClose();
    }
  }
    
  onMount(() => {
      $algorithmParams = {
          knn_item: algorithms[0].defaultParams,
          knn_user: algorithms[1].defaultParams,
          content_based: algorithms[2].defaultParams,
          svd: algorithms[3].defaultParams,
          fixedReturns: defaultFixedReturns
      };
  });
    
    function calculateEstimatedTime(): string {
        // These are example calculations - adjust based on your actual algorithm performance
        const baseTime = {
            knn_item: 2,    // base 2 seconds
            knn_user: 3,    // base 3 seconds
            content_based: 1, // base 1 second
            svd: 5          // base 5 seconds
        };
    
        let multiplier = 1;
        
        switch(selectedAlgorithm) {
            case 'knn_item':
                multiplier = $algorithmParams.knn_item.k * 0.1;
                break;
            case 'knn_user':
                multiplier = $algorithmParams.knn_user.k * 0.15;
                break;
            case 'content_based':
                multiplier = 1 / $algorithmParams.content_based.minSimilarity;
                break;
            case 'svd':
                multiplier = ($algorithmParams.svd.factors * algorithmParams.svd.epochs) / 1000;
                break;
        }
    
        const estimatedSeconds = baseTime[$selectedAlgorithm] * multiplier;
        return estimatedSeconds.toFixed(1);
    }
    
    $: estimatedTime = calculateEstimatedTime();
    
    function updateParams(paramKey: string, value: any) {
        $algorithmParams[$selectedAlgorithm][paramKey] = value;
    }
</script>
    
<!-- Backdrop -->
<div 
  class="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center"
  on:click={onClose}
>
  <!-- Modal -->
  <div 
    class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4 z-50"
    on:click|stopPropagation
  >
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Recommendation Parameters</h2>
      <button
        on:click={onClose}
        class="text-gray-400 hover:text-gray-600 text-2xl"
        aria-label="Close parameters panel"
      >
        ×
      </button>
    </div>
                
        <div class="space-y-4">
    
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
                  bind:value={$algorithmParams[$selectedAlgorithm].k}
                  class="w-1/2 p-2 border rounded"
                  min="1"
                  max="100"
                  />
                  <span class="pl-2 text-sm text-gray-600 pt-2">Neighbors (1-100)</span>
  
                  <input 
                  type="number" 
                  bind:value={$algorithmParams[$selectedAlgorithm].minCommonItems}
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
                  bind:value={$algorithmParams[$selectedAlgorithm].k}
                  class="w-1/2 p-2 border rounded"
                  min="1"
                  max="100"
                  />
                  <span class="pl-2 text-sm text-gray-600 pt-2">Neighbors (1-100)</span>
  
                  <input 
                  type="number" 
                  bind:value={$algorithmParams[$selectedAlgorithm].moviesToConsider}
                  class="w-1/4 p-2 border rounded"
                  min="0"
                  max="1"
                  step="0.1"
                  />
                  <span class="pl-2 text-sm text-gray-600 pt-2">Number of movies to consider</span>
  
                  <input 
                  type="number" 
                  bind:value={$algorithmParams[$selectedAlgorithm].minCommonUsers}
                  class="w-1/4 p-2 border rounded"
                  min="0"
                  max="{$algorithmParams[$selectedAlgorithm].k}"
                  step="0.1"
                  />
                  <span class="pl-2 text-sm text-gray-600 pt-2">For these movies, how many users ?</span>
  
                  
                </div>
            {/if}
    
            
  
            {#if $selectedAlgorithm === 'content_based'}
                <div class="space-y-2">
                  
                  <input 
                      type="number" 
                      bind:value={$algorithmParams[$selectedAlgorithm].minSimilarity}
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
                        bind:value={$algorithmParams.fixedReturns}
                        class="w-full p-2 border rounded"
                        min="1"
                        max="100"
                    />
        </div>
    
        <div class="text-sm text-gray-600 mb-4 flex justify-between items-center">
            Estimated processing time: {estimatedTime} seconds
            <button 
      on:click={onClose}
        class="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-600 text-white px-6 py-2 rounded-lg flex items-center gap-2"
        aria-label="Clear recommendations"
      >
        Save
      </button>
        </div>
    
    </div>
    </div>
    </div>