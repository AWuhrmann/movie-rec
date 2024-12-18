<!-- ContentZoom.svelte -->
<script>
  import { onMount } from 'svelte';
  
  let mainContent;
  let scrollY;
  let windowHeight;
  let scale = 0.3;
  
  const maxScale = 1;
  const initialScale = 0.3;
  const scrollDistance = 1000;
  
  onMount(() => {
    windowHeight = window.innerHeight;
    
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  });
  
  function handleScroll() {
    scrollY = window.scrollY;
    
    if (scrollY <= scrollDistance) {
      scale = initialScale + (maxScale - initialScale) * (scrollY / scrollDistance);
    } else {
      scale = maxScale;
    }
  }

  $: isFullyZoomed = scrollY > scrollDistance;
</script>

<style>
  .container {
    /* Much taller to allow for content scrolling */
    min-height: 400vh;
    background: #f5f5f5;
  }
  
  .zoom-wrapper {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    pointer-events: none; /* Allows scrolling through when fixed */
  }
  
  .content {
    width: 90%;
    max-width: 1200px;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transform-origin: center center;
    transition: transform 0.1s ease-out;
  }
  
  .scroll-section {
    position: absolute;
    top: 100vh; /* Start after first viewport */
    left: 0;
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 2rem;
  }

  .card {
    background: #f0f0f0;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin: 2rem 0;
  }
</style>

<div class="container">
  <!-- Zoom effect section -->
  <div class="zoom-wrapper" style="opacity: {isFullyZoomed ? 0 : 1}">
    <div class="content" style="transform: scale({scale})">
      <!-- Initial view content -->
      <h1>Welcome to My Website</h1>
      <p class="card">Start scrolling to zoom in and explore more content!</p>
    </div>
  </div>
  
  <!-- Scrollable content -->
  <div class="scroll-section">
    <div class="content" style="opacity: {isFullyZoomed ? 1 : 0}">
      <h1>Welcome to My Website</h1>
      
      <p class="card">Start scrolling to zoom in and explore more content!</p>
      
      <h2>Featured Sections</h2>
      <div class="grid">
        <div class="card">
          <h3>Section 1</h3>
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p>
        </div>
        <div class="card">
          <h3>Section 2</h3>
          <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.</p>
        </div>
      </div>
      
      <h2>More Content</h2>
      <div class="card">
        <h3>Deep Dive</h3>
        <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
        <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
      </div>
      
      <h2>Additional Sections</h2>
      <div class="grid">
        <div class="card">
          <h3>Section 3</h3>
          <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.</p>
        </div>
        <div class="card">
          <h3>Section 4</h3>
          <p>Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur.</p>
        </div>
      </div>
      
      <h2>Final Thoughts</h2>
      <div class="card">
        <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum.</p>
        <p>Deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.</p>
      </div>
    </div>
  </div>
</div>