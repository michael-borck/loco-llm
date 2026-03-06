---
title: "Benchmarking Guide"
---

How LocoLLM adapters are evaluated and how the results fit into the bigger picture.

## What `loco eval` Does Today

The evaluation harness compares an adapter against the base model on the adapter's own evaluation dataset:

```bash
uv run loco eval math
```

This runs both `qwen3:4b` (base) and `locollm-math` (adapter) on the problems in `adapters/math/eval_dataset.jsonl` and prints a side-by-side score.

Three scoring modes are supported, configured per adapter in `registry.yaml` via the `eval_type` field:

| eval_type | How it scores | Used by |
|-----------|---------------|---------|
| `numeric` | Extract a number from the response, compare to expected answer | math |
| `code` | Check valid Python syntax + expected keywords present | code |
| `analysis` | Check that the expected answer string appears in the response | analysis |

Each adapter must include at least 50 evaluation examples. See [evaluation standards](evaluation-standards.md) for benchmark construction guidelines.

## What's Not Implemented Yet

The following are documented in [evaluation standards](evaluation-standards.md) as requirements but are not yet built into the harness. Each is a student project:

- **Out-of-domain check** — run your adapter on another domain's benchmark to verify it doesn't degrade general capability. The eval-standards doc specifies within 5 percentage points of base.
- **Cross-model comparison** — run the same benchmark against other quantized models (e.g., does our fine-tuned Qwen3-4B beat a stock Phi-3-mini at Q4_K_M on math?). This would answer whether fine-tuning is better than just picking a different base model.
- **Frontier API comparison** — run the benchmark against GPT-4 / Claude / Gemini to establish an upper bound. Answers the central research question: how close can routed 4-bit specialists get?
- **Structured results output** — `results.json` with per-difficulty breakdowns, hardware info, inference settings, and version history.
- **LLM-as-judge scoring** — for domains like writing where exact match doesn't apply.
- **Deterministic inference settings** — temperature 0, fixed max_tokens, enforced by the harness rather than relying on Ollama defaults.

## How smol-bench Informed Base Model Selection

The base model (Qwen3-4B at Q4_K_M) was selected using data from [smol-bench](https://github.com/michael-borck/smol-bench), an independent benchmarking project that evaluates small language models across standard tasks (MMLU, GSM8K, HellaSwag, etc.) at multiple quantization levels on consumer hardware. The selection rationale is documented in [ADR-0001](adr/0001-base-model-qwen3-4b.md) and [base model selection](base-model-selection.md).

smol-bench and LocoLLM are separate projects. smol-bench benchmarks base models. LocoLLM benchmarks what fine-tuning adds on top.
