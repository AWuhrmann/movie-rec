<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
	import { enrichRecommendationStore } from '$lib/recommendationStore';
	import type { Movie } from '../types/movie';
  
  // Create reactive variables for our data and loading state
  let worldGeoJson: any = null;
  let neuronsData: any = null;
  let populationData = new Map();
  let isLoading = true;
  let isLoadingMovies = true;
  let error: string | null = null;

  let movies: Movie[] = [];

  const languageCountries = {
    'en': ['USA', 'GBR', 'CAN', 'AUS', 'NZL', 'GHA', 'NGA', 'KEN', 'UGA', 'ZWE', 'ZMB', 'SLE', 'LBR', 'GMB', 'BWA', 'MWI', 'TZA', 'SSD'],
    'es': ['ESP', 'MEX', 'COL', 'ARG', 'PER', 'CHL', 'ECU', 'GTM', 'CUB', 'GNQ'],
    'tr': ['TUR'],
    'sv': ['SWE'],
    'it': ['ITA', 'CHE'],
    'hi': ['IND'],
    'pl': ['POL'],
    'hu': ['HUN'],
    'de': ['DEU', 'AUT', 'CHE', 'LIE', 'NAM'],  // Namibia has German as a recognized language
    'sr': ['SRB'],
    'fi': ['FIN'],
    'ko': ['KOR'],
    'fr': ['FRA', 'CAN', 'BEL', 'CHE', 'MCO', 'LUX', 'SEN', 'MLI', 'BFA', 'NER', 'TCD', 'CIV', 'BEN', 'TGO', 'CMR', 'GAB', 'COG', 'CAF', 'GIN', 'BDI', 'COM', 'DJI', 'MDG', 'MUS', 'COD', 'RWA'],
    'da': ['DNK'],
    'ro': ['ROU', 'MDA'],
    'zh': ['CHN', 'TWN', 'SGP'],
    'ja': ['JPN'],
    'pt': ['PRT', 'BRA', 'AGO', 'MOZ', 'CPV', 'GNB', 'STP'],
    'he': ['ISR'],
    'nl': ['NLD', 'BEL', 'SUR'],
    'el': ['GRC', 'CYP'],
    'mk': ['MKD'],
    'ru': ['RUS', 'BLR', 'KAZ'],
    'bs': ['BIH'],
    'cs': ['CZE'],
    'fa': ['IRN'],
    'no': ['NOR'],
    'th': ['THA'],
    'sl': ['SVN'],
    'ar': ['SAU', 'EGY', 'IRQ', 'YEM', 'SYR', 'DZA', 'SDN', 'MAR', 'TUN', 'LBY', 'MRT', 'SOM', 'DJI', 'COM', 'ERI', 'TCD'],
    'bn': ['BGD', 'IND'],
    'ky': ['KGZ'],
    'id': ['IDN'],
    'tl': ['PHL'],
    'ka': ['GEO'],
    'hr': ['HRV'],
    'ur': ['PAK'],
    'is': ['ISL'],
    'mn': ['MNG'],
    'tg': ['TJK'],
    'rw': ['RWA'],
    'sq': ['ALB', 'KOS'],
    'vi': ['VNM'],
    'sk': ['SVK'],
    'ps': ['AFG'],
    'bg': ['BGR'],
    'lt': ['LTU'],
    'et': ['EST'],
    'uk': ['UKR'],
    'ms': ['MYS', 'BRN'],
    'af': ['ZAF', 'NAM'],
    'lv': ['LVA'],
    'am': ['ETH'],
    'sw': ['TZA', 'KEN', 'UGA'], // Added Swahili
    'ha': ['NGA', 'NER'], // Added Hausa
    'ig': ['NGA'], // Added Igbo
    'yo': ['NGA'], // Added Yoruba
    'wo': ['SEN'], // Added Wolof
    'ny': ['MWI'], // Added Chichewa
    'sn': ['ZWE'], // Added Shona
    'xh': ['ZAF'], // Added Xhosa
    'zu': ['ZAF']  // Added Zulu
};

  let currentNeuron: number = 0;

  // Create our SVG container reference
  let svgContainer: SVGElement;

  // Other for activation
  let svgActivation: SVGElement;

  // Function to fetch and process our data
  async function fetchData() {
    try {
      // Fetch both datasets in parallel
      const [geoResponse, populationResponse, neurons_data] = await Promise.all([
        fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson'),
        fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world_population.csv'),
        fetch('/neurons_data.json')
      ]);

      
      // Parse the GeoJSON data
      worldGeoJson = await geoResponse.json();
      neuronsData = await neurons_data.json();
      const langMap = new Map();
      Object.entries(neuronsData[currentNeuron].countries).forEach(d => {
        const val = Object.entries(d[1])[0];
        const langCode = val[0].split('_').pop();
        
        // If language exists in our mapping
        if (languageCountries[langCode]) {
          // For each country that uses this language
          languageCountries[langCode].forEach(countryCode => {
            langMap.set(countryCode, val[1]);
          });
        }
      });
      
      const movieDetails = await enrichRecommendationStore(neuronsData[currentNeuron].titles).finally(() => {isLoadingMovies = false;});

    
      movies = movieDetails.slice(0, 4);

      // Parse the CSV data and create our population map
      const csvText = await populationResponse.text();
      const csvData = d3.csvParse(csvText);
      populationData = langMap;

      // Now that we have our data, create the visualization
      createVisualization();
    } catch (e) {
      error = 'Error loading map data';
      console.error('Error:', e);
    } finally {
      isLoading = false;
    }
  }

  // Function to create our visualization once data is loaded
  function createVisualization() {
    if (!worldGeoJson || !svgContainer || !svgActivation) return;

    // Set up our projection and path generator
    const projection = d3.geoMercator()
      .scale(110)
      .center([-50, 40])
      .translate([widthMap / 2, heightMap / 2]);

    const path = d3.geoPath().projection(projection);

    const containerWidth = svgContainer.parentElement?.clientWidth || 0;
    const containerHeight = svgContainer.parentElement?.clientHeight || 0;

    
    // Clear any existing content
    d3.select(svgContainer).selectAll("*").remove();
    
    // Set SVG attributes for responsiveness
    const svg = d3.select(svgContainer)
      .attr('viewBox', `0 0 ${containerWidth} ${containerHeight}`)

    // Create color scale for population
    const colorScale = d3.interpolateRdBu;

    // Draw the map
    svg.append("g")
      .selectAll("path")
      .data(worldGeoJson.features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", d => {
        const pop = populationData.get(d.id);
        return pop ? colorScale(0.5 + 2*pop) : "#ccc";
      })
      .style("stroke", "#fff")
      .style("stroke-width", 0.5)
      // Add hover interactivity
      .on("mouseover", function(event, d) {
        d3.select(this)
          .style("stroke", "#000")
          .style("stroke-width", 1);
          tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(Math.round((1000.0 * populationData.get(d.id))) / 1000)
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");

      })
      .on("mouseout", function(event, d) {
        d3.select(this)
          .style("stroke", "#fff")
          .style("stroke-width", 0.5);
      
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
        });


    const containerActWidth = svgActivation.parentElement?.clientWidth || 0;
    const containerActHeight = svgActivation.parentElement?.clientHeight || 0;

    
    // Set SVG attributes for responsiveness
    const svg2 = d3.select(svgActivation)
      .attr('viewBox', `0 0 ${containerActWidth} ${containerActHeight}`)

      d3.select(svgActivation).selectAll("*").remove();
      
      const data = Object.entries(neuronsData[currentNeuron].activations);
      const tooltip = d3.select("body")
        .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background-color", "white")
        .style("border", "solid")
        .style("padding", "5px");
      
      svg2.selectAll("rect")
      .data(data)
      .enter()
      .append('rect')
      .attr('x', (d, i) => i * (widthAct / data.length))
      .attr('y', d => d[1] > 0 ? heightAct/2 - d[1]*200 : heightAct/2)  
      .attr('width', widthAct / data.length - 2)
      .attr('height', d => Math.abs(d[1]*200))
      .attr('fill', d => d[1] > 0 ? 'steelblue' : 'red');
      
      
      svg2.selectAll("rect.hover-area")
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'hover-area')
      .attr('x', (d, i) => i * (widthAct / data.length) - 10)
      .attr('y', 0)
      .attr('width', widthAct / data.length + 20)
      .attr('height', heightAct)
      .attr('fill', 'transparent')
      .on("mouseover", (event, d) => {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(d[0])
          .style("left", (event.pageX) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", () => {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      });;
 
  }

  // Set up our constants
  const widthMap = 500;
  const heightMap = 200;
  const widthAct = 500;
  const heightAct = 200;

  // Use Svelte's onMount to start loading data when component mounts
  onMount(() => {
    fetchData();
  });

  // Watch for container size changes
  $: if (svgContainer && worldGeoJson && svgActivation) {
    createVisualization();
  }

  async function updateVisualization() {
    
    const movieDetails = await enrichRecommendationStore(neuronsData[currentNeuron].titles).finally(() => {isLoadingMovies = false;});
    movies = movieDetails.slice(0, 4);


    createVisualization();

    const langMap = new Map();
      Object.entries(neuronsData[currentNeuron].countries).forEach(d => {
        const val = Object.entries(d[1])[0];
        const langCode = val[0].split('_').pop();
        
        // If language exists in our mapping
        if (languageCountries[langCode]) {
          // For each country that uses this language
          languageCountries[langCode].forEach(countryCode => {
            langMap.set(countryCode, val[1]);
          });
        }
      });

      populationData = langMap
  }

  $: if (svgActivation && currentNeuron) {
    updateVisualization();
  }
</script>

<div class="grid-container">
  <!-- Left Column -->
  <div class="left-column">
    <!-- Search Section -->
    
    <div class="search-section">
      <h2 class="section-title">Enter neuron number</h2>
      <input 
      type="number" bind:value={currentNeuron}
        placeholder="Search..." 
        class="w-full p-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
    </div>
    
    <!-- Movies Grid -->
    <div>

      <h2 class="section-title">Movies</h2> <!-- Added title -->
      <div class="movies-grid">
        {#if isLoadingMovies}
        <div class="loading-state">
          <span class="text-lg text-gray-600">Loading movies...</span>
        </div>
        {:else}
        {#each movies as movie}
        <div class="movie-card">
          <img
          src={movie.poster}
          alt={`${movie.title} poster`}
          class="movie-poster"
          loading="lazy"
          />
        </div>
        {/each}
        {/if}
      </div>
    </div>
  </div>

  <!-- Right Column -->
  <div class="right-column">
    <!-- Map Container -->
    <div class="map-section">
      <h2 class="section-title">Language correlation</h2>
      {#if isLoading}
        <div class="loading-state">Loading map data...</div>
      {:else if error}
        <div class="error-state">{error}</div>
      {:else}
        <svg bind:this={svgContainer}></svg>
      {/if}
    </div>

    <!-- Activation Container -->
    <div class="activation-section">
      <h2 class="section-title">Feature correlation</h2>
      {#if isLoading}
        <div class="loading-state">Loading map data...</div>
      {:else if error}
        <div class="error-state">{error}</div>
      {:else}
        <svg bind:this={svgActivation}></svg>
      {/if}
    </div>
  </div>
</div>

<style>
  h2 {
    margin-top: 0px;
  }

  .grid-container {
    display: grid;
    grid-template-columns: 1fr 2fr; /* Two equal columns */
    gap: 2rem;
    padding: 2rem;
  }

  .left-column {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .search-section {
    padding: 1rem 0;
  }

  .movies-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr); /* 2x2 grid */
    gap: 1rem;
    overflow-y: auto;
    background-color: #f8f9fa;
    border-radius: 0.5rem;

  }

  .movie-card {
    aspect-ratio: 2/3;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  .movie-poster {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.2s;
  }

  .movie-poster:hover {
    transform: scale(1.05);
  }

  .right-column {
    display: grid;
    grid-template-rows: 1fr 1fr; /* Two equal rows */
    gap: 1.5rem;
  }

  .map-section,
  .activation-section {
    background-color: #f8f9fa;
    border-radius: 0.5rem;
    padding: 1rem;
    min-height: 0; /* Prevents overflow issues */
    width: 100%;
    height: 300px; /* or whatever fixed height you want */
    /* or use a percentage of the viewport */
    /* height: 40vh; */
    position: relative;
    overflow: hidden; /* This prevents any overflow */
  }

  .loading-state,
  .error-state {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 1.125rem;
    color: #6b7280;
  }

  /* Ensure SVGs take full space of their containers */
  

  .loading, .error {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 1rem;
  }

  .error {
    color: #e53e3e;
  }
</style>