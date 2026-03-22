#!/usr/bin/env python3
"""Train a LoRA adapter using Unsloth and export as merged GGUF.

Generic version of train_math_adapter.py — works for any adapter by name.

This script:
1. Loads Qwen3-4B in 4-bit quantization via Unsloth
2. Applies LoRA adapters to attention layers
3. Trains on the adapter's training_data.jsonl
4. Merges LoRA weights into the base model
5. Exports as Q4_K_M GGUF ready for Ollama

Requirements:
    source .venv-train/bin/activate
    pip install unsloth unsloth_zoo

Usage:
    python scripts/train_adapter.py --adapter-name code
    python scripts/train_adapter.py --adapter-name analysis --epochs 5 --lr 1e-4
"""

import argparse
import json
from pathlib import Path

from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_training_data(adapter_name: str) -> Dataset:
    """Load training data from JSONL and convert to HuggingFace Dataset."""
    data_path = PROJECT_ROOT / "adapters" / adapter_name / "training_data.jsonl"
    if not data_path.exists():
        raise FileNotFoundError(
            f"Training data not found at {data_path}\n"
            f"Run: python scripts/prepare_{adapter_name}_data.py"
        )

    records = []
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} training examples from {data_path}")
    return Dataset.from_list(records)


def format_conversations(examples, tokenizer):
    """Format conversations into text using the tokenizer's chat template."""
    texts = []
    for convos in examples["conversations"]:
        text = tokenizer.apply_chat_template(
            convos,
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(text)
    return {"text": texts}


def main():
    parser = argparse.ArgumentParser(description="Train a LoRA adapter")
    parser.add_argument(
        "--adapter-name",
        required=True,
        help="Name of the adapter (e.g., math, code, analysis)",
    )
    parser.add_argument("--model", default="unsloth/Qwen3-4B-unsloth-bnb-4bit", help="Base model")
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--quant-method", default="q4_k_m")
    args = parser.parse_args()

    adapter_name = args.adapter_name
    output_dir = PROJECT_ROOT / "adapters" / adapter_name / "gguf"
    checkpoint_dir = PROJECT_ROOT / "adapters" / adapter_name / "checkpoints"

    print("=" * 60)
    print(f"  LocoLLM Adapter Training: {adapter_name}")
    print("=" * 60)

    # --- Step 1: Load model ---
    print(f"\n[1/5] Loading model: {args.model}")
    model, tokenizer = FastModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        load_in_4bit=True,
        full_finetuning=False,
    )

    # --- Step 2: Apply LoRA ---
    print(f"\n[2/5] Applying LoRA (r={args.lora_r}, alpha={args.lora_alpha})")
    model = FastModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable parameters: {trainable:,} / {total:,} ({100 * trainable / total:.2f}%)")

    # --- Step 3: Load and format dataset ---
    print("\n[3/5] Loading training data")
    dataset = load_training_data(adapter_name)
    dataset = dataset.map(lambda ex: format_conversations(ex, tokenizer), batched=True)

    # --- Step 4: Train ---
    effective_batch = args.batch_size * args.grad_accum
    print(f"\n[4/5] Training ({args.epochs} epochs, effective batch size {effective_batch})")

    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=TrainingArguments(
            output_dir=str(checkpoint_dir),
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.grad_accum,
            num_train_epochs=args.epochs,
            learning_rate=args.lr,
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
        max_seq_length=args.max_seq_length,
        packing=False,
    )

    trainer.train()

    # --- Step 5: Export merged GGUF ---
    print(f"\n[5/5] Exporting merged GGUF ({args.quant_method})")
    output_dir.mkdir(parents=True, exist_ok=True)

    model.save_pretrained_gguf(
        str(output_dir),
        tokenizer,
        quantization_method=args.quant_method,
    )

    expected_gguf = output_dir / f"unsloth.{args.quant_method.upper()}.gguf"
    if expected_gguf.exists():
        size_mb = expected_gguf.stat().st_size / (1024 * 1024)
        print(f"\n  GGUF exported: {expected_gguf}")
        print(f"  Size: {size_mb:.0f} MB")
    else:
        ggufs = list(output_dir.glob("*.gguf"))
        if ggufs:
            for g in ggufs:
                size_mb = g.stat().st_size / (1024 * 1024)
                print(f"\n  GGUF exported: {g}")
                print(f"  Size: {size_mb:.0f} MB")
        else:
            print("\n  WARNING: No GGUF file found in output directory!")

    print("\n" + "=" * 60)
    print(f"  Training complete for '{adapter_name}'!")
    print("  Next steps:")
    print(f"    1. loco setup")
    print(f"    2. loco query --adapter {adapter_name} '<your prompt>'")
    print(f"    3. loco eval {adapter_name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
