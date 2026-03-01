#!/usr/bin/env python3
"""Benchmark GGUF base models using lm-evaluation-harness.

Runs lm_eval across candidate GGUF models and produces a comparison table.
Download GGUF files first, then point the script at their directory.

Usage:
    pip install lm-eval[hf]
    python scripts/benchmark_base_models.py --models-dir ./models
    python scripts/benchmark_base_models.py --models-dir ./models --tasks gsm8k,mmlu
    python scripts/benchmark_base_models.py --models-dir ./models --tokenizer Qwen/Qwen3-4B-Instruct
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# GGUF files don't bundle tokenizers — map filename patterns to HF tokenizers.
# Patterns are matched case-insensitively against the GGUF filename (stem).
TOKENIZER_LOOKUP = [
    (["qwen", "4b"], "Qwen/Qwen3-4B-Instruct"),
    (["qwen", "1.7b"], "Qwen/Qwen3-1.7B"),
    (["qwen", "coder", "3b"], "Qwen/Qwen2.5-Coder-3B"),
    (["llama", "3b"], "meta-llama/Llama-3.2-3B-Instruct"),
    (["llama", "1b"], "meta-llama/Llama-3.2-1B-Instruct"),
    (["phi", "4", "mini"], "microsoft/phi-4-mini-instruct"),
    (["gemma", "4b"], "google/gemma-3-4b-it"),
    (["gemma", "1b"], "google/gemma-3-1b-it"),
    (["deepseek", "r1", "1.5b"], "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"),
    (["smollm", "1.7b"], "HuggingFaceTB/SmolLM2-1.7B"),
    (["ministral", "3b"], "mistralai/Ministral-3-3B-Instruct-2512"),
]

DEFAULT_TASKS = "mmlu,gsm8k,hellaswag,truthfulqa_mc2,arc_challenge"


def resolve_tokenizer(gguf_path: Path) -> str | None:
    """Match a GGUF filename against the built-in lookup table."""
    name = gguf_path.stem.lower()
    for patterns, tokenizer in TOKENIZER_LOOKUP:
        if all(p in name for p in patterns):
            return tokenizer
    return None


def discover_models(models_dir: Path) -> list[Path]:
    """Find all *.gguf files in a directory."""
    models = sorted(models_dir.glob("*.gguf"))
    if not models:
        print(f"Error: no .gguf files found in {models_dir}", file=sys.stderr)
        sys.exit(1)
    return models


def run_benchmark(
    gguf_path: Path,
    tokenizer: str,
    tasks: str,
    output_dir: Path,
    batch_size: str,
    device: str,
) -> Path:
    """Run lm_eval on a single GGUF model via subprocess."""
    model_name = gguf_path.stem
    result_dir = output_dir / model_name
    result_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "lm_eval",
        "--model", "gguf",
        "--model_args", f"base_url={gguf_path},tokenizer={tokenizer}",
        "--tasks", tasks,
        "--batch_size", batch_size,
        "--device", device,
        "--output_path", str(result_dir),
        "--log_samples",
    ]

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  STDERR:\n{result.stderr}", file=sys.stderr)
        raise RuntimeError(f"lm_eval failed for {model_name} (exit code {result.returncode})")

    if result.stdout:
        print(result.stdout)

    return result_dir


def collect_results(output_dir: Path) -> dict:
    """Parse lm_eval result JSONs from each model subdirectory."""
    summary = {}
    for model_dir in sorted(output_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        # lm_eval writes results.json inside the output path
        results_file = model_dir / "results.json"
        if not results_file.exists():
            # lm_eval sometimes nests results one level deeper
            candidates = list(model_dir.rglob("results.json"))
            if not candidates:
                continue
            results_file = candidates[0]

        with open(results_file) as f:
            data = json.load(f)

        scores = {}
        results_data = data.get("results", {})
        for task_name, task_results in results_data.items():
            # lm_eval stores the primary metric as acc or acc_norm or exact_match
            for metric in ("acc,none", "acc_norm,none", "exact_match,none", "mc2,none"):
                if metric in task_results:
                    scores[task_name] = round(task_results[metric] * 100, 1)
                    break

        summary[model_dir.name] = scores
    return summary


def print_summary_table(summary: dict) -> None:
    """Print a formatted comparison table to stdout."""
    if not summary:
        print("No results to display.")
        return

    # Collect all task names across models
    all_tasks = sorted({task for scores in summary.values() for task in scores})

    # Column widths
    model_width = max(len(m) for m in summary) + 2
    col_width = max(max((len(t) for t in all_tasks), default=8), 8) + 2

    # Header
    header = "Model".ljust(model_width) + "".join(t.ljust(col_width) for t in all_tasks)
    print(f"\n{'=' * len(header)}")
    print("BENCHMARK RESULTS (scores in %)")
    print(f"{'=' * len(header)}")
    print(header)
    print("-" * len(header))

    # Rows
    for model_name in sorted(summary):
        scores = summary[model_name]
        row = model_name.ljust(model_width)
        for task in all_tasks:
            val = scores.get(task)
            cell = f"{val:.1f}" if val is not None else "-"
            row += cell.ljust(col_width)
        print(row)

    print(f"{'=' * len(header)}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark GGUF base models with lm-evaluation-harness",
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        required=True,
        help="Directory containing .gguf model files",
    )
    parser.add_argument(
        "--tasks",
        default=DEFAULT_TASKS,
        help=f"Comma-separated lm-eval tasks (default: {DEFAULT_TASKS})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/base-model-benchmark"),
        help="Where to save results (default: results/base-model-benchmark/)",
    )
    parser.add_argument(
        "--batch-size",
        default="auto",
        help="Batch size passed to lm-eval (default: auto)",
    )
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="Device for inference (default: cuda:0)",
    )
    parser.add_argument(
        "--tokenizer",
        default=None,
        help="Override tokenizer for all models (useful for single-model runs)",
    )
    args = parser.parse_args()

    models = discover_models(args.models_dir)
    print(f"Found {len(models)} GGUF model(s) in {args.models_dir}:\n")
    for m in models:
        print(f"  - {m.name}")
    print()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    total = len(models)

    for i, gguf_path in enumerate(models, 1):
        print(f"[{i}/{total}] Benchmarking {gguf_path.name} ...")

        tokenizer = args.tokenizer or resolve_tokenizer(gguf_path)
        if tokenizer is None:
            print(
                f"  Skipping — no tokenizer mapping for {gguf_path.name}. "
                "Use --tokenizer to specify one.",
                file=sys.stderr,
            )
            continue

        print(f"  Tokenizer: {tokenizer}")
        run_benchmark(
            gguf_path=gguf_path,
            tokenizer=tokenizer,
            tasks=args.tasks,
            output_dir=args.output_dir,
            batch_size=args.batch_size,
            device=args.device,
        )
        print()

    # Collect and display results
    summary = collect_results(args.output_dir)
    print_summary_table(summary)

    # Save aggregated summary
    summary_path = args.output_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
