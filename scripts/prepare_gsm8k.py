#!/usr/bin/env python3
"""Download and format a subset of GSM8K for LoRA training.

Produces adapters/math/training_data.jsonl in Qwen3 chat format:
    {"conversations": [{"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}]}

Usage:
    source .venv-train/bin/activate
    python scripts/prepare_gsm8k.py [--num-examples 200]
"""

import argparse
import json
import re
from pathlib import Path

# GSM8K is available on Hugging Face as openai/gsm8k
HF_DATASET_URL = "https://datasets-server.huggingface.co/rows?dataset=openai/gsm8k&config=main&split=train&offset=0&length={length}"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "adapters" / "math" / "training_data.jsonl"


def download_gsm8k(num_examples: int) -> list[dict]:
    """Download GSM8K examples from Hugging Face datasets API."""
    import requests

    url = HF_DATASET_URL.format(length=num_examples)
    print(f"Downloading {num_examples} examples from GSM8K...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    rows = [r["row"] for r in data["rows"]]
    print(f"  Got {len(rows)} examples")
    return rows


def format_answer(answer_text: str) -> str:
    """Convert GSM8K answer format to clean step-by-step reasoning.

    GSM8K answers look like:
        Step 1 explanation\nStep 2 explanation\n#### 42

    We convert to:
        Step 1 explanation
        Step 2 explanation
        The answer is 42
    """
    # Split off the final answer (after ####)
    parts = answer_text.split("####")
    reasoning = parts[0].strip()
    final_answer = parts[1].strip() if len(parts) > 1 else ""

    # Clean up the reasoning: remove any "<<...>>" annotation markers GSM8K uses
    reasoning = re.sub(r"<<.*?>>", "", reasoning)
    reasoning = reasoning.strip()

    return f"{reasoning}\nThe answer is {final_answer}"


def format_for_training(examples: list[dict]) -> list[dict]:
    """Convert GSM8K examples to Qwen3 chat format."""
    formatted = []
    for ex in examples:
        question = ex["question"].strip()
        answer = format_answer(ex["answer"])
        formatted.append(
            {
                "conversations": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ]
            }
        )
    return formatted


def main():
    parser = argparse.ArgumentParser(description="Prepare GSM8K training data")
    parser.add_argument(
        "--num-examples",
        type=int,
        default=200,
        help="Number of GSM8K examples to download (default: 200)",
    )
    args = parser.parse_args()

    examples = download_gsm8k(args.num_examples)
    formatted = format_for_training(examples)

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
