# Contributing to LocoLLM

This guide covers everything you need to contribute a new adapter to the LocoLLM ecosystem. Whether you're a student working on a semester project or an external contributor, the process is the same.

## Overview

Contributing an adapter involves five steps:

1. Propose a domain and get it approved
2. Curate and prepare training data
3. Fine-tune a LoRA adapter using the standard training script
4. Evaluate it against the base model using the standard harness
5. Submit a pull request with all required artifacts

The whole process is designed to be completable by a student team in one semester.

## Step 1: Propose a Domain

Before starting work, open a GitHub issue using the `[adapter-proposal]` template. Your proposal should cover:

- **Target domain**: What task or subject area will this adapter specialize in?
- **Why the base model underperforms**: Show 3-5 example queries where the base model gives poor results. This is your motivation.
- **Planned training data sources**: Where will your training examples come from? Public datasets, synthetic generation, expert-written examples, or a combination?
- **Scope boundaries**: What's in and out of scope for this adapter? "Math" is too broad. "Multi-step arithmetic word problems at secondary school level" is about right.
- **Estimated training set size**: How many examples do you plan to use?

A maintainer will review and either approve, suggest adjustments, or flag overlap with existing adapters.

### Choosing Good Domains

Adapters work best when the target domain has these properties:

**Good candidates:**
- The base model gives mediocre results but not terrible ones (there's something to build on)
- The task has a relatively consistent input/output structure
- Quality can be measured objectively or semi-objectively
- Enough training data exists or can be generated
- Students in the program would actually use this

**Poor candidates:**
- The base model already handles it well (basic summarization, simple Q&A)
- The task is too broad or subjective to benchmark meaningfully
- Training data would require deep domain expertise to create or validate
- The domain changes so rapidly that training data goes stale quickly

**Suggested starter domains** (for teams that want guidance):
- Structured output formatting (JSON, CSV, specific templates)
- Domain-specific reasoning (accounting calculations, legal clause analysis)
- Code generation in a specific language or framework
- Academic writing style (citations, formal structure, discipline-specific conventions)
- Data analysis narration (turning numbers into plain-language insights)

## Step 2: Prepare Training Data

### Format

All training data must be in JSONL format with three fields:

```json
{"instruction": "What to do", "input": "Context or problem", "output": "Expected response"}
```

For tasks without separate context, leave `input` as an empty string:

```json
{"instruction": "Write a formal email declining a meeting invitation", "input": "", "output": "Dear [Name], ..."}
```

### Requirements

- **Minimum 500 examples** for initial training. More is generally better, but quality matters more than quantity.
- **No copyrighted material** in training data. Use public domain sources, synthetic generation, or original content.
- **Diverse examples** within your domain. Don't train on 500 variations of the same problem.
- **Consistent quality** in the output field. Every output should be an example of what a good response looks like.
- **Document everything** in `TRAINING_LOG.md`: data sources, any filtering or cleaning steps, how synthetic data was generated.

### Synthetic Data Generation

Using a frontier model to generate training examples is fine and often practical. If you do this:

- Document which model and what prompts you used
- Include the generation script in your training directory
- Manually review at least 10% of generated examples for quality
- Note the review process and any rejection/edit rates in your training log

### Data Splits

- **Training set**: Your main JSONL file (minimum 500 examples)
- **Benchmark set** (`eval/benchmark.jsonl`): Separate set of at least 50 examples, held out from training, used for evaluation. These should never appear in training data.

## Step 3: Fine-Tune

Use the standard training script to ensure consistency across all adapters:

```bash
python scripts/fine_tune.py \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --dataset adapters/your-domain/training/dataset.jsonl \
  --output adapters/your-domain/ \
  --lora-rank 16 \
  --epochs 3 \
  --lr 2e-4 \
  --batch-size 4 \
  --max-seq-length 1024
```

### Training Hardware

Fine-tuning a 3B model with LoRA is feasible on:
- A single consumer GPU (8GB+ VRAM) in 1-4 hours
- Google Colab free tier (T4 GPU) in 2-6 hours
- University lab machines

The standard script uses QLoRA (4-bit base model + LoRA adapters) to minimize memory requirements.

### Hyperparameter Guidance

The defaults in `fine_tune.py` are good starting points. If you want to experiment:

| Parameter | Default | Notes |
|---|---|---|
| LoRA rank | 16 | Higher = more capacity but larger adapter. 8-32 is reasonable range. |
| Learning rate | 2e-4 | Standard for QLoRA. Reduce if loss is unstable. |
| Epochs | 3 | Watch for overfitting. 2-5 is typical. |
| Batch size | 4 | Increase if GPU memory allows. |
| Max sequence length | 1024 | Increase for tasks with longer inputs/outputs. |

### Output Artifacts

After training, your adapter directory should contain:

```
adapters/your-domain/
├── adapter_config.json          # LoRA configuration
├── adapter_model.safetensors    # Trained weights
├── training/
│   ├── dataset.jsonl            # Training data
│   ├── train_config.yaml        # Exact config used
│   └── TRAINING_LOG.md          # Human-readable training record
└── eval/
    ├── benchmark.jsonl           # 50+ held-out test cases
    └── results.json              # Populated in Step 4
```

## Step 4: Evaluate

Run the standard evaluation harness to benchmark your adapter:

```bash
# Evaluate your adapter
python scripts/evaluate.py \
  --adapter adapters/your-domain/ \
  --benchmark adapters/your-domain/eval/benchmark.jsonl \
  --output adapters/your-domain/eval/results.json

# Evaluate the base model on the same benchmark (for comparison)
python scripts/evaluate.py \
  --benchmark adapters/your-domain/eval/benchmark.jsonl \
  --output adapters/your-domain/eval/base_results.json

# Run out-of-domain check (pick another adapter's benchmark)
python scripts/evaluate.py \
  --adapter adapters/your-domain/ \
  --benchmark adapters/math-reasoning/eval/benchmark.jsonl \
  --output adapters/your-domain/eval/ood_results.json
```

### Minimum Bar

Your adapter must:
- Score higher than the base model on your domain benchmark
- Not score significantly lower than the base model on the out-of-domain benchmark (small degradation is acceptable, large drops are not)

There is no fixed percentage improvement threshold. A 10% improvement on a hard task is valuable. A 50% improvement on a trivial task is less interesting. Use judgment and document your reasoning.

### Results Format

The evaluation script produces a `results.json`:

```json
{
  "adapter": "your-domain",
  "base_model": "Qwen/Qwen2.5-3B-Instruct",
  "quantization": "Q4_K_M",
  "benchmark": "your-domain/eval/benchmark.jsonl",
  "n_examples": 50,
  "metric": "exact_match",
  "adapter_score": 0.72,
  "base_model_score": 0.41,
  "improvement": 0.756,
  "timestamp": "2026-08-15T14:30:00Z"
}
```

## Step 5: Submit

Open a pull request that includes:

1. Your complete adapter directory (all files listed above)
2. An updated entry in `adapters/registry.yaml`
3. A PR description that includes:
   - What the adapter does and why it's useful
   - Benchmark results (adapter score vs base model score)
   - Any known limitations or edge cases
   - Team members and their contributions

### PR Checklist

- [ ] `adapter_config.json` and `adapter_model.safetensors` present
- [ ] `training/dataset.jsonl` with 500+ examples
- [ ] `training/TRAINING_LOG.md` fully documented
- [ ] `eval/benchmark.jsonl` with 50+ held-out test cases
- [ ] `eval/results.json` showing improvement over base model
- [ ] Out-of-domain evaluation completed
- [ ] `registry.yaml` updated with new adapter entry
- [ ] No copyrighted material in training data
- [ ] All data sources documented

## Improving Existing Adapters

Not every contribution needs to be a new adapter. Improving an existing one is equally valuable:

- **Better training data**: More examples, higher quality, more diverse
- **Hyperparameter tuning**: Finding a better training configuration
- **Benchmark expansion**: Adding more test cases or harder test cases
- **Version bumping**: If your improved adapter beats the current version on the same benchmark, submit it as a version upgrade

When improving an existing adapter, keep the previous version's benchmark results in the PR for comparison.

## Code Contributions

Contributions to the core framework (router, CLI, evaluation harness) are also welcome. For these:

1. Open an issue describing the proposed change
2. Get a maintainer's input before starting significant work
3. Follow existing code style and patterns
4. Include tests where applicable
5. Update documentation if behavior changes

## Questions?

Open an issue with the `[question]` tag or reach out to the project maintainers.
