# Benchmarking Guide

!!! note "Moved to smol-bench"
    The full benchmarking methodology, test matrix, and tooling guide have been moved to [smol-bench](https://github.com/michael-borck/smol-bench) — a standalone benchmarking project that LocoLLM uses as its data source.

    **Full guide:** [smol-bench Benchmarking Guide](https://michael-borck.github.io/smol-bench/guide/)

## Why a Separate Project?

The benchmarking work has a different audience, a different publication path, and a different lifespan than LocoLLM:

- **The benchmark data is independently citable.** Other researchers can use it regardless of whether they care about LocoLLM's routing approach.
- **The data's credibility is stronger when independent.** It is not tied to a project that is also advocating for a specific architecture.
- **Updates to the benchmark matrix** (new models, new quant levels) are decoupled from adapter/router development.

## What smol-bench Covers

- **14 models x 8 quantization levels** = 112 variants
- **Standard tasks:** MMLU, HellaSwag, GSM8K, TruthfulQA, ARC-Challenge
- **Speed metrics:** tokens/sec, time-to-first-token, peak RAM usage
- **"Bang per bit" analysis:** Pareto efficiency frontiers for constrained hardware
- **Consumer hardware focus:** Results on RTX 2060, CPU-only laptops, and secondhand machines

## How LocoLLM Uses smol-bench

LocoLLM consumes smol-bench data to:

1. **Select the base model** — the annual ADR process references smol-bench rankings at Q4_K_M
2. **Validate quantization choices** — confirming that Q4_K_M retains sufficient quality for adapter fine-tuning
3. **Measure adapter impact** — comparing fine-tuned adapter scores against smol-bench base model baselines
4. **Inform the benchmarks section** of the LocoLLM documentation site

## Quick Start

To run a quick benchmark yourself:

```bash
pip install lm-eval[hf]

lm_eval --model hf \
  --model_args pretrained=/path/to/gguf/,gguf_file=qwen3-4b-q4_k_m.gguf,tokenizer=Qwen/Qwen3-4B-Instruct \
  --tasks mmlu,gsm8k,hellaswag \
  --device cuda:0 \
  --batch_size auto \
  --output_path results/qwen3-4b-q4_k_m/
```

For the full methodology, hardware recommendations, and tiered evaluation approach, see the [smol-bench guide](https://michael-borck.github.io/smol-bench/guide/).
