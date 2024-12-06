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

  	export let value = `$x + 2 = 0$`;
    
    $: totalMovies = $movies.length;
    $: ratedMovies = $movies.filter(m => m.rating > 0).length;
    $: averageRating = $movies.reduce((acc, m) => acc + m.rating, 0) / ratedMovies || 0;
  </script>
  
  <div class="max-w-4xl">
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

    <GraphComponent></GraphComponent>
  
    <section id="ratings" class="mb-16">
      <h2 class="text-2xl font-bold mb-6">Ratings Analysis</h2>
      <div class="bg-white p-6 rounded-lg shadow-sm">
        
        <p class="text-gray-700">Analysis of your movie ratings distribution and patterns. </p>
        <h1>The Mathematical Foundations of Terryology: A Critical Analysis</h1>
    
    <div class="abstract">
        <h2>Abstract</h2>
        <p>This paper examines the mathematical framework proposed by Terrence Howard's Terryology, which posits that 1 × 1 = 2. Through rigorous analysis of Howard's "Universal Math" system, we explore the implications of this revolutionary perspective on fundamental arithmetic operations.</p>
    </div>

    <h2>Introduction</h2>
    <p>In 2015, actor Terrence Howard proposed a radical reinterpretation of mathematics, challenging the centuries-old understanding that 1 × 1 = 1. This paper presents a detailed examination of Howard's theories and their potential implications for modern mathematics.</p>

    <h2>Methodology</h2>
    <p>Our analysis employs Howard's "straight line" theory, which argues that since multiplication represents physical motion along geometric paths, the product of 1 and 1 must trace two distinct linear paths, thereby yielding 2 as the result.</p>

    <h2>Key Principles of Terryology</h2>
    <ul>
        <li>The rejection of traditional multiplication principles based on Howard's observation that "If one times one equals one, that means that two is of no value."</li>
        <li>The assertion that the square root of 2 must be a whole number, as "everything in the universe is perfect."</li>
        <li>The concept that numbers exist as physical entities that follow "natural law" rather than human-made conventions.</li>
    </ul>

    <h2>Analysis</h2>
    <p>Howard's system proposes that when multiplying 1 × 1:</p>
    <ul>
        <li>The first "1" creates an initial straight line</li>
        <li>The second "1" creates a second straight line</li>
        <li>Therefore, two lines are created, resulting in 1 × 1 = 2</li>
    </ul>

    <p>This leads to fascinating implications, such as:</p>
    <ul>
        <li>2 × 2 would equal 8 (following the same logic)</li>
        <li>The square root of 2 would be 1</li>
        <li>π would be a rational number</li>
    </ul>

    <h2>Discussion</h2>
    <p>While Terryology challenges our fundamental understanding of mathematics, several questions arise:</p>
    <ul>
        <li>How does this system reconcile with observed physical phenomena?</li>
        <li>What implications would this have for engineering and technology?</li>
        <li>How might this affect our understanding of quantum mechanics?</li>
    </ul>

    <h2>Conclusion</h2>
    <p>Terryology represents a unique perspective on mathematical principles that, while divergent from conventional mathematics, prompts us to question our assumptions about numerical relationships. Further research is needed to fully understand the implications of this revolutionary framework.</p>

      </div>
    </section>
  
    <section id="trends" class="mb-16">
      <h2 class="text-2xl font-bold mb-6">Rating Trends <Markdown {carta} {value}></Markdown></h2>
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <p class="text-gray-700">Trends in your rating behavior over time.</p>
      </div>
    </section>
  
    <section id="recommendations" class="mb-16">
      <h2 class="text-2xl font-bold mb-6">Recommendations</h2>
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <p class="text-gray-700">Movie recommendations based on your ratings.</p>
      </div>
    </section>
  </div>