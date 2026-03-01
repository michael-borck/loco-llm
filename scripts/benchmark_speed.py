#!/usr/bin/env python3
"""Benchmark GGUF model speed using llama-bench.

Runs llama-bench across candidate GGUF models and produces a comparison table
with prompt processing speed, generation speed, and time-to-first-token.

Usage:
    python scripts/benchmark_speed.py --models-dir ./models
    python scripts/benchmark_speed.py --models-dir ./models --ngl 99 --repetitions 3
    python scripts/benchmark_speed.py --models-dir ./models --llama-bench /path/to/llama-bench
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def discover_models(models_dir: Path) -> list[Path]:
    """Find all *.gguf files in a directory."""
    models = sorted(models_dir.glob("*.gguf"))
    if not models:
        print(f"Error: no .gguf files found in {models_dir}", file=sys.stderr)
        sys.exit(1)
    return models


def run_llama_bench(
    gguf_path: Path,
    llama_bench: str,
    prompt_tokens: int,
    gen_tokens: int,
    ngl: int,
    repetitions: int,
    threads: int,
) -> dict:
    """Run llama-bench on a single GGUF model and return parsed JSON results."""
    cmd = [
        llama_bench,
        "-m", str(gguf_path),
        "-p", str(prompt_tokens),
        "-n", str(gen_tokens),
        "-ngl", str(ngl),
        "-r", str(repetitions),
        "-t", str(threads),
        "-o", "json",
    ]

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  STDERR:\n{result.stderr}", file=sys.stderr)
        raise RuntimeError(
            f"llama-bench failed for {gguf_path.name} (exit code {result.returncode})"
        )

    # llama-bench -o json outputs a JSON array of test results
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  Failed to parse JSON output:\n{result.stdout}", file=sys.stderr)
        raise

    return data


def extract_metrics(bench_data: list[dict], prompt_tokens: int) -> dict:
    """Extract pp/tg speeds and compute TTFT from llama-bench JSON output.

    llama-bench outputs one entry per test type (pp = prompt processing,
    tg = text generation). Each entry includes avg_ts (tokens/sec) and
    stddev_ts.
    """
    metrics = {}

    for entry in bench_data:
        test_type = entry.get("test")  # "pp" or "tg"
        avg_ts = entry.get("avg_ts")
        stddev_ts = entry.get("stddev_ts")

        if test_type == "pp":
            metrics["pp_avg_ts"] = avg_ts
            metrics["pp_stddev_ts"] = stddev_ts
            # TTFT = time to process the full prompt (ms)
            if avg_ts and avg_ts > 0:
                metrics["ttft_ms"] = prompt_tokens / avg_ts * 1000
            else:
                metrics["ttft_ms"] = None
        elif test_type == "tg":
            metrics["tg_avg_ts"] = avg_ts
            metrics["tg_stddev_ts"] = stddev_ts

    return metrics


def print_summary_table(summary: dict) -> None:
    """Print a formatted comparison table to stdout."""
    if not summary:
        print("No results to display.")
        return

    columns = [
        ("Model", "model"),
        ("Size (MB)", "size_mb"),
        ("pp (t/s)", "pp_avg_ts"),
        ("tg (t/s)", "tg_avg_ts"),
        ("TTFT (ms)", "ttft_ms"),
    ]

    # Compute column widths
    col_widths = []
    for header, key in columns:
        width = len(header)
        for entry in summary.values():
            val = entry.get(key)
            if val is None:
                cell = "-"
            elif key == "model":
                cell = str(val)
            elif key == "size_mb":
                cell = f"{val:.0f}"
            else:
                cell = f"{val:.2f}"
            width = max(width, len(cell))
        col_widths.append(width + 2)

    # Header
    header_line = ""
    for i, (header, _) in enumerate(columns):
        header_line += header.ljust(col_widths[i])
    total_width = len(header_line)

    print(f"\n{'=' * total_width}")
    print("SPEED BENCHMARK RESULTS")
    print(f"{'=' * total_width}")
    print(header_line)
    print("-" * total_width)

    # Rows
    for model_name in sorted(summary):
        entry = summary[model_name]
        row = ""
        for i, (_, key) in enumerate(columns):
            val = entry.get(key)
            if val is None:
                cell = "-"
            elif key == "model":
                cell = str(val)
            elif key == "size_mb":
                cell = f"{val:.0f}"
            else:
                cell = f"{val:.2f}"
            row += cell.ljust(col_widths[i])
        print(row)

    print(f"{'=' * total_width}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark GGUF model speed with llama-bench",
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        required=True,
        help="Directory containing .gguf model files",
    )
    parser.add_argument(
        "--llama-bench",
        default="llama-bench",
        help="Path to llama-bench binary (default: llama-bench, assumes PATH)",
    )
    parser.add_argument(
        "--prompt-tokens",
        type=int,
        default=512,
        help="Prompt length in tokens (default: 512)",
    )
    parser.add_argument(
        "--gen-tokens",
        type=int,
        default=128,
        help="Generation length in tokens (default: 128)",
    )
    parser.add_argument(
        "--ngl",
        type=int,
        default=0,
        help="Number of GPU layers; 0 = CPU-only, 99 = full GPU (default: 0)",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Repetitions per test (default: 5)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help=f"CPU threads (default: {os.cpu_count()})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/speed-benchmark/"),
        help="Where to save results (default: results/speed-benchmark/)",
    )
    args = parser.parse_args()

    models = discover_models(args.models_dir)
    print(f"Found {len(models)} GGUF model(s) in {args.models_dir}:\n")
    for m in models:
        print(f"  - {m.name}")
    print()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    total = len(models)
    summary = {}

    for i, gguf_path in enumerate(models, 1):
        print(f"[{i}/{total}] Benchmarking {gguf_path.name} ...")

        try:
            bench_data = run_llama_bench(
                gguf_path=gguf_path,
                llama_bench=args.llama_bench,
                prompt_tokens=args.prompt_tokens,
                gen_tokens=args.gen_tokens,
                ngl=args.ngl,
                repetitions=args.repetitions,
                threads=args.threads,
            )
        except RuntimeError as e:
            print(f"  Error: {e}", file=sys.stderr)
            print()
            continue

        # Save raw JSON
        model_name = gguf_path.stem
        raw_path = args.output_dir / f"{model_name}.json"
        with open(raw_path, "w") as f:
            json.dump(bench_data, f, indent=2)
        print(f"  Raw results saved to {raw_path}")

        # Extract metrics
        metrics = extract_metrics(bench_data, args.prompt_tokens)
        size_mb = gguf_path.stat().st_size / (1024 * 1024)

        summary[model_name] = {
            "model": model_name,
            "size_mb": size_mb,
            **metrics,
        }
        print()

    # Display summary
    print_summary_table(summary)

    # Save summary
    summary_path = args.output_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
