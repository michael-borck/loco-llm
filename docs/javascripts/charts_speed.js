// Speed page charts: Generation Speed bar + TTFT vs File Size scatter
(function() {
  'use strict';

  function render() {
    if (!window.BENCHMARK_DATA || !window.LOCOLLM_CHART_THEME) return;

    var data = window.BENCHMARK_DATA;
    var theme = window.LOCOLLM_CHART_THEME;

    renderGenerationSpeed(data, theme);
    renderTTFT(data, theme);
  }

  function renderGenerationSpeed(data, theme) {
    var div = document.getElementById('chart-speed-generation');
    if (!div) return;

    // Filter to Q4_K_M for a clean comparison, sorted by speed
    var variants = data.variants
      .filter(function(v) { return v.quant === 'Q4_K_M' && v.tg_ts !== null; })
      .sort(function(a, b) { return a.tg_ts - b.tg_ts; });

    var labels = variants.map(function(v) { return v.model_name; });
    var speeds = variants.map(function(v) { return v.tg_ts; });
    var colors = variants.map(function(v) { return theme.colorForFamily(v.family); });

    var trace = {
      x: speeds,
      y: labels,
      type: 'bar',
      orientation: 'h',
      marker: { color: colors },
      text: speeds.map(function(s) { return s.toFixed(1) + ' t/s'; }),
      textposition: 'outside',
      textfont: { color: '#e2e8f0', size: 11 },
      hovertemplate: '%{y}<br>%{x:.1f} t/s<extra></extra>'
    };

    // Usability threshold line at 5 t/s
    var shapes = [{
      type: 'line',
      x0: 5, x1: 5,
      y0: -0.5, y1: labels.length - 0.5,
      line: { color: '#f97316', width: 2, dash: 'dash' }
    }];

    var annotations = [{
      x: 5, y: labels.length - 0.5,
      text: '5 t/s usability threshold',
      showarrow: false,
      font: { color: '#f97316', size: 10 },
      xanchor: 'left',
      xshift: 5
    }];

    var layout = theme.mergeLayout({
      title: { text: 'Generation Speed at Q4_K_M (CPU-only)' },
      xaxis: { title: { text: 'Tokens/sec (tg)' } },
      yaxis: { automargin: true, tickfont: { size: 11 } },
      margin: { l: 160, r: 80, t: 50, b: 50 },
      showlegend: false,
      shapes: shapes,
      annotations: annotations
    });

    Plotly.newPlot(div, [trace], layout, theme.config);
  }

  function renderTTFT(data, theme) {
    var div = document.getElementById('chart-speed-ttft');
    if (!div) return;

    var variants = data.variants.filter(function(v) {
      return v.ttft_ms !== null && v.file_size_gb !== null;
    });

    // Group by family
    var families = {};
    variants.forEach(function(v) {
      if (!families[v.family]) families[v.family] = [];
      families[v.family].push(v);
    });

    var traces = [];
    Object.keys(families).forEach(function(family) {
      var fv = families[family];
      traces.push({
        x: fv.map(function(v) { return v.file_size_gb; }),
        y: fv.map(function(v) { return v.ttft_ms; }),
        text: fv.map(function(v) {
          return v.model_name + ' ' + v.quant + '<br>' +
                 'TTFT: ' + v.ttft_ms.toFixed(0) + ' ms<br>' +
                 'Size: ' + v.file_size_gb + ' GB';
        }),
        hoverinfo: 'text',
        mode: 'markers',
        name: family,
        marker: {
          color: theme.colorForFamily(family),
          size: 7,
          opacity: 0.7
        }
      });
    });

    var layout = theme.mergeLayout({
      title: { text: 'Time-to-First-Token vs File Size' },
      xaxis: { title: { text: 'File Size (GB)' } },
      yaxis: { title: { text: 'TTFT (ms)' } },
      legend: { orientation: 'h', y: -0.15 }
    });

    Plotly.newPlot(div, traces, layout, theme.config);
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() { render(); });
  } else {
    document.addEventListener('DOMContentLoaded', render);
  }
})();
