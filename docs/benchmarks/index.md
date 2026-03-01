# Benchmark Results

LocoLLM benchmarks **14 models** across **8 quantization levels** (112 variants) to answer one question: *which small, quantized model gives you the most capability per byte?*

!!! info "Sample Data"
    These charts currently show **simulated data** generated with realistic degradation curves. They will be replaced with real benchmark results once the full evaluation matrix completes.

!!! tip "Key Finding"
    Q4_K_M consistently sits in the efficiency sweet spot — retaining 90-95% of BF16 quality at ~30% of the file size. Below Q3_K_M, quality collapses sharply for knowledge-heavy tasks.

## Composite Score vs File Size

Each point is one model at one quantization level. The **orange line** traces the Pareto frontier — the best quality achievable at each file size. Points above and to the left are more efficient.

<div id="chart-overview-scatter" class="plotly-chart"></div>

## Top 10 Variants by Composite Score

Composite score averages across MMLU, HellaSwag, GSM8K, TruthfulQA, and ARC-Challenge.

<div id="chart-overview-leaderboard" class="plotly-chart"></div>

---

## Explore the Details

<div class="grid cards" markdown>

-   **Quality Analysis**

    ---

    Per-task scores and quantization degradation curves.

    [:octicons-arrow-right-24: Quality](quality.md)

-   **Speed Analysis**

    ---

    Generation speed, prompt processing, and time-to-first-token.

    [:octicons-arrow-right-24: Speed](speed.md)

-   **Bang per Bit**

    ---

    Pareto efficiency, quality-speed tradeoffs, and task sensitivity.

    [:octicons-arrow-right-24: Bang per Bit](bang-per-bit.md)

</div>

---

**Methodology:** All quality benchmarks use [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness). Speed benchmarks use [llama-bench](https://github.com/ggml-org/llama.cpp) on CPU-only (0 GPU layers). See the [Benchmarking Guide](../benchmarking-guide.md) for full details.
