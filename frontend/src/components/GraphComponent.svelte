<svelte:head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js" type="text/javascript"></script>
</svelte:head>

<script>
    import { onMount } from 'svelte';
    
    let plotDiv;
    
    onMount(() => {
      // Initialize parameters
      const n = 100;
      const dt = 0.015;
      
      // Initialize arrays
      let x = [], y = [], z = [];
      
      // Set initial random positions
      for (let i = 0; i < n; i++) {
        x[i] = Math.random() * 2 - 1;
        y[i] = Math.random() * 2 - 1;
        z[i] = 30 + Math.random() * 10;
      }
      
      // Create initial plot
      Plotly.newPlot(plotDiv, [{
        x: x,
        y: z,
        mode: 'markers',
        
      }], {
        xaxis: {range: [-40, 40],
          visible: false,
          showgrid: false
        },
        yaxis: {range: [0, 60],
          visible: false,
          showgrid: false
        },
        paper_bgcolor : 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'

      }, {staticPlot: true,
        });
      
      // Compute new positions using Lorenz equations
      function compute() {
        const s = 10, b = 8/3, r = 28;
        let dx, dy, dz;
        let xh, yh, zh;
        
        for (let i = 0; i < n; i++) {
          dx = s * (y[i] - x[i]);
          dy = x[i] * (r - z[i]) - y[i];
          dz = x[i] * y[i] - b * z[i];
          
          xh = x[i] + dx * dt * 0.5;
          yh = y[i] + dy * dt * 0.5;
          zh = z[i] + dz * dt * 0.5;
          
          dx = s * (yh - xh);
          dy = xh * (r - zh) - yh;
          dz = xh * yh - b * zh;
          
          x[i] += dx * dt;
          y[i] += dy * dt;
          z[i] += dz * dt;
        }
      }
      
      // Update animation frame
      function update() {
        compute();
        
        Plotly.animate(plotDiv, {
          data: [{x: x, y: z}]
        }, {
          transition: {
            duration: 0
          },
          frame: {
            duration: 0,
            redraw: false
          }
        });
        
        requestAnimationFrame(update);
      }
      
      // Start animation
      requestAnimationFrame(update);
      
      // Cleanup on component unmount
      return () => {
        Plotly.purge(plotDiv);
      };
    });
    </script>
    
    <div bind:this={plotDiv}></div>