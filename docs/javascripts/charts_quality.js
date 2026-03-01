// Quality page charts: Per-Task Comparison + Degradation Curves
(function() {
  'use strict';

  function render() {
    if (!window.BENCHMARK_DATA || !window.LOCOLLM_CHART_THEME) return;

    var data = window.BENCHMARK_DATA;
    var theme = window.LOCOLLM_CHART_THEME;

    renderTaskComparison(data, theme);
    renderDegradation(data, theme);
  }

  function renderTaskComparison(data, theme) {
    var div = document.getElementById('chart-quality-tasks');
    if (!div) return;

    // Filter to Q4_K_M only
    var q4km = data.variants.filter(function(v) { return v.quant === 'Q4_K_M'; });
    // Sort by composite score descending
    q4km.sort(function(a, b) { return b.composite_score - a.composite_score; });

    var models = q4km.map(function(v) { return v.model_name; });
    var tasks = data.tasks;

    var taskLabels = {
      mmlu: 'MMLU',
      hellaswag: 'HellaSwag',
      gsm8k: 'GSM8K',
      truthfulqa: 'TruthfulQA',
      arc_challenge: 'ARC-Challenge'
    };

    var traces = tasks.map(function(task, i) {
      return {
        x: models,
        y: q4km.map(function(v) { return v.scores[task]; }),
        name: taskLabels[task] || task,
        type: 'bar',
        marker: { color: theme.colorForIndex(i) }
      };
    });

    var layout = theme.mergeLayout({
      title: { text: 'Per-Task Scores at Q4_K_M' },
      barmode: 'group',
      xaxis: { tickangle: -35, automargin: true },
      yaxis: { title: { text: 'Score (%)' }, range: [0, 85] },
      legend: { orientation: 'h', y: -0.25 },
      margin: { b: 120 }
    });

    Plotly.newPlot(div, traces, layout, theme.config);
  }

  function renderDegradation(data, theme) {
    var div = document.getElementById('chart-quality-degradation');
    if (!div) return;

    // Group variants by model, compute average score at each quant level
    var models = {};
    data.variants.forEach(function(v) {
      if (!models[v.model_id]) {
        models[v.model_id] = { name: v.model_name, family: v.family, quants: {} };
      }
      models[v.model_id].quants[v.quant] = v.composite_score;
    });

    // Sort quant levels by bpw descending (BF16 first)
    var quantOrder = data.quant_levels.slice().reverse();
    var bpwValues = quantOrder.map(function(q) { return data.quant_meta[q].bpw; });

    var traces = [];
    Object.keys(models).forEach(function(modelId) {
      var m = models[modelId];
      var scores = quantOrder.map(function(q) { return m.quants[q] || null; });

      traces.push({
        x: bpwValues,
        y: scores,
        name: m.name,
        mode: 'lines+markers',
        line: { color: theme.colorForFamily(m.family), width: 2 },
        marker: { size: 5 },
        hovertemplate: m.name + '<br>%{x:.1f} bpw: %{y:.1f}%<extra></extra>'
      });
    });

    var layout = theme.mergeLayout({
      title: { text: 'Composite Score vs Bits per Weight' },
      xaxis: {
        title: { text: 'Bits per Weight' },
        autorange: 'reversed',
        dtick: 2
      },
      yaxis: { title: { text: 'Composite Score (%)' }, range: [15, 75] },
      legend: {
        orientation: 'v',
        x: 1.02,
        y: 1,
        font: { size: 10 }
      },
      margin: { r: 160 }
    });

    Plotly.newPlot(div, traces, layout, theme.config);
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() { render(); });
  } else {
    document.addEventListener('DOMContentLoaded', render);
  }
})();
