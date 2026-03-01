#!/usr/bin/env python3
"""Generate benchmark_data.js for interactive charts on locollm.org.

Reads raw benchmark results (speed + quality JSON) and produces a single
JavaScript file that assigns structured data to window.BENCHMARK_DATA.

The --sample flag generates realistic dummy data so charts can be developed
and previewed before real benchmarks complete.

Usage:
    python scripts/generate_chart_data.py --sample
    python scripts/generate_chart_data.py \
        --speed-json results/speed-benchmark/summary.json \
        --quality-json results/base-model-benchmark/summary.json
"""

import argparse
import json
import math
import random
import sys
from pathlib import Path

# ── Model definitions ────────────────────────────────────────────────────

MODELS = [
    {"id": "qwen3-4b", "name": "Qwen3-4B", "family": "Qwen", "params_b": 4.0},
    {"id": "qwen3-1.7b", "name": "Qwen3-1.7B", "family": "Qwen", "params_b": 1.7},
    {"id": "llama-3.2-3b", "name": "Llama-3.2-3B", "family": "Llama", "params_b": 3.2},
    {"id": "llama-3.2-1b", "name": "Llama-3.2-1B", "family": "Llama", "params_b": 1.0},
    {"id": "phi-4-mini", "name": "Phi-4-Mini", "family": "Phi", "params_b": 3.8},
    {"id": "gemma-3-1b", "name": "Gemma-3-1B", "family": "Gemma", "params_b": 1.0},
    {"id": "gemma-3-4b", "name": "Gemma-3-4B", "family": "Gemma", "params_b": 4.0},
    {"id": "deepseek-r1-1.5b", "name": "DeepSeek-R1-1.5B", "family": "DeepSeek", "params_b": 1.5},
    {"id": "smollm2-1.7b", "name": "SmolLM2-1.7B", "family": "SmolLM", "params_b": 1.7},
    {"id": "ministral-3b", "name": "Ministral-3B", "family": "Mistral", "params_b": 3.0},
    {"id": "qwen2.5-coder-3b", "name": "Qwen2.5-Coder-3B", "family": "Qwen", "params_b": 3.0},
    {"id": "phi-4-mini-reasoning", "name": "Phi-4-Mini-Reasoning", "family": "Phi", "params_b": 3.8},
    {"id": "deepseek-r1-7b", "name": "DeepSeek-R1-7B", "family": "DeepSeek", "params_b": 7.0},
    {"id": "tinyllama-1.1b", "name": "TinyLlama-1.1B", "family": "TinyLlama", "params_b": 1.1},
]

QUANT_LEVELS = [
    {"id": "BF16", "bpw": 16.0},
    {"id": "Q8_0", "bpw": 8.0},
    {"id": "Q6_K", "bpw": 6.6},
    {"id": "Q5_K_M", "bpw": 5.7},
    {"id": "Q4_K_M", "bpw": 4.8},
    {"id": "Q4_0", "bpw": 4.0},
    {"id": "Q3_K_M", "bpw": 3.4},
    {"id": "Q2_K", "bpw": 2.6},
]

TASKS = ["mmlu", "hellaswag", "gsm8k", "truthfulqa", "arc_challenge"]

# Approximate BF16 scores by model (realistic ranges)
BF16_SCORES = {
    "qwen3-4b":             {"mmlu": 65.2, "hellaswag": 76.1, "gsm8k": 58.3, "truthfulqa": 52.4, "arc_challenge": 55.8},
    "qwen3-1.7b":           {"mmlu": 48.5, "hellaswag": 62.3, "gsm8k": 30.1, "truthfulqa": 44.2, "arc_challenge": 42.7},
    "llama-3.2-3b":         {"mmlu": 58.7, "hellaswag": 73.5, "gsm8k": 44.6, "truthfulqa": 49.1, "arc_challenge": 51.3},
    "llama-3.2-1b":         {"mmlu": 38.2, "hellaswag": 55.8, "gsm8k": 18.3, "truthfulqa": 40.5, "arc_challenge": 35.1},
    "phi-4-mini":           {"mmlu": 63.8, "hellaswag": 74.9, "gsm8k": 62.1, "truthfulqa": 50.7, "arc_challenge": 56.2},
    "gemma-3-1b":           {"mmlu": 39.5, "hellaswag": 57.2, "gsm8k": 21.4, "truthfulqa": 42.1, "arc_challenge": 36.8},
    "gemma-3-4b":           {"mmlu": 62.1, "hellaswag": 75.3, "gsm8k": 52.7, "truthfulqa": 51.3, "arc_challenge": 54.1},
    "deepseek-r1-1.5b":     {"mmlu": 44.3, "hellaswag": 58.1, "gsm8k": 38.5, "truthfulqa": 41.8, "arc_challenge": 39.2},
    "smollm2-1.7b":         {"mmlu": 46.8, "hellaswag": 61.5, "gsm8k": 28.7, "truthfulqa": 43.5, "arc_challenge": 41.3},
    "ministral-3b":         {"mmlu": 56.4, "hellaswag": 71.8, "gsm8k": 41.2, "truthfulqa": 48.3, "arc_challenge": 49.7},
    "qwen2.5-coder-3b":     {"mmlu": 52.1, "hellaswag": 68.4, "gsm8k": 35.8, "truthfulqa": 45.6, "arc_challenge": 46.2},
    "phi-4-mini-reasoning": {"mmlu": 64.5, "hellaswag": 74.2, "gsm8k": 67.8, "truthfulqa": 51.2, "arc_challenge": 57.1},
    "deepseek-r1-7b":       {"mmlu": 68.3, "hellaswag": 78.5, "gsm8k": 72.1, "truthfulqa": 54.6, "arc_challenge": 59.8},
    "tinyllama-1.1b":       {"mmlu": 32.1, "hellaswag": 50.3, "gsm8k": 8.5, "truthfulqa": 38.7, "arc_challenge": 30.2},
}


# ── Sample data generation ───────────────────────────────────────────────

def _quant_degradation(bpw: float, task: str) -> float:
    """Return a multiplier (0-1) modelling quality loss from quantization.

    Lower bpw = more degradation.  Knowledge tasks (MMLU) degrade faster
    than commonsense tasks (HellaSwag).
    """
    # Sensitivity per task — higher means more degradation at low bpw
    sensitivity = {
        "mmlu": 1.0,
        "hellaswag": 0.6,
        "gsm8k": 1.2,
        "truthfulqa": 0.7,
        "arc_challenge": 0.8,
    }
    s = sensitivity.get(task, 0.8)
    # Sigmoid-ish curve: near 1.0 at high bpw, drops steeply below ~4 bpw
    ratio = 1.0 - s * 0.02 * max(0, 16 - bpw) ** 1.5 / 50
    return max(0.3, min(1.0, ratio))


def _file_size_gb(params_b: float, bpw: float) -> float:
    """Estimate GGUF file size in GB."""
    bits_total = params_b * 1e9 * bpw
    bytes_total = bits_total / 8
    # ~5% overhead for GGUF metadata
    return bytes_total * 1.05 / (1024 ** 3)


def generate_sample_data() -> dict:
    """Generate realistic sample benchmark data for all 14x8 variants."""
    random.seed(42)
    variants = []

    for model in MODELS:
        bf16_scores = BF16_SCORES[model["id"]]

        for quant in QUANT_LEVELS:
            # Quality scores with quantization degradation + noise
            scores = {}
            for task in TASKS:
                base = bf16_scores[task]
                degraded = base * _quant_degradation(quant["bpw"], task)
                noisy = degraded + random.gauss(0, 0.5)
                scores[task] = round(max(0, min(100, noisy)), 1)

            composite = round(sum(scores.values()) / len(scores), 1)

            # File size
            file_size_gb = round(_file_size_gb(model["params_b"], quant["bpw"]), 3)

            # Speed metrics (CPU-only): smaller + more quantized = faster
            base_tg = 18 / model["params_b"]  # rough t/s scaling
            quant_speedup = 16 / quant["bpw"]
            tg_ts = round(base_tg * quant_speedup * random.uniform(0.9, 1.1), 1)

            base_pp = 120 / model["params_b"]
            pp_ts = round(base_pp * quant_speedup * random.uniform(0.9, 1.1), 1)

            ttft_ms = round(512 / pp_ts * 1000, 1) if pp_ts > 0 else None

            variants.append({
                "model_id": model["id"],
                "model_name": model["name"],
                "family": model["family"],
                "params_b": model["params_b"],
                "quant": quant["id"],
                "bpw": quant["bpw"],
                "file_size_gb": file_size_gb,
                "scores": scores,
                "composite_score": composite,
                "tg_ts": tg_ts,
                "pp_ts": pp_ts,
                "ttft_ms": ttft_ms,
            })

    return {
        "generated": "sample",
        "models": [m["id"] for m in MODELS],
        "model_meta": {m["id"]: m for m in MODELS},
        "quant_levels": [q["id"] for q in QUANT_LEVELS],
        "quant_meta": {q["id"]: q for q in QUANT_LEVELS},
        "tasks": TASKS,
        "variants": variants,
        "pareto_frontier": _compute_pareto(variants),
    }


# ── Real data loading ────────────────────────────────────────────────────

def _parse_model_quant(name: str) -> tuple[str, str] | None:
    """Extract (base_model_id, quant_level) from a benchmark result key.

    Handles patterns like:
      qwen3-4b-instruct-q4_k_m  ->  (qwen3-4b, Q4_K_M)
      Llama-3.2-3B-Instruct-BF16  ->  (llama-3.2-3b, BF16)
    """
    name_lower = name.lower().replace(" ", "-")
    quant_found = None
    for q in QUANT_LEVELS:
        q_lower = q["id"].lower().replace("_", "[-_]?")
        # Check if the name ends with or contains the quant tag
        if q["id"].lower() in name_lower or q["id"].lower().replace("_", "-") in name_lower:
            quant_found = q["id"]
            break

    if not quant_found:
        return None

    # Try to match to a known model
    for model in MODELS:
        # Check if model id components appear in the name
        model_parts = model["id"].lower().split("-")
        if all(part in name_lower for part in model_parts):
            return (model["id"], quant_found)

    return None


def load_real_data(speed_path: Path, quality_path: Path) -> dict:
    """Load real benchmark results from JSON files."""
    speed_data = {}
    quality_data = {}

    if speed_path.exists():
        with open(speed_path) as f:
            speed_data = json.load(f)

    if quality_path.exists():
        with open(quality_path) as f:
            quality_data = json.load(f)

    variants = []
    seen = set()

    # Merge speed and quality data
    all_keys = set(list(speed_data.keys()) + list(quality_data.keys()))

    for key in all_keys:
        parsed = _parse_model_quant(key)
        if not parsed:
            print(f"  Warning: could not parse model/quant from '{key}', skipping", file=sys.stderr)
            continue

        model_id, quant_id = parsed
        variant_key = f"{model_id}:{quant_id}"
        if variant_key in seen:
            continue
        seen.add(variant_key)

        model_meta = next((m for m in MODELS if m["id"] == model_id), None)
        quant_meta = next((q for q in QUANT_LEVELS if q["id"] == quant_id), None)
        if not model_meta or not quant_meta:
            continue

        # Quality scores
        scores = quality_data.get(key, {})
        task_scores = {t: scores.get(t) for t in TASKS}
        valid_scores = [v for v in task_scores.values() if v is not None]
        composite = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else None

        # Speed metrics
        speed = speed_data.get(key, {})
        file_size_gb = round(speed.get("size_mb", 0) / 1024, 3) if speed.get("size_mb") else None

        if file_size_gb is None:
            file_size_gb = round(_file_size_gb(model_meta["params_b"], quant_meta["bpw"]), 3)

        variants.append({
            "model_id": model_id,
            "model_name": model_meta["name"],
            "family": model_meta["family"],
            "params_b": model_meta["params_b"],
            "quant": quant_id,
            "bpw": quant_meta["bpw"],
            "file_size_gb": file_size_gb,
            "scores": task_scores,
            "composite_score": composite,
            "tg_ts": speed.get("tg_avg_ts"),
            "pp_ts": speed.get("pp_avg_ts"),
            "ttft_ms": speed.get("ttft_ms"),
        })

    return {
        "generated": "real",
        "models": [m["id"] for m in MODELS],
        "model_meta": {m["id"]: m for m in MODELS},
        "quant_levels": [q["id"] for q in QUANT_LEVELS],
        "quant_meta": {q["id"]: q for q in QUANT_LEVELS},
        "tasks": TASKS,
        "variants": variants,
        "pareto_frontier": _compute_pareto(variants),
    }


# ── Pareto frontier ──────────────────────────────────────────────────────

def _compute_pareto(variants: list[dict]) -> list[str]:
    """Return variant labels on the Pareto frontier (max composite, min size)."""
    # Filter variants with valid data
    valid = [
        v for v in variants
        if v["composite_score"] is not None and v["file_size_gb"] is not None
    ]
    # Sort by file size ascending
    valid.sort(key=lambda v: v["file_size_gb"])

    frontier = []
    best_score = -1
    for v in valid:
        if v["composite_score"] > best_score:
            best_score = v["composite_score"]
            frontier.append(f"{v['model_name']} {v['quant']}")

    # The frontier should go from smallest+worst to largest+best
    # But Pareto = for each size, the best score achievable
    # Re-compute properly: walk from largest to smallest, track max score
    valid.sort(key=lambda v: v["file_size_gb"], reverse=True)
    frontier = []
    best_score = -1
    for v in valid:
        if v["composite_score"] >= best_score:
            best_score = v["composite_score"]
            frontier.append(f"{v['model_name']} {v['quant']}")

    frontier.reverse()
    return frontier


# ── Output ───────────────────────────────────────────────────────────────

def write_js(data: dict, output_path: Path) -> None:
    """Write data as a JS file assigning to window.BENCHMARK_DATA."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_str = json.dumps(data, indent=2)

    js_content = f"// Auto-generated by scripts/generate_chart_data.py — do not edit\nwindow.BENCHMARK_DATA = {json_str};\n"

    with open(output_path, "w") as f:
        f.write(js_content)

    print(f"Wrote {output_path} ({len(data['variants'])} variants)")


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate benchmark_data.js for locollm.org charts",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate realistic sample data instead of reading real results",
    )
    parser.add_argument(
        "--speed-json",
        type=Path,
        default=Path("results/speed-benchmark/summary.json"),
        help="Path to speed benchmark summary JSON",
    )
    parser.add_argument(
        "--quality-json",
        type=Path,
        default=Path("results/base-model-benchmark/summary.json"),
        help="Path to quality benchmark summary JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/javascripts/benchmark_data.js"),
        help="Output JS file path (default: docs/javascripts/benchmark_data.js)",
    )
    args = parser.parse_args()

    if args.sample:
        data = generate_sample_data()
    else:
        if not args.speed_json.exists() and not args.quality_json.exists():
            print(
                "Error: no benchmark results found. Use --sample for dummy data.",
                file=sys.stderr,
            )
            sys.exit(1)
        data = load_real_data(args.speed_json, args.quality_json)

    write_js(data, args.output)


if __name__ == "__main__":
    main()
