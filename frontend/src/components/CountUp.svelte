<script lang="ts">
    import { Tween, tweened } from 'svelte/motion';
    import { cubicOut, circOut, quintOut } from 'svelte/easing';
    import { onMount } from 'svelte';

    let { endValue, decimal, easing = quintOut } = $props();
    
    const tween = new Tween(0,
    {
      delay: 100, 
      duration: 4000, 
      easing: easing});

    let triggerElement : HTMLSpanElement;
  
    onMount(() => {

      console.log('test')
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            tween.target = endValue;
            // Your action here
          }
        });
      });
    
    if (triggerElement) {
      observer.observe(triggerElement);
    }
    
    return () => observer.disconnect();
  });
  </script>
  
<span bind:this={triggerElement}>{tween.current.toFixed(decimal)}</span>    