#!/usr/bin/env python3
"""Train a LoRA math adapter using Unsloth and export as merged GGUF.

This script:
1. Loads Qwen3-4B in 4-bit quantization via Unsloth
2. Applies LoRA adapters to attention layers
3. Fine-tunes on GSM8K-style math problems
4. Merges LoRA weights into the base model
5. Exports as Q4_K_M GGUF ready for Ollama

Requirements:
    source .venv-train/bin/activate
    pip install unsloth unsloth_zoo

Usage:
    python scripts/train_math_adapter.py

Output:
    adapters/math/gguf/unsloth.Q4_K_M.gguf
"""

import json
from pathlib import Path

from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastModel

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAINING_DATA = PROJECT_ROOT / "adapters" / "math" / "training_data.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "adapters" / "math" / "gguf"
CHECKPOINT_DIR = PROJECT_ROOT / "adapters" / "math" / "checkpoints"

# --- Hyperparameters ---
MODEL_NAME = "unsloth/Qwen3-4B-unsloth-bnb-4bit"
MAX_SEQ_LENGTH = 1024
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4  # effective batch size = 8
QUANTIZATION_METHOD = "q4_k_m"


def load_training_data() -> Dataset:
    """Load training data from JSONL and convert to HuggingFace Dataset."""
    if not TRAINING_DATA.exists():
        raise FileNotFoundError(
            f"Training data not found at {TRAINING_DATA}\nRun: python scripts/prepare_gsm8k.py"
        )

    records = []
    with open(TRAINING_DATA) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} training examples")
    return Dataset.from_list(records)


def format_conversations(examples):
    """Format conversations into text using the tokenizer's chat template."""
    texts = []
    for convos in examples["conversations"]:
        # Apply chat template — Unsloth's tokenizer handles this
        text = tokenizer.apply_chat_template(
            convos,
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(text)
    return {"text": texts}


def main():
    global tokenizer  # needed by format_conversations callback

    print("=" * 60)
    print("  LocoLLM Math Adapter Training")
    print("=" * 60)

    # --- Step 1: Load model ---
    print(f"\n[1/5] Loading model: {MODEL_NAME}")
    model, tokenizer = FastModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
        full_finetuning=False,
    )

    # --- Step 2: Apply LoRA ---
    print(f"\n[2/5] Applying LoRA (r={LORA_R}, alpha={LORA_ALPHA})")
    model = FastModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    # Print trainable parameter count
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable parameters: {trainable:,} / {total:,} ({100 * trainable / total:.2f}%)")

    # --- Step 3: Load and format dataset ---
    print("\n[3/5] Loading training data")
    dataset = load_training_data()
    dataset = dataset.map(format_conversations, batched=True)

    # --- Step 4: Train ---
    print(
        f"\n[4/5] Training ({NUM_EPOCHS} epochs, "
        f"effective batch size {BATCH_SIZE * GRADIENT_ACCUMULATION})"
    )

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=TrainingArguments(
            output_dir=str(CHECKPOINT_DIR),
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION,
            num_train_epochs=NUM_EPOCHS,
            learning_rate=LEARNING_RATE,
            lr_scheduler_type="cosine",
            warmup_ratio=0.1,
            fp16=True,
            logging_steps=5,
            save_strategy="epoch",
            seed=42,
            optim="adamw_8bit",
            report_to="none",
        ),
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        packing=False,
    )

    trainer.train()

    # --- Step 5: Export merged GGUF ---
    print(f"\n[5/5] Exporting merged GGUF ({QUANTIZATION_METHOD})")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model.save_pretrained_gguf(
        str(OUTPUT_DIR),
        tokenizer,
        quantization_method=QUANTIZATION_METHOD,
    )

    expected_gguf = OUTPUT_DIR / f"unsloth.{QUANTIZATION_METHOD.upper()}.gguf"
    if expected_gguf.exists():
        size_mb = expected_gguf.stat().st_size / (1024 * 1024)
        print(f"\n  GGUF exported: {expected_gguf}")
        print(f"  Size: {size_mb:.0f} MB")
    else:
        # Unsloth may use a different naming convention
        ggufs = list(OUTPUT_DIR.glob("*.gguf"))
        if ggufs:
            for g in ggufs:
                size_mb = g.stat().st_size / (1024 * 1024)
                print(f"\n  GGUF exported: {g}")
                print(f"  Size: {size_mb:.0f} MB")
        else:
            print("\n  WARNING: No GGUF file found in output directory!")

    print("\n" + "=" * 60)
    print("  Training complete!")
    print("  Next steps:")
    print("    1. ollama create locollm-math -f adapters/math/Modelfile")
    print("    2. ollama run locollm-math 'What is 15 + 27?'")
    print("    3. loco eval math")
    print("=" * 60)


if __name__ == "__main__":
    main()
