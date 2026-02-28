# Evaluation Standards

This document defines how LocoLLM adapters are evaluated, what metrics are used, and what constitutes a passing result.

## Core Principle

Every adapter must answer one question with data: *"Does this adapter make the base model measurably better at the target task?"*

If the answer is no, or "maybe, it's hard to tell," the adapter isn't ready to ship.

## Benchmark Requirements

### Minimum Benchmark Size

Each adapter must include a benchmark of at least **50 test cases**. This isn't arbitrary. With 50 binary-scored examples, a 10-percentage-point difference between adapter and base model is statistically significant at p < 0.05 using a paired proportions test. Fewer examples and you can't distinguish real improvement from noise.

For tasks scored on continuous scales (ROUGE, LLM-judge rubrics), 50 examples still provides reasonable statistical power for moderate effect sizes.

### Benchmark Construction

**Held-out requirement:** Benchmark examples must never appear in training data. The evaluation harness checks for exact matches between benchmark and training files. Partial overlap (same problem with different numbers, same template with different names) should also be avoided.

**Difficulty distribution:** Benchmarks should include a mix of easy, medium, and hard examples. A useful rough split:
- 30% straightforward (base model should get ~50%+ of these right)
- 50% moderate (base model struggles, adapter should improve)
- 20% challenging (stretch goals, even adapted model may miss some)

**Edge cases:** Include at least 5 examples that test boundary conditions for your domain. For a math adapter: very large numbers, zero/negative values, ambiguous wording. For a code adapter: edge cases in logic, empty inputs, error handling.

**Format:**

```jsonl
{"id": "domain-001", "instruction": "Task description", "input": "Specific problem", "expected_output": "Correct answer", "evaluation_type": "exact_match", "difficulty": "easy"}
{"id": "domain-002", "instruction": "Task description", "input": "Specific problem", "expected_output": "Correct answer", "evaluation_type": "exact_match", "difficulty": "medium"}
```

## Evaluation Types

### exact_match

Best for: Math, classification, structured output, factual QA.

The harness extracts an answer from the model's response using a configurable pattern, normalizes it, and compares to the expected output.

```json
{
  "evaluation_type": "exact_match",
  "evaluation_config": {
    "extract_pattern": "\\d+\\.?\\d*",
    "normalize": true,
    "case_sensitive": false
  }
}
```

Normalization includes: lowercasing, stripping whitespace, converting number formats, handling common equivalences (e.g., "50%" = "0.5" if configured).

### code_execution

Best for: Code generation, data transformation.

The harness runs the generated code in a sandboxed environment and checks the output against expected results.

```json
{
  "evaluation_type": "code_execution",
  "evaluation_config": {
    "language": "python",
    "timeout_seconds": 10,
    "test_cases": [
      {"input": "5", "expected_output": "120"},
      {"input": "0", "expected_output": "1"}
    ]
  }
}
```

Scoring: Pass@1 (does the code run correctly on the first attempt?). Partial credit for code that runs but produces wrong output vs code that doesn't execute at all.

### llm_judge

Best for: Writing quality, style adherence, open-ended generation.

A separate LLM (the base model itself, or a frontier model if available) scores the response against a rubric.

```json
{
  "evaluation_type": "llm_judge",
  "evaluation_config": {
    "rubric": "Score 1-5 on: (1) relevance to prompt, (2) clarity of expression, (3) appropriate formality level, (4) structural organization, (5) grammar and mechanics. Provide a total score out of 25.",
    "extract_score_pattern": "Total:\\s*(\\d+)/25",
    "max_score": 25
  }
}
```

**Important:** LLM-as-judge evaluation is inherently noisy. For this reason:
- Run each example 3 times and average the scores
- Report the standard deviation alongside the mean
- An adapter needs to show improvement beyond the noise margin

### rouge

Best for: Summarization, paraphrasing, information extraction.

Standard ROUGE-L F1 score between generated and reference text.

```json
{
  "evaluation_type": "rouge",
  "evaluation_config": {
    "metric": "rougeL",
    "threshold": 0.3
  }
}
```

### custom

For domains that need specialized evaluation logic, the adapter can include a custom evaluation script:

```json
{
  "evaluation_type": "custom",
  "evaluation_config": {
    "script": "eval/custom_eval.py",
    "function": "evaluate"
  }
}
```

The function must accept `(generated: str, expected: str) -> float` and return a score between 0.0 and 1.0.

## Required Evaluations

Every adapter submission must include three evaluation runs:

### 1. Domain Benchmark (adapter vs base model)

The primary evaluation. Run the adapter and the base model on the same domain benchmark.

```bash
# Adapter
python scripts/evaluate.py --adapter adapters/your-domain/ --benchmark adapters/your-domain/eval/benchmark.jsonl

# Base model (no adapter)
python scripts/evaluate.py --benchmark adapters/your-domain/eval/benchmark.jsonl
```

**Pass criterion:** Adapter score must be higher than base model score.

### 2. Out-of-Domain Check

Run the adapter on at least one other domain's benchmark to verify it doesn't degrade general capability.

```bash
python scripts/evaluate.py --adapter adapters/your-domain/ --benchmark adapters/math-reasoning/eval/benchmark.jsonl
```

**Pass criterion:** Adapter score should be within 5 percentage points of the base model's score on the same benchmark. Small degradation is normal (the adapter shifts the model's attention toward its domain). Large degradation (more than 10 points) indicates a problem with training.

### 3. Qualitative Spot Check

Not automated, but required in the PR description. Show 5 example queries with the base model's response alongside the adapter's response. Pick examples that illustrate the improvement clearly. Include at least one failure case where the adapter still doesn't get it right.

## Results Reporting

### results.json Format

```json
{
  "adapter_name": "math-reasoning",
  "adapter_version": "1.2.0",
  "base_model": "Qwen/Qwen2.5-3B-Instruct",
  "quantization": "Q4_K_M",
  "benchmark_file": "adapters/math-reasoning/eval/benchmark.jsonl",
  "benchmark_hash": "sha256:a1b2c3...",
  "n_examples": 50,
  "evaluation_type": "exact_match",
  "results": {
    "adapter_score": 0.72,
    "base_model_score": 0.41,
    "improvement_absolute": 0.31,
    "improvement_relative": 0.756,
    "per_difficulty": {
      "easy": {"adapter": 0.93, "base": 0.73},
      "medium": {"adapter": 0.72, "base": 0.36},
      "hard": {"adapter": 0.40, "base": 0.10}
    }
  },
  "out_of_domain": {
    "benchmark": "adapters/code-python/eval/benchmark.jsonl",
    "adapter_score": 0.44,
    "base_model_score": 0.45,
    "degradation": -0.01
  },
  "timestamp": "2026-08-15T14:30:00Z",
  "hardware": "NVIDIA T4, Google Colab",
  "inference_config": {
    "temperature": 0.0,
    "max_tokens": 512,
    "top_p": 1.0
  }
}
```

### Inference Settings for Evaluation

All evaluations must use deterministic settings to ensure reproducibility:

- **temperature**: 0.0 (greedy decoding)
- **top_p**: 1.0
- **max_tokens**: 512 (unless the domain requires longer outputs)
- **repetition_penalty**: 1.0

These are enforced by the evaluation harness. Don't override them.

## Versioning and Re-evaluation

When an adapter is updated (new training data, different hyperparameters), it must be re-evaluated against the same benchmark. The results.json should include both the new and previous scores:

```json
{
  "previous_version": {
    "version": "1.1.0",
    "adapter_score": 0.65,
    "base_model_score": 0.41
  },
  "current_version": {
    "version": "1.2.0",
    "adapter_score": 0.72,
    "base_model_score": 0.41
  }
}
```

If the benchmark itself changes (new examples added, scoring adjusted), all previously evaluated adapters need to be re-run on the updated benchmark, and the benchmark hash in results.json will flag this automatically.

## Frontier API Comparison (Optional but Encouraged)

Where possible, also run the benchmark against a frontier API (GPT-4, Claude, Gemini) to establish an upper-bound reference point. This isn't a pass/fail criterion, but it answers the project's central research question: how close can a routed collection of 4-bit specialists get to frontier quality?

Document the API model version, date, and any relevant settings. These comparisons have a shelf life since API models change.
