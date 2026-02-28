# Training the Math LoRA Adapter

Step-by-step instructions for training the math adapter on neurocore (or any machine with an NVIDIA GPU and 8GB+ VRAM).

## Prerequisites

- NVIDIA GPU with 8GB+ VRAM (tested on RTX 2060 SUPER)
- CUDA 12.1+ with compatible PyTorch
- Python 3.10+
- Ollama installed and running
- The `qwen3:4b` model pulled in Ollama

## Overview

The training pipeline:

1. **Prepare data** — download GSM8K examples and format for Qwen3 chat template
2. **Train** — QLoRA fine-tune Qwen3-4B using Unsloth, then merge LoRA weights and export as GGUF
3. **Deploy** — load the merged GGUF into Ollama and verify with eval benchmark

The key design choice: we **merge LoRA weights into the base model** and export a standalone GGUF. Ollama does not support Qwen3 LoRA adapters via the `ADAPTER` directive (only Llama/Mistral/Gemma), so merging is required.

## Phase 1: Environment Setup

Training uses [Unsloth](https://github.com/unslothai/unsloth), which requires specific versions of transformers, peft, and torch that conflict with the locollm runtime. We use a **separate venv** (`.venv-train`) so training dependencies don't break the main project.

```bash
cd ~/projects/research/loco-llm
python3 -m venv .venv-train
source .venv-train/bin/activate
pip install --upgrade pip
pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo
```

> **Why not `uv`?** The main project doesn't use `uv` yet. When it does, this venv should remain separate — Unsloth's dependency matrix is incompatible with locollm's runtime deps.

Pull the base model in Ollama (if not already present):

```bash
ollama pull qwen3:4b
```

## Phase 2: Prepare Training Data

With the training venv active:

```bash
source .venv-train/bin/activate
python scripts/prepare_gsm8k.py --num-examples 200
```

This produces `adapters/math/training_data.jsonl` — 200 math problems in Qwen3 chat format:

```jsonl
{"conversations": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Each answer includes step-by-step reasoning ending with "The answer is N".

## Phase 3: Train and Export

```bash
source .venv-train/bin/activate
python scripts/train_math_adapter.py
```

This script:
1. Loads `Qwen3-4B` in 4-bit quantization via Unsloth
2. Applies LoRA (r=16, alpha=32) to attention layers (q/k/v/o_proj)
3. Fine-tunes for 3 epochs (effective batch size 8) with SFTTrainer
4. Merges LoRA weights into the base model
5. Exports as `Q4_K_M` GGUF to `adapters/math/gguf/`

Training takes ~15 minutes on an RTX 2060 SUPER with 200 examples.

### Training Hyperparameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| LoRA rank | 16 | Standard middle ground for math reasoning |
| LoRA alpha | 32 | 2x rank scaling factor |
| Learning rate | 2e-4 | Standard QLoRA default |
| Epochs | 3 | Small dataset needs multiple passes |
| Batch size | 2 (gradient accum 4) | Fits 8GB VRAM, effective batch 8 |
| Max seq length | 1024 | Sufficient for GSM8K problems |
| Quantization | Q4_K_M | Matches project standard (~2.5GB) |

## Phase 4: Deploy to Ollama

Create a Modelfile and load into Ollama:

```bash
echo 'FROM ./adapters/math/gguf/unsloth.Q4_K_M.gguf' > adapters/math/Modelfile
ollama create locollm-math -f adapters/math/Modelfile
```

Or use the CLI:

```bash
loco setup
```

## Phase 5: Verify

### Manual smoke test

```bash
ollama run locollm-math "What is 15 + 27?"
ollama run locollm-math "Solve for x: 2x + 5 = 13"
```

### Automated evaluation

```bash
loco eval math
```

This runs the 20-problem benchmark comparing base `qwen3:4b` vs the merged math adapter. Expect the fine-tuned adapter to score higher due to consistent answer formatting.

## Troubleshooting

**Out of memory during training**: Reduce `BATCH_SIZE` to 1 in `scripts/train_math_adapter.py`. Gradient accumulation will compensate.

**Unsloth install fails**: Check CUDA version compatibility. Unsloth requires CUDA 12.1+. Run `nvidia-smi` to verify driver version.

**GGUF file not found after training**: Check `adapters/math/gguf/` for any `.gguf` files — Unsloth may use a slightly different naming convention than expected.

**`loco setup` skips math adapter**: The GGUF must exist before setup can register it. Train first, then run setup.

## Output Files

| File | Purpose |
|------|---------|
| `adapters/math/training_data.jsonl` | Formatted GSM8K training data |
| `adapters/math/gguf/unsloth.Q4_K_M.gguf` | Merged GGUF ready for Ollama |
| `adapters/math/checkpoints/` | Training checkpoints (can be deleted after export) |
| `adapters/math/Modelfile` | Ollama Modelfile pointing to the GGUF |
