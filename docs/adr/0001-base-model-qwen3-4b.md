# ADR-0001: Use Qwen3-4B-Instruct as Base Model for 2026-2027

## Status

Accepted

## Date

2026-02-28

## Context

LocoLLM needs a single base model that all adapters target for an academic year. The model must:
- Fit in 8GB RAM with room for OS and adapter overhead (~4GB budget for the model)
- Support LoRA fine-tuning with good community tooling (Unsloth, PEFT)
- Have strong instruction-following out of the box
- Be available in GGUF format for Ollama
- Have a permissive license for academic use

Candidates evaluated: Qwen3-4B, Phi-3-mini, Llama-3.2-3B, Gemma-2-2B. See `docs/base-model-selection.md` for the full comparison.

## Decision

Use **Qwen3-4B-Instruct** in Q4_K_M quantization (~2.5GB) as the base model for the 2026-2027 academic year. All student adapters must target this model.

## Consequences

- Standardises the ecosystem — any adapter works on any LocoLLM installation
- Limits students to one model architecture (no experimentation with different bases)
- Annual re-evaluation allows adopting better models as they emerge
- Q4_K_M quantization balances quality and memory; students wanting higher quality can experiment with Q5 or Q6 on capable hardware but must submit Q4_K_M for the registry
