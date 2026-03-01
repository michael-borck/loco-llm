# Speed Analysis

Real-world inference speed on CPU-only hardware — the deployment target for LocoLLM users.

!!! note "Hardware"
    All speed benchmarks run with [llama-bench](https://github.com/ggml-org/llama.cpp) using **0 GPU layers** (pure CPU) to represent the experience on student laptops and Chromebooks. Prompt length: 512 tokens. Generation length: 128 tokens.

## Generation Speed by Variant

Tokens per second during generation (tg), sorted by speed. Higher is better. The usability threshold for interactive use is roughly **5 t/s** (marked with a dashed line).

<div id="chart-speed-generation" class="plotly-chart"></div>

## Time-to-First-Token vs File Size

TTFT measures how long a user waits before seeing the first response token. Smaller, more quantized models load and process prompts faster.

<div id="chart-speed-ttft" class="plotly-chart"></div>

---

## Key Observations

- **Quantization directly improves speed** — Q4_K_M models run 2-3x faster than BF16 on CPU
- **1B models** comfortably exceed 10 t/s at Q4_K_M on most hardware
- **4B models at Q4_K_M** hover around 4-6 t/s on CPU, borderline for interactive use
- **TTFT scales linearly** with file size for a given hardware class
- **Q4_0 vs Q4_K_M**: Q4_0 is slightly faster due to simpler dequantization, but Q4_K_M's quality advantage usually makes it the better choice

---

[:octicons-arrow-left-24: Quality Analysis](quality.md) · [:octicons-arrow-right-24: Bang per Bit](bang-per-bit.md)
