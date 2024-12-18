<svelte:head>
 <script src="https://cdn.plot.ly/plotly-latest.min.js" type="text/javascript"></script>
</svelte:head>
<script>
import { onMount } from 'svelte';
let plotDiv;

onMount(async () => {
    const response = await fetch('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv');
    const text = await response.text();
    const rows = text.split('\n').map(row => row.split(','));
    const data = rows.slice(1).filter(row => row.length > 1).map(row => ({
        COUNTRY: row[0],
        GDP: parseFloat(row[1]),
        CODE: row[2]
    }));

    data.forEach(d => {
        if (d.GDP > 0) d.GDP = Math.log(d.GDP);
    });

    const layout = {
        geo: {
            projection: {
                type: 'orthographic'
            },
            showframe: true,
            showcoastlines: true,
            coastlinecolor: '#d1d1d1',
            showland: true,
            landcolor: '#f7f7f7',
            bgcolor: 'rgba(0,0,0,0)'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 0, l: 0, r: 0, b: 0 },
        dragmode: true
    };

    const config = {
        displayModeBar: false,
        responsive: true
    };

    const trace = {
        type: 'choropleth',
        locationmode: 'ISO-3',
        locations: data.map(d => d.CODE),
        z: data.map(d => d.GDP),
        text: data.map(d => d.COUNTRY),
        colorscale: 'Reds',
        marker: {
            line: {
                color: 'rgb(209,209,209)',
                width: 0.5
            }
        },
        colorbar: {
            title: 'GDP (log)',
            thickness: 20
        }
    };

    Plotly.newPlot(plotDiv, [trace], layout, config);

    return () => {
        Plotly.purge(plotDiv);
    };
});
</script>
<div bind:this={plotDiv}></div>