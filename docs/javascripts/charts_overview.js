// Overview page charts: Composite Score vs File Size scatter + Top 10 Leaderboard
(function() {
  'use strict';

  function render() {
    if (!window.BENCHMARK_DATA || !window.LOCOLLM_CHART_THEME) return;

    var data = window.BENCHMARK_DATA;
    var theme = window.LOCOLLM_CHART_THEME;

    renderScatter(data, theme);
    renderLeaderboard(data, theme);
  }

  function renderScatter(data, theme) {
    var div = document.getElementById('chart-overview-scatter');
    if (!div) return;

    var variants = data.variants.filter(function(v) {
      return v.composite_score !== null && v.file_size_gb !== null;
    });

    // Group by family for coloring
    var families = {};
    variants.forEach(function(v) {
      if (!families[v.family]) families[v.family] = [];
      families[v.family].push(v);
    });

    var traces = [];

    Object.keys(families).forEach(function(family) {
      var fv = families[family];
      var isQ4KM = fv.map(function(v) { return v.quant === 'Q4_K_M'; });

      traces.push({
        x: fv.map(function(v) { return v.file_size_gb; }),
        y: fv.map(function(v) { return v.composite_score; }),
        text: fv.map(function(v) {
          return v.model_name + ' ' + v.quant + '<br>' +
                 'Score: ' + v.composite_score + '<br>' +
                 'Size: ' + v.file_size_gb + ' GB';
        }),
        hoverinfo: 'text',
        mode: 'markers',
        name: family,
        marker: {
          color: theme.colorForFamily(family),
          size: fv.map(function(v) { return v.quant === 'Q4_K_M' ? 12 : 7; }),
          opacity: fv.map(function(v) { return v.quant === 'Q4_K_M' ? 1.0 : 0.6; }),
          line: {
            color: fv.map(function(v) {
              return v.quant === 'Q4_K_M' ? '#ffffff' : 'rgba(0,0,0,0)';
            }),
            width: fv.map(function(v) { return v.quant === 'Q4_K_M' ? 2 : 0; })
          }
        }
      });
    });

    // Pareto frontier line
    var pareto = data.pareto_frontier;
    var paretoVariants = [];
    pareto.forEach(function(label) {
      for (var i = 0; i < variants.length; i++) {
        if (variants[i].model_name + ' ' + variants[i].quant === label) {
          paretoVariants.push(variants[i]);
          break;
        }
      }
    });

    if (paretoVariants.length > 1) {
      paretoVariants.sort(function(a, b) { return a.file_size_gb - b.file_size_gb; });
      traces.push({
        x: paretoVariants.map(function(v) { return v.file_size_gb; }),
        y: paretoVariants.map(function(v) { return v.composite_score; }),
        mode: 'lines',
        name: 'Pareto frontier',
        line: { color: theme.PARETO_COLOR, width: 2, dash: 'dash' },
        hoverinfo: 'skip',
        showlegend: true
      });
    }

    var layout = theme.mergeLayout({
      title: { text: 'Composite Score vs File Size' },
      xaxis: { title: { text: 'File Size (GB)' } },
      yaxis: { title: { text: 'Composite Score (%)' } },
      legend: { orientation: 'h', y: -0.15 }
    });

    Plotly.newPlot(div, traces, layout, theme.config);
  }

  function renderLeaderboard(data, theme) {
    var div = document.getElementById('chart-overview-leaderboard');
    if (!div) return;

    var variants = data.variants
      .filter(function(v) { return v.composite_score !== null; })
      .sort(function(a, b) { return b.composite_score - a.composite_score; })
      .slice(0, 10);

    // Reverse for horizontal bar (bottom to top)
    variants.reverse();

    var labels = variants.map(function(v) { return v.model_name + ' ' + v.quant; });
    var scores = variants.map(function(v) { return v.composite_score; });
    var colors = variants.map(function(v) { return theme.colorForFamily(v.family); });

    var trace = {
      x: scores,
      y: labels,
      type: 'bar',
      orientation: 'h',
      marker: { color: colors, line: { width: 0 } },
      text: scores.map(function(s) { return s.toFixed(1); }),
      textposition: 'outside',
      textfont: { color: '#e2e8f0', size: 12 },
      hoverinfo: 'x+y'
    };

    var layout = theme.mergeLayout({
      title: { text: 'Top 10 Variants by Composite Score' },
      xaxis: { title: { text: 'Composite Score (%)' }, range: [0, 80] },
      yaxis: { automargin: true, tickfont: { size: 11 } },
      margin: { l: 180, r: 60, t: 50, b: 50 },
      showlegend: false
    });

    Plotly.newPlot(div, [trace], layout, theme.config);
  }

  // MkDocs Material instant navigation compatibility
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() { render(); });
  } else {
    document.addEventListener('DOMContentLoaded', render);
  }
})();
