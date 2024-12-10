<!-- MovieVisualization.svelte -->
<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    let data = [];
  let svg;
  let colorBy = 'Genres';
  let isLoading = true;
  let error = null;

  const width = 800;
  const height = 600;
  const margin = { top: 20, right: 20, bottom: 40, left: 40 };

  onMount(async () => {
    try {
      const response = await fetch('/movie_data.json');
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      data = await response.json();
      isLoading = false;
      drawVisualization();
    } catch (e) {
      error = e.message;
      isLoading = false;
    }
  });

    onMount(() => {
      drawVisualization();
    });
  
    function drawVisualization() {
      const svgElement = d3.select(svg);
  
      // Clear previous content
      svgElement.selectAll("*").remove();
  
      // Create scales
      const xScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.TSNE_1))
        .range([margin.left, width - margin.right]);
  
      const yScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.TSNE_2))
        .range([height - margin.bottom, margin.top]);
  
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
  
      const tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);


      // Create circles for each data point
      svgElement.selectAll("circle")
        .data(data)
        .join("circle")
        .attr("cx", d => xScale(d.TSNE_1))
        .attr("cy", d => yScale(d.TSNE_2))
        .attr("r", d => d.marker_size / 2)
        .attr("fill", d => colorScale(colorBy === 'Genres' ? d.Genres : d.Country))
        .attr("stroke", "DarkSlateGrey")
        .attr("stroke-width", 1)
        .attr("opacity", 0.7)
        .on("mouseover", function(event, d) {
            const currentValue = colorBy === 'Genres' ? d.Genres : d.Country;
            
            d3.select(this)
            .attr("opacity", 1)
            .attr("stroke-width", 2);
            
            tooltip.transition()
            .duration(200)
            .style("opacity", .9);
            
            tooltip.html(`
            <strong>${d.Title}</strong> (${d.Year})<br/>
            ${colorBy}: ${currentValue}<br/>
            Box Office: ${d.marker_size.toFixed(2)}
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");



        })
        .on("mouseout", function() {
            d3.select(this)
            .attr("opacity", 0.7)
            .attr("stroke-width", 1);
            
            tooltip.transition()
            .duration(500)
            .style("opacity", 0);
        });
    }
  
    // Update visualization when colorBy changes
    $: if (svg && colorBy) {
      drawVisualization();
    }
  </script>
  
  
{#if isLoading}
<div>Loading...</div>
{:else if error}
<div class="error">Error: {error}</div>
{:else}
<div class="visualization-container">
  <div class="buttons">
    <button 
      class:active={colorBy === 'Genres'} 
      on:click={() => colorBy = 'Genres'}
    >
      Color by Genre
    </button>
    <button 
      class:active={colorBy === 'Country'} 
      on:click={() => colorBy = 'Country'}
    >
      Color by Country
    </button>
  </div>
  
  <svg 
    bind:this={svg} 
    {width} 
    {height}
  ></svg>
</div>
{/if}
  
  <style>
    .visualization-container {
      margin: 20px;
    }
  
    .buttons {
      margin-bottom: 10px;
    }

    :global(.tooltip) {
    position: absolute;
    padding: 8px;
    font: 12px sans-serif;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #ddd;
    border-radius: 4px;
    pointer-events: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    button {
      margin-right: 10px;
      padding: 8px 16px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background: white;
      cursor: pointer;
    }
  
    button.active {
      background: #007bff;
      color: white;
      border-color: #0056b3;
    }
  
    button:hover {
      background: #e9ecef;
    }
  
    button.active:hover {
      background: #0056b3;
    }
  </style>