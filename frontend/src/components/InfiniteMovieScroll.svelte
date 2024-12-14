<script lang="ts">
    import type { Movie } from '../types/movie';
    
    export let movies: Movie[] = [];
    export let direction: 'left' | 'right' = 'left';
    export let speed: number = 10; // seconds for one complete cycle
    export let itemWidth: number = 200; // width of each movie card
    export let itemHeight: number = 300; // height of each movie card
    
    let isHovered = false;
    
    // Calculate total width based on movies length
    $: totalWidth = movies.length * itemWidth;
    
    function handleMouseEnter() {
      isHovered = true;
    }
    
    function handleMouseLeave() {
      isHovered = false;
    }
  </script>
<div class="not-prose">
    
    <div 
    class="movie-scroll"
    class:reverse={direction === 'right'}
    on:mouseenter={handleMouseEnter}
    on:mouseleave={handleMouseLeave}
    style="--width: {itemWidth}px; --height: {itemHeight}px; --quantity: {movies.length};"
    >
    <div class="movie-list">
        {#each movies as movie, i}
        <div 
          class="movie-item"
          class:hovered={isHovered}
          style="--position: {i + 1}"
        >
        <div class="movie-card">
            {#if movie.poster && movie.poster !== "N/A"}
              <img
              src={movie.poster}
                alt={`${movie.title} poster`}
                class="movie-poster"
                loading="lazy"
              />
              {:else}
              <div class="movie-poster-placeholder">
                <span>No poster</span>
            </div>
            {/if}
            <div class="movie-info">
              <h3>{movie.title}</h3>
              <p>{movie.year}</p>
              {#if movie.imdbRating !== "N/A"}
              <div class="rating">⭐ {movie.imdbRating}</div>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>
  
  <style lang="postcss">
    .movie-scroll {
      width: 100%;
      height: var(--height);
      overflow: hidden;
    }
    
    .movie-list {
      display: flex;
      width: 100%;
      min-width: calc(var(--width) * var(--quantity));
      position: relative;
    }
    
    .movie-item {
      width: var(--width);
      height: var(--height);
      position: absolute;
      left: 100%;
      animation: autoRun 20s linear infinite;
      animation-delay: calc((20s / var(--quantity)) * (var(--position) - 1) - 20s) !important;
    }
    
    .movie-card {
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
      border-radius: 8px;
      transition: transform 0.3s ease;
    }
    
    .movie-scroll:hover .movie-item {
      animation-play-state: paused !important;
      filter: grayscale(1);
    }
    
    .movie-item:hover {
      filter: grayscale(0) !important;
    }
    
    .movie-item:hover .movie-card {
      transform: scale(1.05);
      z-index: 1;
    }
    
    .movie-poster {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .movie-poster-placeholder {
      width: 100%;
      height: 100%;
      background-color: theme(colors.gray.200);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .movie-info {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 1rem;
      background: linear-gradient(
        to bottom,
        transparent 0%,
        rgba(0, 0, 0, 0.7) 30%,
        rgba(0, 0, 0, 0.9) 100%
      );
      color: white;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    
    .movie-item:hover .movie-info {
      opacity: 1;
    }
    
    .movie-info h3 {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .movie-info p {
      margin: 0.25rem 0;
      font-size: 0.875rem;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .rating {
      font-size: 0.875rem;
      color: theme(colors.yellow.400);
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    @keyframes autoRun {
      from {
        left: 100%;
      }
      to {
        left: calc(var(--width) * -1);
      }
    }
    
    .movie-scroll.reverse .movie-item {
      animation-name: reversePlay;
    }
    
    @keyframes reversePlay {
      from {
        left: calc(var(--width) * -1);
      }
      to {
        left: 100%;
      }
    }
  </style>