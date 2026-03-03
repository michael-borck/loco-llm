#!/usr/bin/env bash
# Download GGUF models needed for LocoLLM development and inference.
#
# By default, downloads only the current base model (Qwen3-4B at Q4_K_M).
# Use --all-quants to also grab other quantization levels for local testing.
#
# For the full 14-model x 8-quant benchmark matrix, see:
#   https://github.com/michael-borck/smol-bench
#
# Usage:
#   bash scripts/download_models.sh                # base model only (~2.5 GB)
#   bash scripts/download_models.sh --all-quants   # all quant levels (~15 GB)
#
# Safe to restart — only downloads files that don't already exist locally.

set -euo pipefail

MODELS_DIR="${MODELS_DIR:-models}"
mkdir -p "$MODELS_DIR"

ALL_QUANTS=false
if [[ "${1:-}" == "--all-quants" ]]; then
    ALL_QUANTS=true
fi

# Track stats
TOTAL=0
SKIPPED=0
DOWNLOADED=0
FAILED=0
FAILURES=""

download() {
    local repo="$1"
    local filename="$2"
    local local_name="${3:-$filename}"

    local dest="$MODELS_DIR/$local_name"

    TOTAL=$((TOTAL + 1))

    if [[ -f "$dest" ]]; then
        echo "  SKIP (exists): $local_name"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    echo "  Downloading: $repo -> $local_name"
    if huggingface-cli download "$repo" "$filename" \
        --local-dir "$MODELS_DIR" \
        --local-dir-use-symlinks False 2>&1; then

        # huggingface-cli downloads to the original filename; rename if needed
        if [[ "$filename" != "$local_name" ]] && [[ -f "$MODELS_DIR/$filename" ]]; then
            mv "$MODELS_DIR/$filename" "$dest"
        fi
        DOWNLOADED=$((DOWNLOADED + 1))
    else
        echo "  FAILED: $local_name"
        FAILED=$((FAILED + 1))
        FAILURES="$FAILURES\n  - $local_name ($repo)"
    fi
}

# ─────────────────────────────────────────────────────────────────────
# Base model: Qwen3-4B (ADR-0001, 2026-2027 standard)
# ─────────────────────────────────────────────────────────────────────

echo "========================================"
echo "LocoLLM Model Downloader"
echo "========================================"
echo "Destination: $MODELS_DIR/"
if $ALL_QUANTS; then
    echo "Mode: All quant levels for base model"
else
    echo "Mode: Base model Q4_K_M only"
fi
echo "========================================"
echo

echo "=== Qwen3-4B (base model) ==="
REPO="unsloth/Qwen3-4B-GGUF"

if $ALL_QUANTS; then
    for q in Q2_K Q3_K_M Q4_0 Q4_K_M Q5_K_M Q6_K Q8_0 BF16; do
        download "$REPO" "Qwen3-4B-${q}.gguf" "Qwen3-4B-${q}.gguf"
    done
else
    download "$REPO" "Qwen3-4B-Q4_K_M.gguf" "Qwen3-4B-Q4_K_M.gguf"
fi

echo
echo "========================================"
echo "DOWNLOAD COMPLETE"
echo "========================================"
echo "Total files:  $TOTAL"
echo "Downloaded:   $DOWNLOADED"
echo "Skipped:      $SKIPPED"
echo "Failed:       $FAILED"
if [[ $FAILED -gt 0 ]]; then
    echo -e "\nFailed downloads:$FAILURES"
fi
echo
echo "Models saved to: $MODELS_DIR/"
du -sh "$MODELS_DIR/" 2>/dev/null || true
echo
echo "For the full 14-model benchmark matrix, see:"
echo "  https://github.com/michael-borck/smol-bench"
