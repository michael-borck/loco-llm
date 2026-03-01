# Quality Analysis

Detailed quality benchmarks across 5 standard tasks from the Open LLM Leaderboard, comparing all 14 models at every quantization level.

!!! note "Evaluation Framework"
    All scores are produced by [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) using GGUF models. Metrics are accuracy (%) for MMLU, HellaSwag, ARC-Challenge; exact match for GSM8K; MC2 for TruthfulQA.

## Per-Task Comparison at Q4_K_M

Q4_K_M is LocoLLM's default quantization level. This chart shows how all 14 models compare across each task at that single quant level.

<div id="chart-quality-tasks" class="plotly-chart"></div>

## Quantization Degradation Curves

How does quality change as you reduce precision? Each line represents one model family. The x-axis is bits per weight (BF16=16 down to Q2_K=2.6). Steeper drops indicate higher quantization sensitivity.

<div id="chart-quality-degradation" class="plotly-chart"></div>

---

## Key Observations

- **Knowledge tasks (MMLU)** degrade fastest under quantization — factual recall is stored in weights and compressed away first
- **Commonsense reasoning (HellaSwag)** is most robust, retaining 95%+ of BF16 quality even at Q4_0
- **Math reasoning (GSM8K)** shows a sharp cliff below Q3_K_M for most models
- **Larger models** (4B+) tolerate quantization better than 1B models at the same bpw
- **The quantization cliff** typically appears between Q3_K_M (3.4 bpw) and Q2_K (2.6 bpw)

---

[:octicons-arrow-left-24: Back to Overview](index.md) · [:octicons-arrow-right-24: Speed Analysis](speed.md)
