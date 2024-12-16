<!-- MovieVisualizationModified.svelte -->
<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    let data = [];
    let svg;
    let isLoading = true;
    let error = null;
    let container;
    let selectedPoints = new Set();
    let relatedPoints = new Set();

    let width;
    let height;
    const aspectRatio = 800 / 600;

    const margin = { top: 20, right: 20, bottom: 40, left: 40 };

    // Example dataset with related points defined
    const sampleData = [
        { 
            id: 1,
            Title: "Movie 1", 
            Year: 2020, 
            TSNE_1: 1, 
            TSNE_2: 1, 
            marker_size: 10,
            relatedTo: [2, 3] // IDs of related movies
        },
        { 
            id: 2,
            Title: "Movie 2", 
            Year: 2019, 
            TSNE_1: 2, 
            TSNE_2: 2, 
            marker_size: 15,
            relatedTo: [1, 4]
        },
        { 
            id: 3,
            Title: "Movie 3", 
            Year: 2021, 
            TSNE_1: 3, 
            TSNE_2: 1, 
            marker_size: 12,
            relatedTo: [1, 5]
        },
        { 
            id: 4,
            Title: "Movie 4", 
            Year: 2018, 
            TSNE_1: 1.5, 
            TSNE_2: 2.5, 
            marker_size: 8,
            relatedTo: [2]
        },
        { 
            id: 5,
            Title: "Movie 5", 
            Year: 2022, 
            TSNE_1: 2.5, 
            TSNE_2: 1.5, 
            marker_size: 20,
            relatedTo: [3]
        }
    ];

    onMount(async () => {
        try {
            // Simulating data fetch with sample data
            data = sampleData;
            isLoading = false;
            drawVisualization();
        } catch (e) {
            error = e.message;
            isLoading = false;
        }

        const cleanup = setupResizeObserver();
        return () => {
            cleanup();
        };
    });

    function setupResizeObserver() {
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                width = entry.contentRect.width;
                height = width / aspectRatio;
                if (data.length > 0) {
                    drawVisualization();
                }
            }
        });
        
        resizeObserver.observe(container);
        return () => resizeObserver.disconnect();
    }

    function selectPoint(d) {
        if (selectedPoints.has(d.id)) {
            selectedPoints.delete(d.id);
            relatedPoints.clear();
        } else {
            selectedPoints.clear();
            selectedPoints.add(d.id);
            
            // Get related points from data
            relatedPoints.clear();
            d.relatedTo.forEach(relatedId => {
                relatedPoints.add(relatedId);
            });
        }
        selectedPoints = selectedPoints; // trigger reactivity
        relatedPoints = relatedPoints; // trigger reactivity
        drawVisualization();
    }

    function getPointColor(d) {
        if (selectedPoints.has(d.id)) return "red";
        if (relatedPoints.has(d.id)) return "green";
        return "blue";
    }

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
            .attr("fill", d => getPointColor(d))
            .attr("stroke", "DarkSlateGrey")
            .attr("stroke-width", 1)
            .attr("opacity", 0.7)
            .attr("cursor", "pointer")
            .on("click", (event, d) => selectPoint(d))
            .on("mouseover", function(event, d) {
                d3.select(this)
                    .attr("opacity", 1)
                    .attr("stroke-width", 2);
                
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                
                const relatedTitles = d.relatedTo
                    .map(id => data.find(item => item.id === id)?.Title)
                    .filter(Boolean)
                    .join(", ");

                tooltip.html(`
                    <strong>${d.Title}</strong> (${d.Year})<br/>
                    Size: ${d.marker_size.toFixed(2)}<br/>
                    Related to: ${relatedTitles}
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
</script>
  
<div class="max-w-300px" bind:this={container}>
    {#if isLoading}
        <div>Loading...</div>
    {:else if error}
        <div class="error">Error: {error}</div>
    {:else}
        <div class="visualization-container">
            <svg 
                bind:this={svg}
                {width}
                {height}
                viewBox="0 0 {width} {height}"
                preserveAspectRatio="xMidYMid meet"
                class="w-full h-auto"
            ></svg>
        </div>
    {/if}
</div>

<style>
    .visualization-container {
        margin: 20px;
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
</style>