# Base Model Selection

This document explains how the standard base model is chosen and the rationale behind the current selection.

## Current Standard

**Model:** Qwen2.5-3B-Instruct
**Quantization:** Q4_K_M (GGUF format)
**RAM footprint:** ~2.0GB model + ~0.5GB runtime overhead
**Effective RAM requirement:** ~3GB (leaving headroom for OS and adapters on 8GB machines)
**Academic year:** 2026-2027

## Selection Criteria

The base model must satisfy all of the following:

### Hard Requirements

1. **Fits in 8GB RAM** with OS, runtime, and adapter loaded simultaneously. In practice this means the quantized model should be under 2.5GB.

2. **Instruction-tuned variant available.** We need a model that can follow instructions out of the box, not a raw pretrained model.

3. **GGUF format available** (or convertible) for Ollama compatibility.

4. **Permissive license** for academic use, redistribution, and modification. Apache 2.0, MIT, or equivalent. No "research only" restrictions.

5. **Active maintenance.** The model provider is actively developing the model family, releasing updates, and responding to community issues.

### Soft Preferences

6. **Strong baseline capability** relative to parameter count. Better base = better floor for adapters.

7. **Good multilingual support.** Many of our students work in multiple languages.

8. **Large community.** More users means more documentation, tutorials, and LoRA examples to learn from.

9. **Compatible with standard training tools.** Works with HuggingFace PEFT, Unsloth, and other common LoRA training frameworks without special modifications.

## Evaluation Process

When selecting a new base model (typically annually), the following evaluation is performed:

### Step 1: Filter by Hard Requirements

Eliminate any model that doesn't meet all hard requirements. This usually reduces the field to 3-5 candidates.

### Step 2: Benchmark on LocoLLM Tasks

Run each candidate on the existing LocoLLM benchmark suite (all adapter benchmarks combined, using only the base model without adapters). This gives a direct comparison of how well each candidate handles our specific task domains out of the box.

### Step 3: LoRA Trainability Test

Fine-tune a quick test adapter (using the math-reasoning training data) on each candidate. Compare:
- Training convergence speed
- Final benchmark score after identical training
- Adapter size

Some models respond better to LoRA fine-tuning than others at the same parameter count.

### Step 4: Practical Testing

Install each candidate on the lowest-spec student laptop available and test:
- Time to first token
- Tokens per second
- Memory stability over long conversations
- Compatibility with Ollama on macOS, Windows, and Linux

## Model Comparison (2026 Evaluation)

| Model | Parameters | Q4_K_M Size | RAM Usage | License | LocoLLM Benchmark |
|---|---|---|---|---|---|
| Qwen2.5-3B-Instruct | 3.09B | 2.0GB | ~2.8GB | Apache 2.0 | Baseline |
| Llama 3.2-3B-Instruct | 3.21B | 2.0GB | ~2.9GB | Llama 3.2 Community | TBD |
| Phi-3.5-mini-instruct | 3.82B | 2.3GB | ~3.2GB | MIT | TBD |
| Gemma 2-2B-it | 2.61B | 1.6GB | ~2.3GB | Gemma License | TBD |

*Note: This table will be populated with actual benchmark scores during the model selection process each year.*

## Why Not 7B?

A 7B model in Q4_K_M quantization requires approximately 4.5GB of RAM for the model alone. With OS overhead (1-2GB), Ollama runtime (~0.5GB), and an active LoRA adapter (~0.1GB), total usage reaches 6-7GB. This is technically possible on an 8GB machine but leaves almost no headroom, leading to:

- Swapping to disk under memory pressure (catastrophic for inference speed)
- Inability to run a web browser or other applications alongside LocoLLM
- Unreliable performance on machines with shared GPU memory (integrated graphics)

The 3B class provides a much more comfortable margin. The lower baseline capability is exactly what the adapter architecture is designed to compensate for.

## Changing the Base Model

A base model change affects the entire ecosystem. All existing adapters must be verified or retrained. This is a significant community effort, so changes should be:

- **Infrequent:** Once per academic year at most
- **Well-justified:** The new model must be meaningfully better, not just marginally
- **Planned:** Announce at least one semester in advance so teams can prepare
- **Backwards-compatible:** Maintain the previous model as a fallback for one semester

### Migration Process

1. Announce candidate model and rationale
2. Run full evaluation (Steps 1-4 above)
3. Test representative adapters from the current ecosystem on the new base
4. If adapters transfer well: publish conversion guide
5. If adapters don't transfer: coordinate retraining effort
6. Update all documentation, templates, and training scripts
7. Old base model remains supported for one additional semester
