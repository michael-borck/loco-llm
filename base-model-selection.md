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
