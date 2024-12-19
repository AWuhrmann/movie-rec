<script>
    export let videoSource1 = '/path/to/video1.mp4';
    export let videoSource2 = '/path/to/video2.mp4';
    export let blurAmount = '5px';
    export let overlayOpacity = '0.3';
    export let transitionWidth = '100px';
    
    let container;
    let angle = 0;
    
    // Calculate the angle of the diagonal based on container dimensions
    function updateDiagonalAngle() {
      if (container) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        angle = Math.atan2(height, width) * (180 / Math.PI);
      }
    }
  </script>
  
  <div 
    class="video-container"
    bind:this={container}
    use:updateDiagonalAngle
    on:resize={updateDiagonalAngle}
  >
    <!-- Bottom-right video -->
    <div class="video-section bottom-right">
      <video 
        class="background-video" 
        autoplay 
        loop 
        muted 
        playsinline
      >
        <source src={videoSource1} type="video/mp4" />
      </video>
    </div>
  
    <!-- Top-left video -->
    <div class="video-section top-left">
      <video 
        class="background-video" 
        autoplay 
        loop 
        muted 
        playsinline
      >
        <source src={videoSource2} type="video/mp4" />
      </video>
    </div>
  
    <!-- Blur transition -->
    <div 
      class="blur-transition"
      style="--diagonal-angle: {angle}deg; --transition-width: {transitionWidth}"
    ></div>
    
    <div class="content">
      <slot>
        <h1>Your Content Here</h1>
        <p>Add any content you want to display over the split video background.</p>
      </slot>
    </div>
  </div>
  
  <style>
    .video-container {
      position: relative;
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
  
    .top-left {
      clip-path: polygon(0 0, 100% 0, 0 100%);
    }
  
    .bottom-right {
      clip-path: polygon(100% 0, 100% 100%, 0 100%);
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
      filter: blur(var(--blur-amount, 5px));
      z-index: 0;
      object-fit: cover;
    }
  
  
    .content {
      position: relative;
      z-index: 2;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      color: white;
      text-align: center;
      background-color: rgba(0, 0, 0, var(--overlay-opacity, 0.3));
    }
  
    :global(.content h1) {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
  
    :global(.content p) {
      font-size: 1.2rem;
      max-width: 600px;
      margin: 0 auto;
    }
  </style>