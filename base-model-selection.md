# Base Model Selection

This document explains how the standard base model is chosen, the rationale behind the current selection, and the external benchmarking resources used to inform the decision.

## Current Standard

**Model:** Qwen3-4B-Instruct
**Quantization:** Q4_K_M (GGUF format)
**RAM footprint:** ~2.5GB model + ~0.5GB runtime overhead
**Effective RAM requirement:** ~3.5GB (leaving headroom for OS and adapters on 8GB machines)
**Academic year:** 2026-2027

### Why Qwen3-4B?

The Qwen3-4B-Instruct model ranks first for post-fine-tuning performance across 8 diverse tasks in distil labs' systematic benchmark of 12 small models, outperforming even 8B models after LoRA training. It achieves this while staying within our 8GB RAM constraint in Q4_K_M quantization.

The most compelling finding for LocoLLM: the fine-tuned Qwen3-4B matched or exceeded a 120B+ teacher model on 7 of 8 benchmarks. On SQuAD 2.0, it beat the teacher by 19 percentage points. A 4B model, properly fine-tuned, can match a model 30x its size. That's the entire thesis of this project validated in someone else's data.

## The Tunability Inversion

One of the most important findings from recent small model research is that smaller models gain more from fine-tuning than larger ones. The distil labs benchmark showed the tunability ranking inverts the size hierarchy: Llama-3.2-1B and Qwen3-0.6B showed the largest improvements from fine-tuning, while 8B models gained the least (because they start stronger and have less room to improve).

This directly validates LocoLLM's architecture. We're not settling for small models as a compromise. We're exploiting the fact that small models are precisely the ones that benefit most from the kind of task-specific adaptation we're building. The adapter approach isn't compensating for a weakness; it's leveraging a strength unique to the small model class.

## Selection Criteria

The base model must satisfy all of the following:

### Hard Requirements

1. **Fits in 8GB RAM** with OS, runtime, and adapter loaded simultaneously. In practice this means the quantized model should be under 3GB.

2. **Instruction-tuned variant available.** We need a model that can follow instructions out of the box, not a raw pretrained model.

3. **GGUF format available** (or convertible) for Ollama compatibility.

4. **Permissive license** for academic use, redistribution, and modification. Apache 2.0, MIT, or equivalent. No "research only" restrictions.

5. **Active maintenance.** The model provider is actively developing the model family, releasing updates, and responding to community issues.

### Soft Preferences

6. **Strong fine-tuning response** (tunability). This matters more than raw base performance for LocoLLM, since every query goes through an adapter. A model that improves dramatically with LoRA training is more valuable than one that starts slightly stronger but plateaus.

7. **Good multilingual support.** Many of our students work in multiple languages.

8. **Large community.** More users means more documentation, tutorials, and LoRA examples to learn from.

9. **Compatible with standard training tools.** Works with HuggingFace PEFT, Unsloth, and other common LoRA training frameworks without special modifications.

## Benchmarking Resources

You don't have to guess how small models perform or infer from larger siblings. Dedicated benchmarking resources exist for the sub-7B class:

### External Leaderboards and Benchmarks

**HuggingFace Open LLM Leaderboard**
https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard

The standard community leaderboard for open models. Tests on IFEval, BBH, MATH, GPQA, MuSR, and MMLU-PRO. Filterable by model size, so you can compare models within a weight class rather than against 70B behemoths.

**Open LLM Leaderboard: Best Models by Size**
https://huggingface.co/collections/open-llm-leaderboard/open-llm-leaderboard-best-models

HuggingFace maintains a curated collection of the top-performing model at each parameter bucket (around 1B, 2B, 7B, 13B, etc.). Useful as a quick reference for what's currently winning at each weight class.

**distil labs: SLM Fine-Tuning Benchmark**
https://www.distillabs.ai/blog/we-benchmarked-12-small-language-models-across-8-tasks-to-find-the-best-base-model-for-fine-tuning

The most directly relevant resource for LocoLLM. Benchmarks 12 small models (0.1B to 8B) across 8 tasks, measuring both base performance and post-fine-tuning performance. This is where the tunability inversion finding comes from and where Qwen3-4B was identified as the top performer after fine-tuning.

**SLM-Bench (EMNLP 2025 Findings)**
https://aclanthology.org/2025.findings-emnlp.1165/

An academic benchmark specifically designed for small language models. Measures 11 metrics across correctness, computational efficiency, and energy consumption on 4 hardware configurations. Useful for understanding efficiency trade-offs, not just accuracy.

**Small Language Models: Survey, Measurements, and Insights**
https://arxiv.org/html/2409.15790v1

Comprehensive survey covering SLMs from 100M to 5B parameters. Includes inference latency measurements (first token time and decode latency per token), memory footprint analysis on actual hardware (including Jetson for edge deployment), and pre-training dataset quality comparisons. Essential reading for understanding what drives performance at this scale.

### How to Use These Resources

When evaluating a candidate base model for LocoLLM:

1. **Check the Open LLM Leaderboard** for its ranking within its size class on standard benchmarks
2. **Check distil labs** (or run your own version of their methodology) for fine-tuning response
3. **Check SLM-Bench** or the SLM survey for practical hardware measurements (latency, memory, energy)
4. **Run LocoLLM's own evaluation** on the specific task domains we care about (see Evaluation Process below)

No single benchmark tells the whole story, but together they give a much clearer picture than guessing from the parent model's performance.

## Evaluation Process

When selecting a new base model (typically annually), the following evaluation is performed:

### Step 1: Filter by Hard Requirements

Eliminate any model that doesn't meet all hard requirements. This usually reduces the field to 3-5 candidates.

### Step 2: Check External Benchmarks

Before running any local tests, review the external resources listed above. If a model performs poorly on the Open LLM Leaderboard for its size class, or shows weak tunability in distil labs' data, there's no need to spend time testing it locally.

### Step 3: Benchmark on LocoLLM Tasks

Run each remaining candidate on the existing LocoLLM benchmark suite (all adapter benchmarks combined, using only the base model without adapters). This gives a direct comparison of how well each candidate handles our specific task domains out of the box.

### Step 4: LoRA Trainability Test

Fine-tune a quick test adapter (using the math-reasoning training data) on each candidate. Compare:
- Training convergence speed
- Final benchmark score after identical training
- Adapter size

This is the most important step. Some models respond dramatically better to LoRA fine-tuning than others at the same parameter count. The distil labs data provides a starting point, but LocoLLM's task domains may differ.

### Step 5: Practical Testing

Install each candidate on the lowest-spec student laptop available and test:
- Time to first token
- Tokens per second
- Memory stability over long conversations
- Compatibility with Ollama on macOS, Windows, and Linux

## Model Comparison (2026 Evaluation)

| Model | Parameters | Est. Q4_K_M Size | License | Fine-Tuning Rank (distil labs) | Base Rank (distil labs) |
|---|---|---|---|---|---|
| **Qwen3-4B-Instruct** | 4B | ~2.5GB | Apache 2.0 | **#1** | #3 |
| Qwen3-1.7B | 1.7B | ~1.1GB | Apache 2.0 | #4 | #5 |
| Qwen3-0.6B | 0.6B | ~0.4GB | Apache 2.0 | #6 | #8 |
| Llama 3.2-3B-Instruct | 3.2B | ~2.0GB | Llama 3.2 Community | #5 | #6 |
| Llama 3.2-1B-Instruct | 1B | ~0.7GB | Llama 3.2 Community | #7 | #9 |
| Gemma 3-1B-it | 1B | ~0.7GB | Gemma License | #8 | #7 |
| SmolLM2-1.7B-Instruct | 1.7B | ~1.1GB | Apache 2.0 | #9 | #10 |

*Rankings sourced from distil labs benchmark (June 2025). LocoLLM-specific benchmarks to be added during Semester 2, 2026.*

## Why Not 7B?

A 7B model in Q4_K_M quantization requires approximately 4.5GB of RAM for the model alone. With OS overhead (1-2GB), Ollama runtime (~0.5GB), and an active LoRA adapter (~0.1GB), total usage reaches 6-7GB. This is technically possible on an 8GB machine but leaves almost no headroom, leading to:

- Swapping to disk under memory pressure (catastrophic for inference speed)
- Inability to run a web browser or other applications alongside LocoLLM
- Unreliable performance on machines with shared GPU memory (integrated graphics)

The 3-4B class provides a comfortable margin while still fitting on constrained hardware. And the tunability data shows that smaller models gain more from fine-tuning, so the gap between a 4B adapter-enhanced model and a 7B general model is narrower than the parameter count suggests.

## Why Not Smaller (1-2B)?

Models in the 1-2B range are tempting for their speed and tiny footprint, and the tunability data shows they gain the most from fine-tuning in relative terms. However, their absolute post-fine-tuning scores still trail the 4B class. The Qwen3-4B consistently produces the best fine-tuned results across diverse tasks.

That said, 1-2B models are worth considering for specific use cases:
- Chromebooks or tablets with 4GB RAM
- Situations where inference speed matters more than quality
- As a secondary "fast model" in a tiered routing setup

If hardware constraints force a smaller model, Llama-3.2-1B-Instruct shows the highest tunability and Qwen3-1.7B offers the best balance of size and post-fine-tuning quality below 2B.

## Future: 1.58-Bit Native Models (Research Track)

The most significant development on the horizon for LocoLLM is 1.58-bit native quantization, primarily through Microsoft's BitNet architecture and models built on it.

### What Is 1.58-Bit?

Unlike post-training quantization (where you train a model in full precision then compress it), BitNet models are trained natively with ternary weights: every weight is -1, 0, or +1. This is 1.58 bits per parameter (log2(3)). Because the model learns to work within these constraints from the start, it avoids the quality loss that comes from compressing a model after the fact.

### Why It Matters for LocoLLM

The numbers are transformative for the digital divide thesis:

| Metric | Qwen3-4B (Q4_K_M) | BitNet b1.58 2B4T |
|---|---|---|
| Model size on disk | ~2.5GB | ~0.4GB |
| RAM usage | ~3.5GB | ~0.8GB |
| Inference speed (CPU) | 15-30 tok/s | ~6 tok/s (unoptimized) |
| Energy per inference | ~35W | ~10W |
| Minimum viable hardware | 8GB RAM laptop | Raspberry Pi 5 / 4GB Chromebook |

A 0.4GB model running on a Raspberry Pi at human reading speed opens LocoLLM to an entirely different population of users: students in developing regions, schools with no laptop budget, offline kiosks, phone-based access.

### Current Limitations

**LoRA incompatibility.** Standard LoRA adapters attach to nn.Linear layers. BitNet replaces these with BitLinear layers that use ternary weights. The two architectures are fundamentally incompatible. Emerging solutions:

- **BitLoRA** (2025): A modified PEFT method designed specifically for BitLinear layers. All adapter weights also operate in ternary. Early results are promising but the tooling is not yet production-ready.
- **Falcon-Edge** (TII, 2025): 1B and 3B models pre-trained natively in 1.58-bit format with a training paradigm specifically designed to support fine-tuning. Available in both BitNet and bfloat16 variants from the same training run.
- **BitDistill** (2025): A framework for distilling existing full-precision models into 1.58-bit BitNet format with performance comparable to the original. Three-stage process: modeling refinement, continued pre-training, and attention distillation.
- **HuggingFace 1.58-bit fine-tuning**: HuggingFace demonstrated that existing models can be gradually fine-tuned down to 1.58-bit using warmup quantization techniques, though results are not yet as strong as native pre-training.

**No Ollama support.** BitNet models require Microsoft's bitnet.cpp inference runtime or specialized kernels. They cannot currently run through Ollama or standard llama.cpp. This means a separate installation path and a different user experience.

**Limited model selection.** As of mid-2025, the available natively-trained 1.58-bit models are: BitNet b1.58 2B4T (Microsoft), Falcon-Edge 1B/3B (TII), and a handful of community experiments. The selection will grow, but it's thin compared to the hundreds of 4-bit quantized models available.

**4K context length.** BitNet b1.58 2B4T has a maximum context of 4,096 tokens. This limits use cases that require longer context windows. Long-context fine-tuning is recommended but adds complexity.

### Planned Research Track (Phase 3+)

LocoLLM's architecture is designed to be base-model-agnostic. The router, evaluation harness, benchmarks, and adapter submission process all work regardless of the underlying model's precision format. This means we can run a parallel track:

**Semester 3 project: "LocoLLM-1bit"**

A student team ports the LocoLLM framework to a 1.58-bit base (Falcon-Edge 3B or successor), adapts the fine-tuning pipeline to use BitLoRA or Falcon-Edge's native fine-tuning approach, and benchmarks the same task domains at both precisions.

Research questions:
- Does routed 1.58-bit task specialization close the gap to 4-bit general models?
- What is the quality/memory/speed trade-off curve across precisions for the same tasks?
- Which task domains are most and least sensitive to extreme quantization?
- Is the tunability inversion (smaller models gain more from fine-tuning) even more pronounced at 1.58-bit?

This comparison, done rigorously on the same task benchmarks, would be a novel contribution. Nobody has published routed multi-adapter evaluation at 1.58-bit precision.

### Decision Framework: When to Switch

LocoLLM should consider making 1.58-bit the default pathway when:

1. At least one 1.58-bit base model exists at 3-4B parameters with competitive benchmark scores
2. A LoRA-compatible fine-tuning method (BitLoRA or equivalent) is available through standard tooling (HuggingFace PEFT or similar)
3. An inference runtime works cross-platform (macOS, Windows, Linux) with a user experience comparable to Ollama
4. Our own benchmarks confirm that routed 1.58-bit adapters achieve at least 80% of the quality of routed 4-bit adapters on LocoLLM task domains

Until those conditions are met, 4-bit remains the production default and 1.58-bit remains a research track.

### Key References

- **BitNet b1.58 model**: https://huggingface.co/microsoft/bitnet-b1.58-2B-4T
- **bitnet.cpp inference runtime**: https://github.com/microsoft/BitNet
- **Falcon-Edge (fine-tunable 1.58-bit)**: https://falcon-lm.github.io/blog/falcon-edge/
- **HuggingFace 1.58-bit fine-tuning guide**: https://huggingface.co/blog/1_58_llm_extreme_quantization
- **BitLoRA paper (adapter tuning for 1.58-bit)**: https://www.sciencedirect.com/science/article/abs/pii/S0957417426003106
- **BitDistill (distillation to 1.58-bit)**: https://arxiv.org/html/2510.13998v1

## Changing the Base Model

A base model change affects the entire ecosystem. All existing adapters must be verified or retrained. This is a significant community effort, so changes should be:

- **Infrequent:** Once per academic year at most
- **Well-justified:** The new model must be meaningfully better, not just marginally
- **Planned:** Announce at least one semester in advance so teams can prepare
- **Backwards-compatible:** Maintain the previous model as a fallback for one semester

### Migration Process

1. Announce candidate model and rationale
2. Run full evaluation (Steps 1-5 above)
3. Test representative adapters from the current ecosystem on the new base
4. If adapters transfer well: publish conversion guide
5. If adapters don't transfer: coordinate retraining effort
6. Update all documentation, templates, and training scripts
7. Old base model remains supported for one additional semester
