# Benchmark Results

LocoLLM uses benchmark data from [smol-bench](https://github.com/michael-borck/smol-bench) — a standalone project that systematically evaluates **14 models** across **8 quantization levels** (112 variants) on consumer hardware.

The benchmarking work was separated into its own project because:

- The data has value independent of LocoLLM's adapter/routing architecture
- It can be cited and used by other researchers regardless of whether they use LocoLLM
- It keeps LocoLLM focused on adapters, routing, and the teaching framework

## Key Findings

!!! tip "The Sweet Spot"
    Q4_K_M consistently retains **90-95% of BF16 quality** at roughly **30% of the file size**. Below Q3_K_M, quality collapses sharply for knowledge-heavy tasks.

- **Knowledge tasks (MMLU)** degrade fastest under quantization — factual recall is stored in weights and compressed away first
- **Commonsense reasoning (HellaSwag)** is most robust, retaining 95%+ of BF16 quality even at Q4_0
- **Math reasoning (GSM8K)** shows a sharp cliff below Q3_K_M for most models
- **4B models at Q4_K_M** hover around 4-6 t/s on CPU, borderline for interactive use
- **1B-1.7B models at Q4_K_M** are the speed sweet spot on CPU-only hardware (>10 t/s)

These findings directly inform LocoLLM's [base model selection](../base-model-selection.md) and the annual ADR process.

## Explore the Full Data

The interactive charts, detailed analysis, and raw data live in smol-bench:

| Resource | What It Covers |
|----------|---------------|
| [Quality Analysis](https://michael-borck.github.io/smol-bench/quality/) | Per-task scores and quantization degradation curves |
| [Speed Analysis](https://michael-borck.github.io/smol-bench/speed/) | Generation speed, prompt processing, time-to-first-token |
| [Bang per Bit](https://michael-borck.github.io/smol-bench/bang-per-bit/) | Pareto efficiency frontiers and tradeoffs |
| [Benchmarking Guide](https://michael-borck.github.io/smol-bench/guide/) | Full methodology, tools, and how to contribute |
| [GitHub Repository](https://github.com/michael-borck/smol-bench) | Scripts, raw results, and documentation source |

## How LocoLLM Uses This Data

1. **Base model selection** — the annual ADR process references smol-bench rankings at Q4_K_M
2. **Quantization validation** — confirming Q4_K_M retains sufficient quality for adapter fine-tuning
3. **Adapter impact measurement** — comparing fine-tuned adapter scores against smol-bench baselines
4. **Deployment guidance** — recommending hardware configurations based on speed/quality tradeoffs
