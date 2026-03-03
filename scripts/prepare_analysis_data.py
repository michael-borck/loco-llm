#!/usr/bin/env python3
"""Download and format science reading comprehension examples for LoRA training.

Produces adapters/analysis/training_data.jsonl in Qwen3 chat format:
    {"conversations": [{"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}]}

Uses allenai/sciq from Hugging Face.

Usage:
    source .venv-train/bin/activate
    python scripts/prepare_analysis_data.py [--num-examples 300]
"""

import argparse
import json
from pathlib import Path

HF_DATASET_URL = "https://datasets-server.huggingface.co/rows?dataset=allenai/sciq&config=default&split=train&offset=0&length={length}"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "adapters" / "analysis" / "training_data.jsonl"


def download_examples(num_examples: int) -> list[dict]:
    """Download examples from Hugging Face datasets API."""
    import requests

    url = HF_DATASET_URL.format(length=num_examples + 100)  # fetch extra to compensate for filtering
    print(f"Downloading examples from allenai/sciq...")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    rows = [r["row"] for r in data["rows"]]
    print(f"  Got {len(rows)} raw examples")
    return rows


def format_for_training(examples: list[dict], num_examples: int) -> list[dict]:
    """Convert to Qwen3 chat format, filtering examples with empty support."""
    formatted = []
    for ex in examples:
        if len(formatted) >= num_examples:
            break

        support = (ex.get("support") or "").strip()
        question = (ex.get("question") or "").strip()
        correct_answer = (ex.get("correct_answer") or "").strip()

        if not support or not question or not correct_answer:
            continue

        user_msg = (
            f"Read the following passage and answer the question.\n\n"
            f"Passage: {support}\n\n"
            f"Question: {question}"
        )

        # Templated reasoning — deliberately crude, obvious improvement target
        assistant_msg = (
            f"Based on the passage, the answer is: {correct_answer}\n\n"
            f"The passage states that {support[:200].rstrip('.')}. "
            f"This tells us that the answer to \"{question}\" is {correct_answer}."
        )

        formatted.append(
            {
                "conversations": [
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg},
                ]
            }
        )

    return formatted


def main():
    parser = argparse.ArgumentParser(description="Prepare analysis (reading comprehension) training data")
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
