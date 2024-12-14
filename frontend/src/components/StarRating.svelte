<script lang="ts">
  import { movies } from '$lib/movieStore';
  
  export let movieId: string;
  export let rating: number;
  
  let hoverRating: number | null = null;
  let isHalfHover = false;
  
  function handleRating(value: number): void {
      movies.updateRating(movieId, value);
  }
  
  function handleStarClick(event: MouseEvent, i: number): void {
      const button = event.currentTarget as HTMLButtonElement;
      const rect = button.getBoundingClientRect();
      const x = event.clientX - rect.left;
      
      const isHalfStar = x < rect.width / 2;
      const value = i + 1 - (isHalfStar ? 0.5 : 0);
      
      handleRating(value);
  }
  
  function handleStarHover(event: MouseEvent, i: number): void {
      const button = event.currentTarget as HTMLButtonElement;
      const rect = button.getBoundingClientRect();
      const x = event.clientX - rect.left;
      
      isHalfHover = x < rect.width / 2;
      hoverRating = i + 1;
  }
  
  function handleMouseLeave(): void {
      hoverRating = null;
      isHalfHover = false;
  }
  </script>
  
  <div 
      class="flex gap-1" 
      on:mouseleave={handleMouseLeave}
      role="group"
      aria-label="Star rating"
  >
      {#each Array(5) as _, i}
          <button
              on:click={(e) => handleStarClick(e, i)}
              on:mousemove={(e) => handleStarHover(e, i)}
              class="text-2xl hover:scale-110 transition-transform focus:outline-none focus:ring-2 focus:ring-yellow-400 rounded relative"
              type="button"
              aria-label="Rate {i + 1} stars"
          >
              {#if hoverRating !== null}
                  {#if i < hoverRating - 1}
                      <span class="text-yellow-200">★</span>
                  {:else if i === hoverRating - 1}
                      {#if isHalfHover}
                          <span class="relative">
                              <span class="absolute text-yellow-200 overflow-hidden" style="width: 50%">★</span>
                              <span class="text-gray-300">☆</span>
                          </span>
                      {:else}
                          <span class="text-yellow-200">★</span>
                      {/if}
                  {:else}
                      <span class="text-gray-300">☆</span>
                  {/if}
              {:else}
                  {#if i < Math.floor(rating)}
                      <span class="text-yellow-400">★</span>
                  {:else if i === Math.floor(rating) && rating % 1 !== 0}
                      <span class="relative">
                          <span class="absolute text-yellow-400 overflow-hidden" style="width: 50%">★</span>
                          <span class="text-gray-300">☆</span>
                      </span>
                  {:else}
                      <span class="text-gray-300">☆</span>
                  {/if}
              {/if}
          </button>
      {/each}
  </div>