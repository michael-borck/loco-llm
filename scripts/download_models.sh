#!/usr/bin/env bash
# Download all GGUF benchmark models at multiple quantization levels.
#
# Designed to be run in a tmux session. Safe to restart — only downloads
# files that don't already exist locally (huggingface-cli skips existing).
#
# Usage:
#   bash scripts/download_models.sh              # download all quants
#   bash scripts/download_models.sh --q4-only    # just Q4_K_M (fast start)
#
# Estimated total size (all quants): ~200+ GB
# Estimated Q4_K_M only: ~25 GB

set -euo pipefail

MODELS_DIR="${MODELS_DIR:-models}"
mkdir -p "$MODELS_DIR"

Q4_ONLY=false
if [[ "${1:-}" == "--q4-only" ]]; then
    Q4_ONLY=true
fi

# Quant levels to download (order: smallest to largest)
if $Q4_ONLY; then
    QUANTS=("Q4_K_M")
else
    QUANTS=("Q2_K" "Q3_K_M" "Q4_0" "Q4_K_M" "Q5_K_M" "Q6_K" "Q8_0" "BF16")
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
# Model definitions: repo, filename pattern, local name pattern
# Each model function downloads all requested quant levels.
#
# Naming convention for local files:
#   {model-name}-{QUANT}.gguf
# This keeps filenames consistent regardless of upstream naming quirks.
# ─────────────────────────────────────────────────────────────────────

download_qwen3_4b() {
    echo "=== Qwen3-4B ==="
    local repo="unsloth/Qwen3-4B-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "Qwen3-4B-${q}.gguf" "Qwen3-4B-${q}.gguf"
    done
    echo
}

download_qwen3_1_7b() {
    echo "=== Qwen3-1.7B ==="
    local repo="unsloth/Qwen3-1.7B-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "Qwen3-1.7B-${q}.gguf" "Qwen3-1.7B-${q}.gguf"
    done
    echo
}

download_llama_3b() {
    echo "=== Llama-3.2-3B-Instruct ==="
    local repo="unsloth/Llama-3.2-3B-Instruct-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "Llama-3.2-3B-Instruct-${q}.gguf" "Llama-3.2-3B-Instruct-${q}.gguf"
    done
    echo
}

download_llama_1b() {
    echo "=== Llama-3.2-1B-Instruct ==="
    local repo="unsloth/Llama-3.2-1B-Instruct-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "Llama-3.2-1B-Instruct-${q}.gguf" "Llama-3.2-1B-Instruct-${q}.gguf"
    done
    echo
}

download_phi4_mini() {
    echo "=== Phi-4-Mini-Instruct ==="
    local repo="unsloth/Phi-4-mini-instruct-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "Phi-4-mini-instruct-${q}.gguf" "Phi-4-mini-instruct-${q}.gguf"
    done
    echo
}

download_phi4_mini_reasoning() {
    echo "=== Phi-4-Mini-Reasoning ==="
    local repo="bartowski/microsoft_Phi-4-mini-reasoning-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "microsoft_Phi-4-mini-reasoning-${q}.gguf" "Phi-4-mini-reasoning-${q}.gguf"
    done
    echo
}

download_gemma_1b() {
    echo "=== Gemma-3-1B-it ==="
    local repo="unsloth/gemma-3-1b-it-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "gemma-3-1b-it-${q}.gguf" "gemma-3-1b-it-${q}.gguf"
    done
    echo
}

download_gemma_4b() {
    echo "=== Gemma-3-4B-it ==="
    local repo="unsloth/gemma-3-4b-it-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "gemma-3-4b-it-${q}.gguf" "gemma-3-4b-it-${q}.gguf"
    done
    echo
}

download_deepseek_1_5b() {
    echo "=== DeepSeek-R1-Distill-Qwen-1.5B ==="
    local repo="unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" "DeepSeek-R1-Distill-Qwen-1.5B-${q}.gguf" "DeepSeek-R1-Distill-Qwen-1.5B-${q}.gguf"
    done
    echo
}

download_deepseek_7b() {
    echo "=== DeepSeek-R1-Distill-Qwen-7B ==="
    local repo="unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF"
    for q in "${QUANTS[@]}"; do
        # unsloth may not have Q4_0; try anyway, failures are non-fatal
        download "$repo" "DeepSeek-R1-Distill-Qwen-7B-${q}.gguf" "DeepSeek-R1-Distill-Qwen-7B-${q}.gguf"
    done
    echo
}

download_smollm2() {
    echo "=== SmolLM2-1.7B-Instruct ==="
    local repo="bartowski/SmolLM2-1.7B-Instruct-GGUF"
    for q in "${QUANTS[@]}"; do
        local filename="SmolLM2-1.7B-Instruct-${q}.gguf"
        # BF16 not available from bartowski — use F16 as substitute
        if [[ "$q" == "BF16" ]]; then
            download "$repo" "SmolLM2-1.7B-Instruct-f16.gguf" "SmolLM2-1.7B-Instruct-BF16.gguf"
        else
            download "$repo" "$filename" "$filename"
        fi
    done
    echo
}

download_ministral_3b() {
    echo "=== Ministral-3-3B-Instruct ==="
    local repo="bartowski/mistralai_Ministral-3-3B-Instruct-2512-GGUF"
    for q in "${QUANTS[@]}"; do
        download "$repo" \
            "mistralai_Ministral-3-3B-Instruct-2512-${q}.gguf" \
            "Ministral-3-3B-Instruct-${q}.gguf"
    done
    echo
}

download_qwen25_coder_3b() {
    echo "=== Qwen2.5-Coder-3B ==="
    local repo="bartowski/Qwen2.5-Coder-3B-GGUF"
    for q in "${QUANTS[@]}"; do
        local filename="Qwen2.5-Coder-3B-${q}.gguf"
        # BF16 not available — use F16 as substitute
        if [[ "$q" == "BF16" ]]; then
            download "$repo" "Qwen2.5-Coder-3B-f16.gguf" "Qwen2.5-Coder-3B-BF16.gguf"
        else
            download "$repo" "$filename" "$filename"
        fi
    done
    echo
}

download_tinyllama() {
    echo "=== TinyLlama-1.1B-Chat ==="
    local repo="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    for q in "${QUANTS[@]}"; do
        # TheBloke uses lowercase dot-separated naming
        local lq
        lq=$(echo "$q" | tr '[:upper:]' '[:lower:]')
        local filename="tinyllama-1.1b-chat-v1.0.${lq}.gguf"
        # BF16 not available — use F16 as substitute
        if [[ "$q" == "BF16" ]]; then
            download "$repo" "tinyllama-1.1b-chat-v1.0.fp16.gguf" "TinyLlama-1.1B-Chat-BF16.gguf"
        else
            download "$repo" "$filename" "TinyLlama-1.1B-Chat-${q}.gguf"
        fi
    done
    echo
}

# ─────────────────────────────────────────────────────────────────────

echo "========================================"
echo "LocoLLM Model Downloader"
echo "========================================"
echo "Destination: $MODELS_DIR/"
if $Q4_ONLY; then
    echo "Mode: Q4_K_M only"
else
    echo "Mode: All quant levels (${#QUANTS[@]} per model)"
fi
echo "========================================"
echo

download_qwen3_4b
download_qwen3_1_7b
download_llama_3b
download_llama_1b
download_phi4_mini
download_phi4_mini_reasoning
download_gemma_1b
download_gemma_4b
download_deepseek_1_5b
download_deepseek_7b
download_smollm2
download_ministral_3b
download_qwen25_coder_3b
download_tinyllama

echo "========================================"
echo "DOWNLOAD COMPLETE"
echo "========================================"
echo "Total files:  $TOTAL"
echo "Downloaded:   $DOWNLOADED"
echo "Skipped:      $SKIPPED"
echo "Failed:       $FAILED"
if [[ $FAILED -gt 0 ]]; then
    echo -e "\nFailed downloads:$FAILURES"
    echo -e "\nSome failures are expected (not all quants exist for every model)."
    echo "Re-run this script to retry failed downloads."
fi
echo
echo "Models saved to: $MODELS_DIR/"
du -sh "$MODELS_DIR/" 2>/dev/null || true
