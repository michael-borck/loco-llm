---
title: "Benchmark Results"
---

## Base Model Benchmarks

LocoLLM's base model (Qwen3-4B at Q4_K_M) was selected using data from [LocoBench](https://github.com/michael-borck/loco-bench), which evaluates small language models across standard tasks at multiple quantization levels. The key finding that shaped our choice:

!!! tip "The Sweet Spot"
    Q4_K_M consistently retains **90-95% of BF16 quality** at roughly **30% of the file size**. Below Q3_K_M, quality collapses sharply for knowledge-heavy tasks.

For the full data, interactive charts, and methodology, see [LocoBench](https://locobench.org/).

## Adapter Benchmarks

Each adapter is evaluated against the base model on its own domain:

```bash
uv run loco eval math
```

This runs both `qwen3:4b` and `locollm-math` on the same evaluation dataset and prints a side-by-side comparison. See the [benchmarking guide](../benchmarking-guide.md) for details on scoring modes and what's planned.

Adapter benchmark results will be published here as adapters are validated.
