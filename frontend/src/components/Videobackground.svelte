<script lang="ts">
  import { onMount } from 'svelte';

  const movieData = {
    "Inception": ["The Matrix", "Memento", "Interstellar"],
    "Toy Story": ["Finding Nemo", "Monsters Inc", "WALL-E"],
    "The Intouchables": ["The Green Book", "Life is Beautiful", "A Beautiful Mind"]
  };

  const moviePaths = {
    "Inception": "/images/matrix.mp4",
    "Toy Story": "/images/how-train-dragon.mp4",
    "The Intouchables": "/images/life-is-beautiful.mp4"
  };

  let videoElement: HTMLVideoElement;
  let videoSource = '/images/matrix.mp4'; // Default video
  let typewriterText = '';
  let recommendationText = '';
  let selectedMovie = '';
  let recommendations = [];
  let currentRecommendationIndex = 0;
  let isTyping = false;
  let scrollProgress = 0;
  let currentAnimation = null;
  let currentAnimationRec = null;

  onMount(() => {
    const handleScroll = () => {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      scrollProgress = Math.min(Math.max(window.scrollY / (window.innerHeight), 0), 1);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });

let typewriterAnimation = null;
let recommendationAnimation = null;

async function typeWriter(movie) {
  // Cancel any ongoing animations
  if (typewriterAnimation) {
    clearTimeout(typewriterAnimation);
  }
  if (recommendationAnimation) {
    clearTimeout(recommendationAnimation);
  }
  
  // Reset states
  isTyping = true;
  typewriterText = '';
  recommendationText = '';
  
  // Type the movie name
  for (let i = 0; i <= movie.length; i++) {
    await new Promise(resolve => {
      typewriterAnimation = setTimeout(() => {
        typewriterText = movie.substring(0, i);
        resolve();
      }, 100);
    });
  }
  
  // Update movie selection and start recommendations
  selectedMovie = movie;
  recommendations = movieData[movie];
  currentRecommendationIndex = 0;
  isTyping = false;
  
  // Start recommendation animation after a small delay
  setTimeout(() => {
    typeRecommendation();
  }, 500);
}

async function typeRecommendation() {
  if (!recommendations.length) return;
  
  // Clear any ongoing recommendation animation
  if (recommendationAnimation) {
    clearTimeout(recommendationAnimation);
  }
  
  recommendationText = '';
  const currentMovie = recommendations[currentRecommendationIndex];
  
  // Type in the recommendation
  for (let i = 0; i <= currentMovie.length; i++) {
    await new Promise(resolve => {
      recommendationAnimation = setTimeout(() => {
        recommendationText = currentMovie.substring(0, i);
        resolve();
      }, 100);
    });
  }
  
  // Wait before starting to delete
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Delete the recommendation
  for (let i = currentMovie.length; i >= 0; i--) {
    await new Promise(resolve => {
      recommendationAnimation = setTimeout(() => {
        recommendationText = currentMovie.substring(0, i);
        resolve();
      }, 50);
    });
  }
  
  // Move to next recommendation after a small delay
  setTimeout(() => {
    currentRecommendationIndex = (currentRecommendationIndex + 1) % recommendations.length;
    typeRecommendation();
  }, 500);
}

function selectMovie(movie: string) {
  // Cancel any ongoing animations first
  if (typewriterAnimation) {
    clearTimeout(typewriterAnimation);
  }
  if (recommendationAnimation) {
    clearTimeout(recommendationAnimation);
  }
  
  // Update video
  const newVideoSource = moviePaths[movie];
  if (newVideoSource && videoElement) {
    videoSource = newVideoSource;
    videoElement.load();
    videoElement.play();
  }
  
  // Start new typing animation
  typeWriter(movie);
}
</script>

<div class="sticky-container">
  <div class="video-section" style="opacity: {1 - scrollProgress}">
    <video
      bind:this={videoElement}
      class="background-video"
      autoplay
      loop
      muted
      playsinline
    >
      <source src={videoSource} type="video/mp4" />
    </video>
    
    <div class="vignette"></div>

    <div class="content">
      <div class="movie-section">
        <div class="top-content">
          <div class="typewriter-container">
            <span class="typewriter-prefix">I liked</span>
            <span class="typewriter-text">{typewriterText}</span>
          </div>
          <div class="movie-options">
            {#each Object.keys(movieData) as movie}
              <button 
                class="movie-button" 
                on:click={() => selectMovie(movie)}
              >
                {movie}
              </button>
            {/each}
          </div>
        </div>
        
        {#if selectedMovie && recommendations.length > 0}
          <div class="recommendations">
            <span class="static-text">Have you watched </span>
            <span class="recommendation-text">{recommendationText}</span>
            <span class="static-text">?</span>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
    .sticky-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.video-section {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.background-video {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translateX(-50%) translateY(-50%);
  filter: blur(5px);
}

.vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle,
    transparent 30%,
    rgba(0, 0, 0, 0.9) 70%
  );
}

.content {
  position: relative;
  z-index: 10;  /* Increased z-index to ensure content is above overlays */
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.3);
  pointer-events: all;  /* Ensure clicks work */
}

.movie-section {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4rem;
  width: 100%;
}

.top-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.movie-options {
  display: flex;
  gap: 1rem;
  margin-left: 2rem;
}

.movie-button {
  padding: 0.5rem 1rem;
  border: 1px solid white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  background: transparent;
  color: white;
  position: relative;
  z-index: 15; /* Higher z-index to ensure buttons are clickable */
  pointer-events: auto; /* Explicitly enable pointer events */
}

.movie-button:hover {
  background-color: white;
  color: black;
}

.typewriter-container {
  display: flex;
  align-items: center;
}

.typewriter-prefix {
  font-size: 3.5rem;
  font-weight: 700;
  margin-right: 0.5rem;
  color: white;
}

.typewriter-text {
  font-size: 3.5rem;
  font-weight: 700;
  min-width: 2ch;
  border-right: 0.15em solid white;
  white-space: nowrap;
  overflow: hidden;
  animation: blink-caret 0.75s step-end infinite;
  color: white;
}

.recommendations {
  align-self: flex-end;
  padding-bottom: 15vh;
  font-size: 3.5rem;
  font-weight: 700;
  text-align: right;
  min-height: 4rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
}

.static-text {
  white-space: nowrap;
}

.recommendation-text {
  border-right: 0.15em solid white;
  white-space: nowrap;
  overflow: hidden;
  animation: blink-caret 0.75s step-end infinite;
  min-width: 1ch;
}
@keyframes blink-caret {
    from, to { border-color: transparent }
    50% { border-color: white }
  }
</style>