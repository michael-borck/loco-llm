# Contributing to LocoLLM

This guide covers everything you need to contribute a new adapter to the LocoLLM ecosystem. Whether you're a student working on a semester project or an external contributor, the process is the same.

## Overview

Contributing an adapter involves five steps:

1. Propose a domain and get it approved
2. Curate and prepare training data
3. Train a LoRA adapter using the standard training script
4. Evaluate it against the base model using the standard harness
5. Submit a pull request with all required artifacts

The whole process is designed to be completable by a student team in one semester.

## Step 1: Propose a Domain

Before starting work, open a GitHub issue with `[adapter-proposal]` in the title. Your proposal should cover:

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

Training data and evaluation data use **different** formats. Getting these right
before you generate hundreds of examples saves a lot of rework.

**Training data** (`training_data.jsonl`), one JSON object per line, each holding
a two-turn conversation:

```json
{"conversations": [{"role": "user", "content": "Write a formal email declining a meeting invitation."}, {"role": "assistant", "content": "Dear [Name], ..."}]}
```

**Evaluation data** (`eval_dataset.jsonl`) depends on the `eval_type` you declare
in `registry.yaml`. Three are supported:

| `eval_type` | Line format | Scored by |
|---|---|---|
| `numeric` | `{"question": "...", "answer": 42}` | Extracting a number from the response and comparing it |
| `code` | `{"question": "...", "answer_keywords": ["def", "sorted"]}` | Valid Python syntax plus the expected keywords appearing |
| `analysis` | `{"question": "...", "answer": "expected text"}` | Case-insensitive check that the expected text appears in the response |

**Choose your eval type before you choose your domain**, not after. The harness
can only score what these three types can express. A domain whose correct answers
cannot be reduced to a number, a set of keywords, or a required phrase will need
the harness extended, which is a larger piece of work. Raise it early if that is
where you are heading.

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

- **Training set** (`training_data.jsonl`): Your main JSONL file (minimum 500 examples)
- **Benchmark set** (`eval_dataset.jsonl`): Separate set of at least 50 examples, held out from training, used for evaluation. These should never appear in training data.

## Step 3: Train the Adapter

Use the standard training script to ensure consistency across all adapters. It
reads `adapters/<name>/training_data.jsonl`, trains the LoRA, merges it into the
base model, and exports a Q4_K_M GGUF ready for Ollama.

Training needs Unsloth, which is heavy and GPU-specific, so it lives in a
separate environment from the main project:

```bash
source .venv-train/bin/activate
pip install unsloth unsloth_zoo

python scripts/train_adapter.py \
  --adapter-name your-domain \
  --lora-r 16 \
  --epochs 3 \
  --lr 2e-4 \
  --max-seq-length 1024
```

On Google Colab, use the notebooks in `notebooks/` rather than running this
script directly.

### Training Hardware

Training a 4B model adapter with LoRA is feasible on:
- A single consumer GPU (8GB+ VRAM) in 1-4 hours
- Google Colab free tier (T4 GPU) in 2-6 hours
- University lab machines

The standard script uses QLoRA (4-bit base model + LoRA adapters) to minimize memory requirements.

### Hyperparameter Guidance

The defaults in `train_adapter.py` are good starting points. If you want to experiment:

| Parameter | Default | Notes |
|---|---|---|
| LoRA rank | 16 | Higher = more capacity but larger adapter. 8-32 is reasonable range. |
| Learning rate | 2e-4 | Standard for QLoRA. Reduce if loss is unstable. |
| Epochs | 3 | Watch for overfitting. 2-5 is typical. |
| Batch size | 2 | Increase if GPU memory allows. Effective batch is this times `--grad-accum` (default 4). |
| Max sequence length | 1024 | Increase for tasks with longer inputs/outputs. |

### Output Artifacts

The training script merges the LoRA weights into the base model and exports a
quantized GGUF, which is what Ollama loads. After training, your adapter
directory should contain:

```
adapters/your-domain/
├── gguf/
│   └── unsloth.Q4_K_M.gguf      # Merged model (gitignored, see below)
├── training_data.jsonl           # Training data, 500+ examples
├── eval_dataset.jsonl            # Held-out benchmark, 50+ examples
├── TRAINING_LOG.md               # Human-readable training record
└── results.json                  # Populated in Step 4
```

**GGUF files are not committed.** `.gitignore` excludes `*.gguf`, because the
merged models are gigabytes each. Your pull request contains the datasets, the
log, the results, and the registry entry. Arrange transfer of the GGUF itself
with a maintainer.

## Step 4: Evaluate

Add your adapter to `adapters/registry.yaml` first, including its `eval_dataset`
and `eval_type` fields, then run the standard harness:

```bash
uv run loco eval your-domain
```

This runs **both** the base model and your adapter over
`eval_dataset.jsonl` and reports the two scores side by side. You do not run the
baseline separately, and you should not write your own harness. A score with no
baseline to compare it against is not a result.

### Out-of-Domain Check

`loco eval` always uses the adapter's own evaluation dataset, so there is no
one-line command for this yet. To check that your adapter has not degraded on
other tasks, temporarily point your registry entry's `eval_dataset` at another
adapter's dataset (for example `../math/eval_dataset.jsonl`), re-run
`loco eval your-domain`, and record the numbers before reverting the change.

### Minimum Bar

Your adapter must:
- Score higher than the base model on your domain benchmark
- Not score significantly lower than the base model on the out-of-domain benchmark (small degradation is acceptable, large drops are not)

There is no fixed percentage improvement threshold. A 10% improvement on a hard task is valuable. A 50% improvement on a trivial task is less interesting. Use judgment and document your reasoning.

### Results Format

Record your results in `results.json`:

```json
{
  "adapter": "your-domain",
  "base_model": "Qwen/Qwen3-4B-Instruct",
  "quantization": "Q4_K_M",
  "benchmark": "your-domain/eval_dataset.jsonl",
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

- [ ] `training_data.jsonl` with 500+ examples
- [ ] `eval_dataset.jsonl` with 50+ held-out test cases
- [ ] **No overlap between the two.** Nothing in `eval_dataset.jsonl` may appear in `training_data.jsonl`. Check this, do not assume it.
- [ ] `TRAINING_LOG.md` fully documented
- [ ] `results.json` showing both the base model score and the adapter score
- [ ] Out-of-domain evaluation completed
- [ ] `registry.yaml` updated with new adapter entry, matching what you submitted
- [ ] Merged GGUF transfer arranged with a maintainer (the file itself is not committed)
- [ ] No copyrighted material in training data
- [ ] All data sources documented

## Improving Existing Adapters

Not every contribution needs to be a new adapter. Improving an existing one is equally valuable:

- **Better training data**: More examples, higher quality, more diverse
- **Hyperparameter tuning**: Finding a better training configuration
- **Benchmark expansion**: Adding more test cases or harder test cases
- **Version bumping**: If your improved adapter beats the current version on the same benchmark, submit it as a version upgrade

When improving an existing adapter, keep the previous version's benchmark results in the PR for comparison.

## Development Setup

```bash
# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (including dev tools)
uv sync

# Run checks
uv run ruff check .        # lint
uv run ruff format --check . # format check
uv run mypy src/           # type check
uv run pytest              # tests
```

## Code Contributions

Contributions to the core framework (router, CLI, evaluation harness) are also welcome. For these:

1. Open an issue describing the proposed change
2. Get a maintainer's input before starting significant work
3. Follow existing code style and patterns
4. Include tests where applicable
5. Update documentation if behavior changes

## Questions?

Open an issue with the `[question]` tag or reach out to the project maintainers.
