<script lang="ts">
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    
    export let endValue: number;
    export let duration = 2000; // Duration in milliseconds
    
    const count = tweened(0, {
      duration,
      easing: cubicOut
    });
    
    // Start the animation when the component mounts
    $: count.set(endValue);
  </script>
  
  <span>{Math.round($count)}</span>
  