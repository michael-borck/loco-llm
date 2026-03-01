// Shared Plotly theme for LocoLLM benchmark charts
// Matches the site's dark slate + orange palette
window.LOCOLLM_CHART_THEME = (function() {
  'use strict';

  // 14-color palette for model families (colorblind-friendly, distinct on dark bg)
  var MODEL_COLORS = {
    'Qwen':      '#f97316',  // orange (brand)
    'Llama':     '#38bdf8',  // sky blue
    'Phi':       '#a78bfa',  // violet
    'Gemma':     '#34d399',  // emerald
    'DeepSeek':  '#fb7185',  // rose
    'SmolLM':    '#facc15',  // yellow
    'Mistral':   '#2dd4bf',  // teal
    'TinyLlama': '#94a3b8',  // slate
  };

  // Per-model colors when we need individual model distinction
  var INDIVIDUAL_COLORS = [
    '#f97316', '#38bdf8', '#a78bfa', '#34d399', '#fb7185',
    '#facc15', '#2dd4bf', '#94a3b8', '#f472b6', '#818cf8',
    '#4ade80', '#fbbf24', '#67e8f9', '#c084fc'
  ];

  var layout = {
    paper_bgcolor: '#0a0a0b',
    plot_bgcolor: '#111114',
    font: {
      family: 'DM Sans, system-ui, sans-serif',
      color: '#e2e8f0',
      size: 13
    },
    title: {
      font: { size: 18, color: '#f8fafc' },
      x: 0.02,
      xanchor: 'left'
    },
    xaxis: {
      gridcolor: '#1e1e23',
      zerolinecolor: '#2a2a30',
      linecolor: '#1e1e23',
      tickfont: { size: 11, color: '#94a3b8' },
      title: { font: { size: 13, color: '#94a3b8' } }
    },
    yaxis: {
      gridcolor: '#1e1e23',
      zerolinecolor: '#2a2a30',
      linecolor: '#1e1e23',
      tickfont: { size: 11, color: '#94a3b8' },
      title: { font: { size: 13, color: '#94a3b8' } }
    },
    legend: {
      bgcolor: 'rgba(17,17,20,0.9)',
      bordercolor: '#1e1e23',
      borderwidth: 1,
      font: { size: 11, color: '#cbd5e1' }
    },
    margin: { l: 60, r: 30, t: 50, b: 60 },
    hoverlabel: {
      bgcolor: '#16161a',
      bordercolor: '#2a2a30',
      font: { family: 'DM Sans, system-ui, sans-serif', size: 12, color: '#f8fafc' }
    }
  };

  var config = {
    responsive: true,
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      scale: 2,
      filename: 'locollm-benchmark'
    },
    modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
  };

  function mergeLayout(overrides) {
    var merged = JSON.parse(JSON.stringify(layout));
    for (var key in overrides) {
      if (typeof overrides[key] === 'object' && !Array.isArray(overrides[key]) && merged[key]) {
        for (var sub in overrides[key]) {
          merged[key][sub] = overrides[key][sub];
        }
      } else {
        merged[key] = overrides[key];
      }
    }
    return merged;
  }

  function colorForFamily(family) {
    return MODEL_COLORS[family] || '#94a3b8';
  }

  function colorForIndex(i) {
    return INDIVIDUAL_COLORS[i % INDIVIDUAL_COLORS.length];
  }

  return {
    layout: layout,
    config: config,
    MODEL_COLORS: MODEL_COLORS,
    INDIVIDUAL_COLORS: INDIVIDUAL_COLORS,
    mergeLayout: mergeLayout,
    colorForFamily: colorForFamily,
    colorForIndex: colorForIndex,
    ORANGE: '#f97316',
    PARETO_COLOR: '#f97316'
  };
})();
