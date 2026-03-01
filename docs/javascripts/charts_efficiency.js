// Efficiency page charts: Pareto Frontier, Quality vs Speed Bubble, Task Sensitivity Heatmap
(function() {
  'use strict';

  function render() {
    if (!window.BENCHMARK_DATA || !window.LOCOLLM_CHART_THEME) return;

    var data = window.BENCHMARK_DATA;
    var theme = window.LOCOLLM_CHART_THEME;

    renderPareto(data, theme);
    renderBubble(data, theme);
    renderHeatmap(data, theme);
  }

  function renderPareto(data, theme) {
    var div = document.getElementById('chart-efficiency-pareto');
    if (!div) return;

    var variants = data.variants.filter(function(v) {
      return v.composite_score !== null && v.file_size_gb !== null;
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
        y: fv.map(function(v) { return v.composite_score; }),
        text: fv.map(function(v) {
          return v.model_name + ' ' + v.quant +
                 '<br>Score: ' + v.composite_score +
                 '<br>Size: ' + v.file_size_gb + ' GB' +
                 '<br>bpw: ' + v.bpw;
        }),
        hoverinfo: 'text',
        mode: 'markers',
        name: family,
        marker: {
          color: theme.colorForFamily(family),
          size: 7,
          opacity: 0.5
        }
      });
    });

    // Pareto frontier line with labels
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
        text: paretoVariants.map(function(v) { return v.model_name + ' ' + v.quant; }),
        mode: 'lines+markers+text',
        name: 'Pareto frontier',
        line: { color: theme.PARETO_COLOR, width: 3 },
        marker: { color: theme.PARETO_COLOR, size: 10, symbol: 'diamond' },
        textposition: 'top right',
        textfont: { color: theme.PARETO_COLOR, size: 9 },
        hovertemplate: '%{text}<br>Score: %{y:.1f}<br>Size: %{x:.2f} GB<extra>Pareto</extra>'
      });
    }

    var layout = theme.mergeLayout({
      title: { text: 'Pareto Frontier: Quality vs File Size' },
      xaxis: { title: { text: 'File Size (GB)' } },
      yaxis: { title: { text: 'Composite Score (%)' } },
      legend: { orientation: 'h', y: -0.15 }
    });

    Plotly.newPlot(div, traces, layout, theme.config);
  }

  function renderBubble(data, theme) {
    var div = document.getElementById('chart-efficiency-bubble');
    if (!div) return;

    // Q4_K_M variants only for clarity
    var variants = data.variants.filter(function(v) {
      return v.quant === 'Q4_K_M' && v.tg_ts !== null && v.composite_score !== null;
    });

    var maxSize = Math.max.apply(null, variants.map(function(v) { return v.file_size_gb; }));

    var trace = {
      x: variants.map(function(v) { return v.tg_ts; }),
      y: variants.map(function(v) { return v.composite_score; }),
      text: variants.map(function(v) {
        return v.model_name + '<br>' +
               v.tg_ts + ' t/s | Score: ' + v.composite_score +
               '<br>Size: ' + v.file_size_gb + ' GB';
      }),
      hoverinfo: 'text',
      mode: 'markers+text',
      textposition: 'top center',
      textfont: { size: 9, color: '#94a3b8' },
      marker: {
        size: variants.map(function(v) { return 15 + (v.file_size_gb / maxSize) * 35; }),
        color: variants.map(function(v) { return theme.colorForFamily(v.family); }),
        opacity: 0.7,
        line: { color: '#1e1e23', width: 1 }
      },
      // Use model names as text labels
      texttemplate: variants.map(function(v) { return v.model_name; })
    };

    var layout = theme.mergeLayout({
      title: { text: 'Quality vs Speed (Q4_K_M, bubble size = file size)' },
      xaxis: { title: { text: 'Generation Speed (t/s)' } },
      yaxis: { title: { text: 'Composite Score (%)' } },
      showlegend: false,
      margin: { t: 50, b: 60 }
    });

    Plotly.newPlot(div, [trace], layout, theme.config);
  }

  function renderHeatmap(data, theme) {
    var div = document.getElementById('chart-efficiency-heatmap');
    if (!div) return;

    var tasks = data.tasks;
    var quantLevels = data.quant_levels.filter(function(q) { return q !== 'BF16'; });

    var taskLabels = {
      mmlu: 'MMLU',
      hellaswag: 'HellaSwag',
      gsm8k: 'GSM8K',
      truthfulqa: 'TruthfulQA',
      arc_challenge: 'ARC-Challenge'
    };

    // For each task x quant, compute average % of BF16 retained across all models
    var z = [];
    var hoverText = [];

    quantLevels.forEach(function(quant) {
      var row = [];
      var hoverRow = [];

      tasks.forEach(function(task) {
        var ratios = [];

        data.models.forEach(function(modelId) {
          var bf16 = null;
          var quantVar = null;

          for (var i = 0; i < data.variants.length; i++) {
            var v = data.variants[i];
            if (v.model_id === modelId && v.quant === 'BF16') bf16 = v;
            if (v.model_id === modelId && v.quant === quant) quantVar = v;
          }

          if (bf16 && quantVar && bf16.scores[task] && quantVar.scores[task]) {
            ratios.push(quantVar.scores[task] / bf16.scores[task] * 100);
          }
        });

        var avg = ratios.length > 0
          ? Math.round(ratios.reduce(function(a, b) { return a + b; }, 0) / ratios.length)
          : null;

        row.push(avg);
        hoverRow.push(quant + ' / ' + (taskLabels[task] || task) + '<br>' +
                       (avg !== null ? avg + '% of BF16' : 'no data'));
      });

      z.push(row);
      hoverText.push(hoverRow);
    });

    var trace = {
      z: z,
      x: tasks.map(function(t) { return taskLabels[t] || t; }),
      y: quantLevels,
      type: 'heatmap',
      colorscale: [
        [0, '#7f1d1d'],     // deep red (bad)
        [0.5, '#78350f'],   // amber
        [0.85, '#365314'],  // green
        [1, '#166534']      // bright green (good)
      ],
      zmin: 60,
      zmax: 102,
      text: hoverText,
      hoverinfo: 'text',
      colorbar: {
        title: { text: '% of BF16', font: { color: '#94a3b8', size: 11 } },
        tickfont: { color: '#94a3b8' },
        ticksuffix: '%'
      }
    };

    // Add text annotations showing values
    var annotations = [];
    for (var i = 0; i < quantLevels.length; i++) {
      for (var j = 0; j < tasks.length; j++) {
        var val = z[i][j];
        if (val !== null) {
          annotations.push({
            x: taskLabels[tasks[j]] || tasks[j],
            y: quantLevels[i],
            text: val + '%',
            showarrow: false,
            font: { color: val < 80 ? '#fca5a5' : '#e2e8f0', size: 12 }
          });
        }
      }
    }

    var layout = theme.mergeLayout({
      title: { text: 'Quality Retained vs BF16 (averaged across models)' },
      xaxis: { side: 'bottom', tickfont: { size: 12 } },
      yaxis: { autorange: 'reversed', tickfont: { size: 11 } },
      annotations: annotations,
      margin: { l: 80, r: 100, t: 50, b: 80 }
    });

    Plotly.newPlot(div, [trace], layout, theme.config);
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() { render(); });
  } else {
    document.addEventListener('DOMContentLoaded', render);
  }
})();
