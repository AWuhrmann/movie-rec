<script lang="ts">
    import { movies } from '$lib/movieStore';
    import 'katex/dist/katex.css';

  import CountUp from '../components/CountUp.svelte';

	import SectionEditor from '../components/SectionEditor.svelte';
	import NeuronsAnalyzer from '../components/NeuronsAnalyzer.svelte';
	import TSne from '../components/tSNE.svelte';
	import InfiniteMovieScroll from '../components/InfiniteMovieScroll.svelte';
	import Videobackground from '../components/Videobackground.svelte';
	import type { Movie } from '../types/movie';


  import { bounceOut } from 'svelte/easing';
	import SunBurstMovies from '../components/SunBurstMovies.svelte';
	import GlobeVisu from '../components/GlobeVisu.svelte';

  	export let value = `
    # this is a test
    hey
    $x + 2 = 0$`;
    
    $: totalMovies = $movies.length;
    $: ratedMovies = $movies.filter(m => m.rating > 0).length;
    $: averageRating = $movies.reduce((acc, m) => acc + m.rating, 0) / ratedMovies || 0;
  
    const sampleMovies: Movie[] = [
    {
      id: "1",
      title: "Inception",
      rating: 0,
      genre: "Sci-Fi",
      year: "2010",
      poster: "/posters/inception.jpg",
      posterPath: null,
      tmdbId: 1,
      plot: "A thief who enters the dreams of others",
      imdbRating: "8.8"
    },
    {
      id: "2",
      title: "The Matrix",
      rating: 0,
      genre: "Sci-Fi",
      year: "1999",
      poster:"/posters/thematrix.jpg",
      posterPath: null,
      tmdbId: 2,
      plot: "A computer programmer discovers a mysterious world",
      imdbRating: "8.7"
    },
    {
      id: "3",
      title: "Pulp Fiction",
      rating: 0,
      genre: "Crime",
      year: "1994",
      poster: "/posters/pulpfiction.jpg",
      posterPath: null,
      tmdbId: 3,
      plot: "Various interconnected stories in Los Angeles",
      imdbRating: "8.9"
    },
    {
      id: "4",
      title: "The Godfather",
      rating: 0,
      genre: "Crime",
      year: "1972",
      poster: "/posters/godfather.jpg",
      posterPath: null,
      tmdbId: 4,
      plot: "The aging patriarch of a crime dynasty",
      imdbRating: "9.2"
    },
    {
      id: "5",
      title: "Interstellar",
      rating: 0,
      genre: "Sci-Fi",
      year: "2014",
      poster: "/posters/interstellar.jpg",
      posterPath: null,
      tmdbId: 5,
      plot: "Astronauts travel through a wormhole",
      imdbRating: "8.6"
    },
    {
      id: "6",
      title: "The Dark Knight",
      rating: 0,
      genre: "Action",
      year: "2008",
      poster: "/posters/thedarkknight.jpg",
      posterPath: null,
      tmdbId: 6,
      plot: "Batman faces his greatest challenge",
      imdbRating: "9.0"
    }
  ];

  </script>

<div class="container">
  <Videobackground 
  videoSource="/images/matrix.mp4"
  blurAmount="5px"
  overlayOpacity="0.3"
  >
  
</Videobackground>

<div class="report-section">
  <div class="report-content">
<div class="container p-8 pl-64 w-[1400px] min-w-0 [@media(min-width:1500px)]:pl-0 [@media(min-width:1500px)]:w-[1000px] mx-auto">
  <div class="prose max-w-none">
    <h1 class="text-3xl font-bold mb-8">Skibidata - Recommendation algorithms</h1>
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      
      <section id="introduction">
        
        <h2>Introduction</h2>
        
        <SectionEditor sectionName='introduction' />
        
      </section>
      
    </div>
    
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      
      <section id="content-based">
        
        <h2>Content-based recommendation</h2>
      </section>
      <SectionEditor sectionName='content-based-recommendations' />
      
      <TSne></TSne>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <h2>Interactive Neuron Analyzer</h2>
      <NeuronsAnalyzer></NeuronsAnalyzer>
    </div>
    <div class="">
      <section id="overview" class="mb-16">
        <div class="grid grid-cols-3 gap-6 mb-8">
          
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-gray-500 mb-2">Total Movies</h3>
            <p class="text-3xl font-bold"><CountUp endValue={342} decimal={0}/></p>
          </div>
          
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-gray-500 mb-2">Rated Movies</h3>
            <p class="text-3xl font-bold"><CountUp endValue={4583821} decimal={0}/></p>
          </div>
          
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-gray-500 mb-2">Average Rating</h3>
            <p class="text-3xl font-bold"><CountUp endValue={3.4} decimal={2} easing={bounceOut}/></p>
          </div>
        </div>
      </section>
      <div class="bg-white p-6 pt-6 rounded-lg shadow-sm mb-12 mt-12">
        <h2 class="">World map XXXX</h2>
        <SectionEditor sectionName='world-map' />
        
        <GlobeVisu></GlobeVisu>
      </div>

      <InfiniteMovieScroll 
      movies={sampleMovies}
      speed={1}
      direction="left"
      gap={20}
      />
      
      <div class="bg-white p-6 rounded-lg shadow-sm mb-12 mt-12">
        
        <section id="collaborative">
          <h2 class="collab-filtering">Collaborative filtering</h2>
          
          <SectionEditor sectionName='collaborative-filtering' />
          
        </section>
      </div>
    <div class="bg-white p-6 pt-6 rounded-lg shadow-sm mb-12 mt-12">
      <h2 class="">Interactive small example</h2>
      <SectionEditor sectionName='sunburst-diagram' />
      
      <SunBurstMovies></SunBurstMovies>
    </div>
    
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <section id="implementation">
        
        <h2>Implementation</h2>
        
        <SectionEditor sectionName='implementation' />
      </section>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <section id="conclusion">
        
        <h2>Conclusion</h2>
        
        <SectionEditor sectionName='conclusion' />
      </section>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <section id="extra-1">
        
        <h2>Extra 1</h2>
        <SectionEditor sectionName='extra-1' />
      </section>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <section id="extra-2">
        
        <h2>Extra 2</h2>
        <SectionEditor sectionName='extra-2' />
      </section>
    </div>

    <div class="bg-white p-6 rounded-lg shadow-sm mb-12">
      <section id="extra-3">
        
        <h2>Extra 3</h2>
        <SectionEditor sectionName='extra-3' />
      </section>
    </div>

  </div>
  
  
</div>
  </div>
</div>

</div>

</div>

  <style>
    h1 {
      @apply mt-0 mb-4 font-bold text-5xl mb-12;
    }
    
    h2 {
      @apply mt-0 mb-4 font-bold text-2xl;
    }
    h3 {
      @apply mt-0;
    }
    .collab-filtering {
      @apply mt-8;
    }

    /* Add these styles to ensure proper content positioning */
    :global(body) {
      margin: 0;
      padding: 0;
      overflow-x: hidden;
    }

  .container {
    min-height: 200vh; /* Makes sure we have enough scroll space */
  }

  .report-section {
    background-color: gray 50;
    padding: 4rem 2rem;
    min-height: 100vh;
    margin-top: 100vh; /* Push report below the video section */
  }


  </style>