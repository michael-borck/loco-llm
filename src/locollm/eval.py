"""Evaluation harness: runs a mini benchmark comparing base model vs adapter."""

import json
import re

from locollm import ollama_client


def load_dataset(path):
    """Load a JSONL evaluation dataset. Each line: {"question": "...", "answer": N}."""
    problems = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                problems.append(json.loads(line))
    return problems


def extract_number(text):
    """Extract the final numeric answer from model output.

    Looks for patterns like "the answer is 42", "= 42", or a standalone number
    at the end of the text. Returns None if no number is found.
    """
    # Try "the answer is <number>" pattern
    m = re.search(r"(?:the answer is|answer:?)\s*[\\$]*\s*(-?[\d,]+\.?\d*)", text, re.IGNORECASE)
    if m:
        return _parse_number(m.group(1))

    # Try boxed answer (LaTeX): \boxed{42}
    m = re.search(r"\\boxed\{(-?[\d,]+\.?\d*)\}", text)
    if m:
        return _parse_number(m.group(1))

    # Try "= <number>" at end of a line
    m = re.search(r"=\s*\$?\s*(-?[\d,]+\.?\d*)\s*\$?\s*$", text, re.MULTILINE)
    if m:
        return _parse_number(m.group(1))

    # Fall back to last number in the text
    matches = re.findall(r"-?[\d,]+\.?\d*", text)
    if matches:
        return _parse_number(matches[-1])

    return None


def _parse_number(s):
    """Parse a number string, removing commas."""
    s = s.replace(",", "")
    try:
        val = float(s)
        return int(val) if val == int(val) else val
    except (ValueError, OverflowError):
        return None


def run_eval(model_name, dataset):
    """Run evaluation on a model. Returns (correct, total, results_list)."""
    correct = 0
    total = len(dataset)
    results = []

    for i, problem in enumerate(dataset, 1):
        question = problem["question"]
        expected = problem["answer"]

        print(f"  [{i}/{total}] ", end="", flush=True)

        # Collect full response (non-streaming for eval)
        response = ollama_client.generate(model_name, question, stream=False)
        predicted = extract_number(response)

        is_correct = predicted is not None and float(predicted) == float(expected)
        if is_correct:
            correct += 1

        status = "OK" if is_correct else "MISS"
        print(f"{status}  (expected={expected}, got={predicted})")

        results.append(
            {
                "question": question,
                "expected": expected,
                "predicted": predicted,
                "correct": is_correct,
                "response": response,
            }
        )

    return correct, total, results


def format_results(base_correct, base_total, adapter_correct, adapter_total, adapter_name):
    """Print a comparison table of base vs adapter results."""
    base_pct = base_correct / base_total * 100 if base_total else 0
    adapter_pct = adapter_correct / adapter_total * 100 if adapter_total else 0
    diff = adapter_pct - base_pct

    print()
    print("=" * 50)
    print(f"  Evaluation Results: {adapter_name}")
    print("=" * 50)
    print(f"  {'Model':<25} {'Score':>10}")
    print(f"  {'-' * 25} {'-' * 10}")
    print(f"  {'Base (qwen3:4b)':<25} {base_correct:>3}/{base_total} ({base_pct:.0f}%)")
    adapter_label = f"Adapter ({adapter_name})"
    print(f"  {adapter_label:<25} {adapter_correct:>3}/{adapter_total} ({adapter_pct:.0f}%)")
    print(f"  {'-' * 25} {'-' * 10}")
    sign = "+" if diff >= 0 else ""
    print(f"  {'Difference':<25} {sign}{diff:.1f}%")
    print("=" * 50)
