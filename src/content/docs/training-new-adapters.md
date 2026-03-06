---
title: "Training New Adapters"
---

A generic workflow for creating LocoLLM adapters. The math, code, and analysis adapters all follow this pattern.

## Overview

Every adapter goes through five stages:

1. **Prepare data** — download a dataset and format it for Qwen3 chat template
2. **Train** — QLoRA fine-tune Qwen3-4B and export as merged GGUF
3. **Register** — add the adapter to `adapters/registry.yaml`
4. **Deploy** — load the merged GGUF into Ollama via `loco setup`
5. **Evaluate** — run `loco eval <adapter>` to compare against the base model

## Stage 1: Data Preparation

Each adapter needs a `training_data.jsonl` in Qwen3 chat format:

```jsonl
{"conversations": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Create a script at `scripts/prepare_<name>_data.py` following the existing patterns:

- **Math** (`scripts/prepare_gsm8k.py`): Downloads from GSM8K, formats step-by-step reasoning
- **Code** (`scripts/prepare_code_data.py`): Downloads Python instruction→code pairs, filters short outputs
- **Analysis** (`scripts/prepare_analysis_data.py`): Downloads science passages, builds passage+question→answer format

Data prep scripts use the Hugging Face datasets API and output to `adapters/<name>/training_data.jsonl`.

### Data quality tips

- Filter out very short or empty outputs
- 200-300 examples is enough for a PoC adapter
- The assistant response format matters: consistent formatting helps the model learn the pattern

## Stage 2: Training

Use the generic training script:

```bash
source .venv-train/bin/activate
python scripts/train_adapter.py --adapter-name <name>
```

This handles LoRA setup, fine-tuning, and GGUF export. Override defaults if needed:

```bash
python scripts/train_adapter.py --adapter-name code --epochs 5 --lr 1e-4
```

The adapter-specific `train_math_adapter.py` still works for math — the generic script is equivalent with `--adapter-name math`.

See [Training the Math Adapter](train-math-adapter.md) for detailed walkthrough of the training process.

### Default hyperparameters

| Parameter | Value |
|-----------|-------|
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Learning rate | 2e-4 |
| Epochs | 3 |
| Batch size | 2 (gradient accum 4, effective 8) |
| Max seq length | 1024 |
| Quantization | Q4_K_M |

## Stage 3: Registration

Add the adapter to `adapters/registry.yaml`:

```yaml
adapters:
  your_adapter:
    version: "0.1.0"
    type: "merged-gguf"
    gguf_path: "your_adapter/gguf/unsloth.Q4_K_M.gguf"
    description: "Short description"
    authors: ["Your Name"]
    tags: ["relevant", "tags"]
    eval_dataset: "eval_dataset.jsonl"
    eval_type: "numeric"  # or "code" or "analysis"
    router_keywords: ["keyword1", "keyword2"]
    training:
      base_model: "unsloth/Qwen3-4B-unsloth-bnb-4bit"
      method: "qlora"
      dataset: "Dataset name (N examples)"
      lora_r: 16
      lora_alpha: 32
      epochs: 3
      quantization: "q4_k_m"
```

Key fields:

- **`eval_type`**: Controls how `loco eval` scores responses — `"numeric"` (exact number match), `"code"` (syntax + keywords), or `"analysis"` (substring match)
- **`router_keywords`**: Words that trigger this adapter when using automatic routing

## Stage 4: Deployment

```bash
loco setup
```

This creates the Ollama model from the merged GGUF.

## Stage 5: Evaluation

Create `adapters/<name>/eval_dataset.jsonl` with 20 hand-crafted problems. Format depends on `eval_type`:

**Numeric** (math):
```json
{"question": "What is 2+2?", "answer": 4}
```

**Code**:
```json
{"question": "Write a function...", "answer_keywords": ["def ", "return"], "eval_type": "code"}
```

**Analysis**:
```json
{"question": "Read the passage... What is X?", "answer": "expected answer", "eval_type": "analysis"}
```

Run the benchmark:

```bash
loco eval <adapter_name>
```

## Worked Examples

| Adapter | Dataset | Data prep | Eval type |
|---------|---------|-----------|-----------|
| math | GSM8K (200 examples) | `scripts/prepare_gsm8k.py` | numeric |
| code | python_code_instructions_18k_alpaca (300 examples) | `scripts/prepare_code_data.py` | code |
| analysis | allenai/sciq (300 examples) | `scripts/prepare_analysis_data.py` | analysis |

## Student Improvement Targets

The current adapters are deliberately basic (PoC quality). Here are concrete ways to improve them:

- **Better data prep**: Clean up noisy examples, add more training data, improve prompt templates
- **Analysis adapter**: The templated reasoning is crude — replace with actual model-generated explanations
- **Code eval**: Add execution-based testing (run the code, check outputs) instead of syntax-only checks
- **Hyperparameter tuning**: Experiment with LoRA rank, learning rate, number of epochs
- **Router upgrade**: Replace keyword matching with an ML classifier (see ADR-0003)
- **New adapters**: Creative writing, translation, summarization — follow the same workflow
- **Prompting strategies**: Add RE2 prompting or chain-of-thought to the eval harness
