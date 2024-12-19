<script>
  import { onMount } from 'svelte';

  const movieData = {
    "Inception": ["The Matrix", "Memento", "Interstellar"],
    "Toy Story": ["Finding Nemo", "Monsters Inc", "WALL-E"],
    "The Intouchables": ["The Green Book", "Life is Beautiful", "A Beautiful Mind"]
  };

  const texts = [
    { type: 'static', text: "Second text appears" },
    { type: 'static', text: "Third text shows up" },
    { type: 'static', text: "Fourth text comes in" },
    { type: 'static', text: "Fifth text arrives" }
  ];

  let typewriterText = '...';
  let recommendationText = '';
  let selectedMovie = '';
  let recommendations = [];
  let currentRecommendationIndex = 0;
  let isTyping = false;

  // Typewriter effect for movie title
  async function typeWriter(movie) {
    if (isTyping) return;
    isTyping = true;
    typewriterText = '';
    
    for (let i = 0; i <= movie.length; i++) {
      typewriterText = movie.substring(0, i);
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    selectedMovie = movie;
    recommendations = movieData[movie];
    currentRecommendationIndex = 0;
    typeRecommendation();
    isTyping = false;
  }

  // Typewriter effect for recommendations
  async function typeRecommendation() {
    if (!recommendations.length) return;
    
    let movieText = '';
    const currentMovie = recommendations[currentRecommendationIndex];
    
    // Type the movie name
    for (let i = 0; i <= currentMovie.length; i++) {
      movieText = currentMovie.substring(0, i);
      recommendationText = movieText;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Wait before erasing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Erase only the movie name
    for (let i = currentMovie.length; i >= 0; i--) {
      movieText = currentMovie.substring(0, i);
      recommendationText = movieText;
      await new Promise(resolve => setTimeout(resolve, 30));
    }
    
    // Move to next recommendation
    currentRecommendationIndex = (currentRecommendationIndex + 1) % recommendations.length;
    typeRecommendation();
  }

  function selectMovie(movie) {
    typeWriter(movie);
  }

  let sections = [];

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const section = entry.target;
          if (entry.isIntersecting) {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
          } else {
            const direction = (section.getBoundingClientRect().top < 0) ? '-20px' : '20px';
            section.style.opacity = '0';
            section.style.transform = `translateY(${direction})`;
          }
        });
      },
      {
        root: null,
        rootMargin: '-20% 0px',
        threshold: 0.1
      }
    );

    sections = document.querySelectorAll('.scroll-section');
    sections.forEach(section => observer.observe(section));

    return () => {
      sections.forEach(section => observer.unobserve(section));
    };
  });
</script>

<style>
  /* Reset styles to prevent interference */
  :global(body),
  :global(html) {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }

  /* Reset any unwanted margins/paddings */
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  /* Main styles */
  .container {
    min-height: 100vh;
    padding: 10vh 0;
    position: relative;
    width: 100%;
    max-width: 100vw;
    margin: 0;
    overflow-x: hidden;
    background: white;  /* or any background you prefer */
    overflow-y: hidden;
  }

  .movie-section {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 4rem;
    padding-top: 0;
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
    border: 1px solid #333;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.2rem;
  }

  .movie-button:hover {
    background-color: #333;
    color: white;
  }

  .typewriter-container {
    display: flex;
    align-items: center;
  }

  .typewriter-prefix {
    font-size: 3.5rem;
    font-weight: 700;
    margin-right: 0.5rem;
  }

  .typewriter-text {
    font-size: 3.5rem;
    font-weight: 700;
    min-width: 2ch;
    border-right: 0.15em solid #333;
    white-space: nowrap;
    overflow: hidden;
    animation: blink-caret 0.75s step-end infinite;
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
  }

  .static-text {
    white-space: nowrap;
  }

  .recommendation-text {
    border-right: 0.15em solid #333;
    white-space: nowrap;
    overflow: hidden;
    animation: blink-caret 0.75s step-end infinite;
    min-width: 1ch;
  }

  .scroll-section {
    height: 50vh;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transform: translateY(20px);
    transition: 
      opacity 0.6s ease-out,
      transform 0.6s ease-out;
  }

  .text {
    font-size: 2rem;
    text-align: center;
    color: #333;
    padding: 1rem;
  }

  @keyframes blink-caret {
    from, to { border-color: transparent }
    50% { border-color: #333 }
  }
</style>

<div class="container">
  <!-- Movie recommendation section -->
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

  <!-- Scrolling sections -->
  {#each texts as section}
    <div class="scroll-section">
      <p class="text">{section.text}</p>
    </div>
  {/each}
</div>