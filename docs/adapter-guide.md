# Adapter Development Guide

A practical, step-by-step guide for student teams building their first LocoLLM adapter.

## Before You Start

Make sure you have:

- A LocoLLM installation (see README Quick Start)
- Access to a GPU for training (Google Colab free tier works)
- An approved adapter proposal (see CONTRIBUTING.md Step 1)
- Python 3.10+ with the LocoLLM dev dependencies installed (`uv sync`)

## Phase 1: Understand Your Domain (Week 1-2)

Before writing any code or collecting data, spend time understanding where the base model fails in your target domain.

### Baseline Testing

Run at least 20 queries in your target domain through the base model and record the results:

```bash
loco query "Your test query here" --no-adapter --save-log baseline_tests.jsonl
```

For each query, note:
- Did the model get it right?
- If wrong, how was it wrong? (factual error, wrong format, missing steps, irrelevant response)
- What would a good answer look like?

This baseline testing serves two purposes: it tells you whether your adapter domain is worth pursuing (if the base model already handles it well, pick a different domain), and the patterns you observe in failures will guide your training data strategy.

### Failure Analysis

Categorize the failures you found. Common patterns:

| Failure Type | Training Strategy |
|---|---|
| Wrong answer format | Include many examples with correct formatting |
| Missing reasoning steps | Use chain-of-thought examples with explicit steps |
| Domain vocabulary errors | Include examples that use domain-specific terms correctly |
| Incorrect application of rules | Create examples covering each rule/formula explicitly |
| Inconsistent quality | More diverse training examples, especially edge cases |

This analysis should go in your `TRAINING_LOG.md`.

## Phase 2: Curate Training Data (Week 2-4)

This is the most important phase. Adapter quality is mostly determined by training data quality. A well-curated dataset of 500 examples will outperform a sloppy dataset of 5000.

### Data Sources

**Option A: Existing public datasets.** Many NLP datasets are freely available on HuggingFace Datasets. Convert them to the LocoLLM JSONL format. Good starting points:
- Math: GSM8K, MATH, AQuA-RAT
- Code: CodeAlpaca, CodeContests
- Writing: Alpaca variants filtered by topic
- Domain QA: SQuAD, Natural Questions (filtered)

**Option B: Synthetic generation.** Use a frontier model to generate training examples. This is practical and effective, but requires careful quality control.

Template for synthetic data generation:

```
Generate a {domain} training example for a language model.

The example should have:
- An instruction telling the model what to do
- An input providing the specific problem or context  
- An output showing the ideal response

Requirements for the output:
- {quality criteria specific to your domain}
- {format requirements}
- {level of detail expected}

Generate one example now in this JSON format:
{"instruction": "...", "input": "...", "output": "..."}
```

Generate in batches, review each batch, and discard or fix low-quality examples. Document your rejection rate.

**Option C: Expert-written examples.** The highest quality but most labor-intensive. Best used for the benchmark set rather than the full training set.

### Data Quality Checklist

Before finalizing your dataset, verify:

- [ ] At least 500 training examples
- [ ] No duplicate or near-duplicate examples
- [ ] Outputs are consistently high quality (would you be happy receiving this response?)
- [ ] Difficulty is varied (not all easy, not all hard)
- [ ] Edge cases are represented
- [ ] Format is consistent (same JSONL schema throughout)
- [ ] Benchmark set (50+ examples) is completely separate from training set
- [ ] All sources are documented in TRAINING_LOG.md

### JSONL Format

```jsonl
{"instruction": "Solve the following arithmetic word problem. Show your reasoning step by step, then give the final answer.", "input": "A bakery makes 240 muffins per day. They sell 75% of them at full price ($3 each) and donate the rest. What is their daily revenue from muffins?", "output": "Step 1: Calculate muffins sold at full price.\n240 muffins x 75% = 240 x 0.75 = 180 muffins sold\n\nStep 2: Calculate revenue.\n180 muffins x $3 = $540\n\nThe bakery's daily muffin revenue is $540."}
```

## Phase 3: Fine-Tune (Week 4-5)

### Google Colab Setup

If you don't have local GPU access, use this Colab workflow:

1. Upload your dataset to Google Drive
2. Open the LocoLLM training notebook (link in project repo)
3. Connect to a T4 runtime (free tier)
4. Run the training cells with your dataset path and domain name

### Local Training

```bash
uv run python scripts/fine_tune.py \
  --base-model Qwen/Qwen2.5-3B-Instruct \
  --dataset adapters/your-domain/training/dataset.jsonl \
  --output adapters/your-domain/ \
  --lora-rank 16 \
  --epochs 3 \
  --lr 2e-4
```

Training a 3B model with LoRA on 500-1000 examples typically takes:
- T4 GPU (Colab free): 2-4 hours
- RTX 3060/4060: 1-2 hours
- RTX 3090/4090: 30-60 minutes
- M1/M2 Mac (MPS): 3-6 hours

### Monitoring Training

Watch for these patterns in the training loss:

**Healthy training:** Loss decreases steadily for the first epoch, then more slowly. Final loss is noticeably lower than starting loss.

**Overfitting:** Loss on training data keeps decreasing but performance on held-out examples starts degrading. Usually means you need more diverse training data or fewer epochs.

**Underfitting:** Loss barely decreases. Usually means the learning rate is too low, or your training data format doesn't match what the model expects.

**Unstable training:** Loss jumps around wildly. Reduce the learning rate.

### Common Pitfalls

**Data format mismatch.** Make sure your JSONL format matches the chat template expected by the base model. The training script handles this conversion, but check that `instruction`, `input`, and `output` fields are correctly populated.

**Too few epochs on small data.** With only 500 examples, the model might need 3-5 passes (epochs) to learn the patterns. With 5000+ examples, 1-2 epochs is often enough.

**LoRA rank too low.** If your domain requires the model to learn many new patterns, rank 8 might not have enough capacity. Try rank 32 if rank 16 doesn't show improvement. The adapter will be larger but still small.

## Phase 4: Evaluate (Week 5-6)

### Running the Evaluation

```bash
# Your adapter vs the benchmark
uv run python scripts/evaluate.py \
  --adapter adapters/your-domain/ \
  --benchmark adapters/your-domain/eval/benchmark.jsonl \
  --output adapters/your-domain/eval/results.json

# Base model vs the same benchmark
uv run python scripts/evaluate.py \
  --benchmark adapters/your-domain/eval/benchmark.jsonl \
  --output adapters/your-domain/eval/base_results.json
```

### Interpreting Results

**Strong result (ship it):** Adapter scores 15+ percentage points above base model, minimal out-of-domain degradation.

**Moderate result (iterate):** Adapter scores 5-15 points above base model. Consider whether the improvement is consistent across difficulty levels. If the adapter only helps on easy questions, the training data may lack challenging examples.

**Weak result (rethink):** Adapter scores less than 5 points above base model. Possible causes:
- Training data quality issues (most common)
- Domain too broad (narrow your scope)
- Base model already handles this domain reasonably well (pick a different domain)
- Not enough training data
- Hyperparameters need tuning

**Negative result (don't ship):** Adapter scores below the base model. Something went wrong in training. Check for data contamination (benchmark examples in training set), format issues, or corrupted training data.

### Iteration Cycle

If your first training run doesn't pass the evaluation bar:

1. Analyze which specific benchmark examples the adapter gets wrong
2. Look for patterns (e.g., all multi-step problems fail, or a specific type of formatting is wrong)
3. Add targeted training examples that address these failure patterns
4. Retrain and re-evaluate
5. Document each iteration in your TRAINING_LOG.md

Most successful adapters go through 2-3 training iterations.

## Phase 5: Package and Submit (Week 6)

### Directory Structure

Your final adapter directory should look like this:

```
adapters/your-domain/
├── adapter_config.json              # Generated by training script
├── adapter_model.safetensors        # Trained weights
├── training/
│   ├── dataset.jsonl                # Full training dataset
│   ├── train_config.yaml            # Exact config used for final run
│   ├── generate_data.py             # Data generation script (if synthetic)
│   └── TRAINING_LOG.md              # Complete development log
└── eval/
    ├── benchmark.jsonl              # 50+ held-out test cases
    ├── results.json                 # Adapter evaluation results
    ├── base_results.json            # Base model evaluation results
    └── ood_results.json             # Out-of-domain check results
```

### Registry Entry

Add your adapter to `adapters/registry.yaml`:

```yaml
your-domain:
  version: "1.0.0"
  base_model: "Qwen/Qwen2.5-3B-Instruct"
  quantization: "Q4_K_M"
  lora_rank: 16
  created: "2026-S2"
  authors: ["Your Team Name, ISYS6020"]
  benchmark_score: 0.72
  base_model_score: 0.41
  improvement: "+75.6%"
  description: "One-line description of what this adapter does"
  tags: ["relevant", "keywords"]
  size_mb: 24
  router_keywords: ["trigger", "words", "for", "keyword", "router"]
```

### Submit Your PR

Open a pull request against the main branch. Use the PR template, which includes the full checklist from CONTRIBUTING.md.

## Tips from Previous Cohorts

*This section will grow as cohorts complete their projects.*

- Start data curation early. It always takes longer than you expect.
- Test the base model extensively before training. Understanding its failures is more valuable than understanding its successes.
- Quality of training outputs matters enormously. Every output in your dataset is teaching the model what "good" looks like for your domain.
- Don't over-scope. "Math reasoning" is a semester project. "All of mathematics" is a career.
- Document as you go, not at the end. Your TRAINING_LOG.md is both a deliverable and a gift to next semester's team.
