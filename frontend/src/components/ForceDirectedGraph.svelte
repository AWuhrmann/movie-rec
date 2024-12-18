<script lang="ts">
    import { onMount, tick } from 'svelte';
    import * as d3 from 'd3';
    
    let data: {
      nodes: Array<{ id: string; name: string; group?: number }>;
      links: Array<{ source: string; target: string }>;
    } | null = null;
  
    let svg;
    let width = 800;
    let height = 600;
    let container;
    let loading = true;
    let error: string | null = null;
    let selectedNodeId: string | null = null;
    let svgElement: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  
    // Watch for changes in svg binding and selectedNodeId
    $: if (svg && selectedNodeId !== null) {
      updateNodeColors();
    }
  
    // Set up svg selection when element is bound
    $: if (svg) {
      svgElement = d3.select(svg);
    }
  
    function selectRandomNode() {
      if (!data || !data.nodes.length) return;
      const randomIndex = Math.floor(Math.random() * data.nodes.length);
      selectedNodeId = data.nodes[randomIndex].id;
    }
  
    function getNodeColor(d) {
      if (!d || !d.id) return '#1f77b4';
      return d.id === selectedNodeId ? '#4CAF50' : '#1f77b4';
    }
  
    function updateNodeColors() {
      if (!svgElement) return;
      
      svgElement
        .selectAll('circle')
        .transition()
        .duration(200)
        .attr('fill', d => getNodeColor(d));
    }
  
    async function fetchGraphData() {
      try {
        const response = await fetch('/graph-data.json');
        if (!response.ok) throw new Error('Failed to fetch data');
        data = await response.json();
        loading = false;
        if (data) {
          // Wait for next tick to ensure svg is bound
          await tick();
        //   drawGraph();
          selectRandomNode();
        }
      } catch (e) {
        error = e.message;
        loading = false;
      }
    }
  
    function drawGraph() {
      if (!data || !svgElement) return;
  
      svgElement.selectAll("*").remove();
  
      svgElement
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
  
      const nodes = data.nodes.map(d => ({...d}));
      const links = data.links.map(d => ({...d}));
  
      const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links)
          .id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter());
  
      const link = svgElement.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 1.5)
        .attr("stroke-linecap", "round")
        .selectAll("line")
        .data(links)
        .join("line");
  
      const node = svgElement.append("g")
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", 5)
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .attr("fill", d => getNodeColor(d))
        .call(drag(simulation))
        .on("click", (event, d) => {
          selectedNodeId = d.id;
        });
  
      node.append("title")
        .text(d => d.name || d.id);
  
      simulation.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
  
        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);
      });
  
      function drag(simulation) {    
        function dragstarted(event) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
          event.subject.fx = event.x;
          event.subject.fy = event.y;
        }
        
        function dragended(event) {
          if (!event.active) simulation.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
        }
        
        return d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended);
      }
  
      return () => {
        simulation.stop();
      };
    }
  
    onMount(async () => {
      await fetchGraphData();
    });
  </script>
  
  <div class="graph-container" bind:this={container}>
    {#if loading}
      <div class="loading">Loading...</div>
    {:else if error}
      <div class="error">Error: {error}</div>
    {:else}
      <button class="random-button" on:click={selectRandomNode}>
        Select Random Node
      </button>
      <svg 
        bind:this={svg}
        {width}
        {height}
      ></svg>
    {/if}
  </div>
  
  <style>
    .graph-container {
      width: 100%;
      height: 100%;
      min-height: 600px;
      position: relative;
    }
  
    svg {
      width: 100%;
      height: 100%;
    }
  
    .random-button {
      position: absolute;
      top: 10px;
      left: 10px;
      padding: 8px 16px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      z-index: 1;
    }
  
    .random-button:hover {
      background-color: #45a049;
    }
  
    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 600px;
      font-size: 1.2rem;
      color: #666;
    }
  
    .error {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 600px;
      font-size: 1.2rem;
      color: #dc2626;
    }
  </style>