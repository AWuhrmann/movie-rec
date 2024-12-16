<script>
    import { onMount } from 'svelte';
  
    // Sample data structure with image parameters
    const data = {
  name: "Root",
  children: [
    {
      name: "France",
      image: {
        url: "/images/france.png",
        size: 60,
        shape: "square",
        padding: 10
      },
      children: [
        {
          name: "District B13",
          value: 1,
          image: {
            url: "/images/district_13.jpg",
            size: 300,
            shape: "circle",
            padding: 2
          },
          children: [
            {
              name: "The Intouchables",
              image: {
                url: "/images/intouchables.jpg",
                size: 1000,
                shape: "square",
                padding: 200
              },
              children: [
                {
                  name: "A Cat in Paris",
                  value: 1,
                  image: {
                    url: "/images/A_Cat_in_Paris_poster.png",
                    size: 750,
                    shape: "circle",
                    padding: 2
                  }
                }
              ]
            }
          ]
        }
      ]
    },
    {
      name: "USA",
      image: {
        url: "/images/us.png",
        size: 60,
        shape: "square",
        padding: 10
      },
      children: [
        {
          name: "Iron Man",
          value: 1,
          image: {
            url: "/images/iron_man.jpg",
            size: 500,
            shape: "circle",
            padding: 2
          },
          children: [
            {
              name: "The Hangover",
              image: {
                url: "/images/hangover.jpg",
                size: 480,
                shape: "circle",
                padding: 5
              },
              children: [
                {
                  name: "How to Train Your Dragon",
                  value: 1,
                  image: {
                    url: "/images/how_train_dragon.jpg",
                    size: 700,
                    shape: "square",
                    padding: 2
                  }
                }
              ]
            }
          ]
        }
      ]
    },
    {
      name: "Japan",
      image: {
        url: "/images/japan.jpg",
        size: 60,
        shape: "square",
        padding: 10
      },
      children: [
        {
          name: "13 Assassins",
          value: 1,
          image: {
            url: "/images/assassin_13.jpg",
            size: 500,
            shape: "circle",
            padding: 2
          },
          children: [
            {
              name: "Survive Style 5+",
              image: {
                url: "/images/survive_style.jpg",
                size: 500,
                shape: "circle",
                padding: 5
              },
              children: [
                {
                  name: "Ponyo",
                  value: 1,
                  image: {
                    url: "/images/ponyo.jpg",
                    size: 1300,
                    shape: "circle",
                    padding: 2
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};

let selectedArc = null;
let movieConnections = null;

onMount(() => {
    loadJson();
});

async function loadJson() {
    const req = await fetch('/movie_recommendations.json');
    movieConnections = await req.json();

    console.log(movieConnections);
}

function isConnected(arc) {
    if (!selectedArc) return false;
    if (!movieConnections[selectedArc.name]) return false;
    return movieConnections[selectedArc.name].recommended_movies.includes(arc.name);
}
  
    let width = 1000;
  let height = 1000;
  let radius = Math.min(width, height) / 2;

  function computeArcs(node, startAngle = 0, endAngle = 2 * Math.PI-0.0001, level = 0) {
    const arcs = [];
    const segmentWidth = 80;
    
    // Special handling for root level to create 3 equal sections
    if (level === 0) {
        const sectionAngle = (2 * Math.PI) / 3;
        
        // Process each root section and its children
        node.children.forEach((child, i) => {
            const sectionStart = i * sectionAngle;
            const sectionEnd = (i + 1) * sectionAngle - 0.0001; // Prevent overlap
            const centerRadius = segmentWidth / 2;
            const centerAngle = (sectionStart + sectionEnd) / 2;
            
            // Add the root section
            arcs.push({
                path: describeArc(width/2, height/2, 0, segmentWidth, sectionStart, sectionEnd),
                clipPath: describeArc(width/2, height/2, 0, segmentWidth, sectionStart, sectionEnd),
                name: child.name,
                image: child.image,
                centerX: width/2 + centerRadius * Math.cos(centerAngle - Math.PI/2),
                centerY: height/2 + centerRadius * Math.sin(centerAngle - Math.PI/2),
                angleWidth: sectionAngle,
                innerRadius: 0,
                outerRadius: segmentWidth,
                startAngle: sectionStart,
                endAngle: sectionEnd,
                level: 0
            });
            
            // Process children of this root section using your existing child processing logic
            if (child.children) {
                let currentAngle = sectionStart;
                const totalValue = child.children.reduce((sum, grandChild) => 
                    sum + (grandChild.value || (grandChild.children ? grandChild.children.length : 1)), 0);

                child.children.forEach(grandChild => {
                    const childValue = grandChild.value || (grandChild.children ? grandChild.children.length : 1);
                    const angle = (sectionEnd - sectionStart) * (childValue / totalValue);
                    arcs.push(...computeArcs(grandChild, currentAngle, currentAngle + angle, 1));
                    currentAngle += angle;
                });
            }
        });
        
        return arcs;
    }

    // Your existing code for non-root levels remains exactly the same
    if (!node.children) {
        const innerRadius = level * segmentWidth;
        const outerRadius = (level + 1) * segmentWidth;
        const centerRadius = (innerRadius + outerRadius) / 2;
        const centerAngle = (startAngle + endAngle) / 2;
        
        return [{
            path: describeArc(width/2, height/2, innerRadius, outerRadius, startAngle, endAngle),
            clipPath: describeArc(width/2, height/2, innerRadius, outerRadius, startAngle, endAngle),
            name: node.name,
            image: node.image,
            centerX: width/2 + centerRadius * Math.cos(centerAngle - Math.PI/2),
            centerY: height/2 + centerRadius * Math.sin(centerAngle - Math.PI/2),
            angleWidth: endAngle - startAngle,
            innerRadius,
            outerRadius,
            startAngle,
            endAngle,
            level
        }];
    }

    // Rest of your existing code for handling children
    const innerRadius = level * segmentWidth;
    const outerRadius = (level + 1) * segmentWidth;
    const centerRadius = (innerRadius + outerRadius) / 2;
    const centerAngle = (startAngle + endAngle) / 2;

    arcs.push({
        path: describeArc(width/2, height/2, innerRadius, outerRadius, startAngle, endAngle),
        clipPath: describeArc(width/2, height/2, innerRadius, outerRadius, startAngle, endAngle),
        name: node.name,
        image: node.image,
        centerX: width/2 + centerRadius * Math.cos(centerAngle - Math.PI/2),
        centerY: height/2 + centerRadius * Math.sin(centerAngle - Math.PI/2),
        angleWidth: endAngle - startAngle,
        innerRadius,
        outerRadius,
        startAngle,
        endAngle,
        level
    });

    let currentAngle = startAngle;
    const totalValue = node.children.reduce((sum, child) => 
        sum + (child.value || (child.children ? child.children.length : 1)), 0);

    node.children.forEach(child => {
        const childValue = child.value || (child.children ? child.children.length : 1);
        const angle = (endAngle - startAngle) * (childValue / totalValue);
        arcs.push(...computeArcs(child, currentAngle, currentAngle + angle, level + 1));
        currentAngle += angle;
    });

    return arcs;
}
  function describeArc(x, y, innerRadius, outerRadius, startAngle, endAngle) {
    const innerStart = polarToCartesian(x, y, innerRadius, endAngle);
    const innerEnd = polarToCartesian(x, y, innerRadius, startAngle);
    const outerStart = polarToCartesian(x, y, outerRadius, endAngle);
    const outerEnd = polarToCartesian(x, y, outerRadius, startAngle);

    const largeArcFlag = endAngle - startAngle <= Math.PI ? "0" : "1";

    return [
      "M", outerStart.x, outerStart.y,
      "A", outerRadius, outerRadius, 0, largeArcFlag, 0, outerEnd.x, outerEnd.y,
      "L", innerEnd.x, innerEnd.y,
      "A", innerRadius, innerRadius, 0, largeArcFlag, 1, innerStart.x, innerStart.y,
      "L", outerStart.x, outerStart.y,
      "Z"
    ].join(" ");
  }

  function polarToCartesian(centerX, centerY, radius, angleInRadians) {
    return {
      x: centerX + (radius * Math.cos(angleInRadians - Math.PI/2)),
      y: centerY + (radius * Math.sin(angleInRadians - Math.PI/2))
    };
  }

  let arcs = computeArcs(data);
  let hoveredArc = null;

  function getClipPathId(arc) {
    return `clip-${arc.name.toLowerCase().replace(/\s+/g, '-')}`;
  }

  // Calculate the maximum size that will fit in the arc
  function calculateMaxImageSize(arc) {
    return 9999
    const radialSpace = arc.outerRadius - arc.innerRadius - (2 * arc.image.padding);
    const arcLength = arc.angleWidth * ((arc.innerRadius + arc.outerRadius) / 2);
    return Math.min(radialSpace, arcLength);
  }
</script>

<div class="sunburst-container">
  <svg {width} {height}>
    <defs>
      {#each arcs as arc}
        <clipPath id={getClipPathId(arc)}>
          <path d={arc.clipPath} />
        </clipPath>
      {/each}
    </defs>

    {#each arcs as arc}
    <g
      class:root={arc.level === 0}
      on:mouseenter={() => hoveredArc = arc}
      on:mouseleave={() => hoveredArc = null}
      on:click={() => selectedArc = (selectedArc === arc) ? null : arc}
      class:selected={selectedArc === arc}
      class:connected={isConnected(arc)}
    >
      <path
        d={arc.path}
        fill="white"
        stroke="#ccc"
        stroke-width="1"
        class="arc"
      />
      {#if arc.image}
        <g clip-path={`url(#${getClipPathId(arc)})`}>
          <image
            href={arc.image.url}
            x={arc.centerX - Math.min(arc.image.size, calculateMaxImageSize(arc)) / 2}
            y={arc.centerY - Math.min(arc.image.size, calculateMaxImageSize(arc)) / 2}
            width={Math.min(arc.image.size, calculateMaxImageSize(arc))}
            height={Math.min(arc.image.size, calculateMaxImageSize(arc))}
            class="segment-image"
            preserveAspectRatio="xMidYMid meet"
            pointer-events="none"
          />
        </g>
      {/if}
    </g>
  {/each}
    
    {#if hoveredArc}
      <text
        x={width/2}
        y={height - 20}
        text-anchor="middle"
        class="hover-text"
      >
        {hoveredArc.name}
      </text>
    {/if}
  </svg>
</div>

<style>
  .sunburst-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .arc {
    transition: fill 0.2s;
}

.arc:hover {
    fill: #e0e0e0;  /* Make this darker for better contrast */
    opacity: 0.8;   /* Add this for better visibility */
}

  .segment-image {
    transition: transform 0.2s;
  }

  .segment-image:hover {
    transform: scale(1);
  }

  .segment-image {
    filter: grayscale(100%);
    transition: filter 0.3s;
}


.root .segment-image {
    filter: grayscale(0%) !important;
}

g:hover .segment-image {
    filter: grayscale(0%);
}

.selected .segment-image {
    filter: grayscale(0%);
}

.connected .segment-image {
    filter: grayscale(0%);
}

.connected .segment-image {
    filter: grayscale(0%) sepia(100%) saturate(300%) brightness(70%) hue-rotate(90deg);
    transition: filter 0.3s;
}
</style>