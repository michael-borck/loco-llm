# Bang per Bit

The core analysis: **how much capability do you get per byte of model weight?** This is the question that matters for deployment on constrained hardware. A 1B model at Q8_0 and a 4B model at Q2_K might be similar sizes — but which one is actually better?

!!! tip "The Pareto Frontier"
    The Pareto frontier represents the **efficient set** — model+quant combinations where you can't improve quality without increasing size, and can't reduce size without losing quality. Every point *on* the frontier is optimal; every point *below* it is dominated by something smaller or better.

## Pareto Frontier: Quality vs Size

The scatter shows all 112 variants. The frontier (orange line) highlights the optimal choices at each size budget.

<div id="chart-efficiency-pareto" class="plotly-chart"></div>

## Quality vs Speed Tradeoff

Can you have both quality *and* speed? This bubble chart plots generation speed against composite quality, with bubble size proportional to file size.

<div id="chart-efficiency-bubble" class="plotly-chart"></div>

## Task Sensitivity to Quantization

Which tasks suffer most from quantization? This heatmap shows the percentage of BF16 quality retained at each quantization level, averaged across all models.

<div id="chart-efficiency-heatmap" class="plotly-chart"></div>

---

## Takeaways for Model Selection

1. **If you have 2+ GB of RAM**: A 4B model at Q4_K_M (e.g., Qwen3-4B) is almost always the best choice — it sits on or near the Pareto frontier for quality/size
2. **If you have < 1.5 GB**: A 1.7B model at Q4_K_M outperforms a 4B model at Q2_K despite being the same size
3. **For math/reasoning tasks**: Prefer larger models at moderate quantization over smaller models at high precision — reasoning ability scales with parameters, not precision
4. **For interactive use (>5 t/s)**: 1B-1.7B models at Q4_K_M are the sweet spot on CPU-only hardware
5. **Never use Q2_K in production**: Quality collapses across the board; it's useful only as a lower bound for analysis

---

[:octicons-arrow-left-24: Speed Analysis](speed.md) · [:octicons-arrow-right-24: Benchmarking Guide](../benchmarking-guide.md)
