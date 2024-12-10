<script lang="ts">
    import { movies } from '$lib/movieStore';
    import 'katex/dist/katex.css';

    import { Carta, Markdown } from 'carta-md';
    import { math } from '@cartamd/plugin-math';
    import { emoji } from '@cartamd/plugin-emoji';
    import { slash } from '@cartamd/plugin-slash';
    import { code } from '@cartamd/plugin-code';
	import CountUp from '../../components/CountUp.svelte';
	import GraphComponent from '../../components/GraphComponent.svelte';

	import SectionEditor from '../../components/SectionEditor.svelte';
	import Diagram from '../../components/Diagram.svelte';
	import TSne from '../../components/tSNE.svelte';
    //import '$lib/styles/github.scss';

    const carta = new Carta({
      sanitizer: false,
      extensions: [
        emoji(),
        slash(),
        code(),
        math()
      ]
    });

  	export let value = `
    # this is a test
    hey
    $x + 2 = 0$`;
    
    $: totalMovies = $movies.length;
    $: ratedMovies = $movies.filter(m => m.rating > 0).length;
    $: averageRating = $movies.reduce((acc, m) => acc + m.rating, 0) / ratedMovies || 0;
  </script>
  
  <div class="max-w-6xl prose">
    <section id="overview" class="mb-16">
      <h1 class="text-3xl font-bold mb-8">Movie Ratings Report</h1>
      <div class="grid grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-gray-500 mb-2">Total Movies</h3>
          
        <p class="text-3xl font-bold"><CountUp endValue={342}/></p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-gray-500 mb-2">Rated Movies</h3>
          <p class="text-3xl font-bold">{ratedMovies}</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="text-gray-500 mb-2">Average Rating</h3>
          <p class="text-3xl font-bold">{averageRating.toFixed(1)}</p>
        </div>
      </div>
    </section>
    
    <div class="prose max-w-6xl">
      
      <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      
      <section id="introduction">
        
        <h2>Introduction</h2>
        
        <SectionEditor sectionName='introduction' />
      </section>
    </div>
  
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
    
      <section id="recommendations-algorithms">
        
        <h2>Content-based recommendation</h2>
  
        <SectionEditor sectionName='content-based-recommendations' />
        
        <TSne></TSne>
        <h2 class="collab-filtering">Collaborative filtering</h2>
  
        <SectionEditor sectionName='collaborative-filtering' />
      
    </section>
  </div>
  
  
  <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
    <section id="introduction">
  
      <h2>Implementation</h2>
    
        <SectionEditor sectionName='implementation' />
      </section>
    </div>
  </div>
</div>

  <style>
    h2 {
      @apply mt-0 mb-4 font-bold text-2xl;
    }
    h3 {
      @apply mt-0
    }
    .collab-filtering {
      @apply mt-8;
    }
  </style>