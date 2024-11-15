<script lang="ts">
    import { movies } from '$lib/movieStore';
  
    let showConfirmation = false;
  
    function handleReset() {
      showConfirmation = true;
    }
  
    function confirmReset() {
      movies.resetAllRatings();
      showConfirmation = false;
    }
  
    function cancelReset() {
      showConfirmation = false;
    }
  </script>
  
  <div class="relative">
    {#if !showConfirmation}
      <button
        on:click={handleReset}
        class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors duration-200"
        type="button"
      >
        Reset All Ratings
      </button>
    {:else}
      <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-lg">
        <p class="text-gray-700 mb-4">Are you sure you want to reset all ratings?</p>
        <div class="flex gap-2">
          <button
            on:click={confirmReset}
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors duration-200"
            type="button"
          >
            Yes, Reset
          </button>
          <button
            on:click={cancelReset}
            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors duration-200"
            type="button"
          >
            Cancel
          </button>
        </div>
      </div>
    {/if}
  </div>