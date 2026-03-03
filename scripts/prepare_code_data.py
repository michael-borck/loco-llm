#!/usr/bin/env python3
"""Download and format Python coding examples for LoRA training.

Produces adapters/code/training_data.jsonl in Qwen3 chat format:
    {"conversations": [{"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}]}

Uses iamtarun/python_code_instructions_18k_alpaca from Hugging Face.

Usage:
    source .venv-train/bin/activate
    python scripts/prepare_code_data.py [--num-examples 300]
"""

import argparse
import json
from pathlib import Path

HF_DATASET_URL = "https://datasets-server.huggingface.co/rows?dataset=iamtarun/python_code_instructions_18k_alpaca&config=default&split=train&offset=0&length={length}"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "adapters" / "code" / "training_data.jsonl"

MIN_OUTPUT_LENGTH = 20


def download_examples(num_examples: int) -> list[dict]:
    """Download examples from Hugging Face datasets API."""
    import requests

    url = HF_DATASET_URL.format(length=num_examples + 100)  # fetch extra to compensate for filtering
    print(f"Downloading examples from python_code_instructions_18k_alpaca...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    rows = [r["row"] for r in data["rows"]]
    print(f"  Got {len(rows)} raw examples")
    return rows


def format_for_training(examples: list[dict], num_examples: int) -> list[dict]:
    """Convert to Qwen3 chat format, filtering short outputs."""
    formatted = []
    for ex in examples:
        if len(formatted) >= num_examples:
            break

        output = (ex.get("output") or "").strip()
        if len(output) < MIN_OUTPUT_LENGTH:
            continue

        # Concatenate instruction + input for the user message
        instruction = (ex.get("instruction") or "").strip()
        extra_input = (ex.get("input") or "").strip()
        if extra_input:
            user_msg = f"{instruction}\n\n{extra_input}"
        else:
            user_msg = instruction

        if not user_msg:
            continue

        formatted.append(
            {
                "conversations": [
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": output},
                ]
            }
        )

    return formatted


def main():
    parser = argparse.ArgumentParser(description="Prepare Python code training data")
    parser.add_argument(
        "--num-examples",
        type=int,
        default=300,
        help="Number of examples to include (default: 300)",
    )
    args = parser.parse_args()

    examples = download_examples(args.num_examples)
    formatted = format_for_training(examples, args.num_examples)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        for item in formatted:
            f.write(json.dumps(item) + "\n")

    print(f"\nWrote {len(formatted)} examples to {OUTPUT_PATH}")
    print("Sample (first example):")
    print(f"  Q: {formatted[0]['conversations'][0]['content'][:80]}...")
    print(f"  A: {formatted[0]['conversations'][1]['content'][:80]}...")


if __name__ == "__main__":
    main()
