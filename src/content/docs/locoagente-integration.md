---
title: "LocoAgente as the Multi-Turn Harness"
description: How LocoLLM composes with LocoAgente as the inference layer of a conversational, multi-turn harness.
---

LocoLLM's Ollama-served models can serve as the inference backend for [LocoAgente](https://locoagente.org), the conversational harness library that handles multi-turn orchestration patterns — Debate, Perspective, Synthesis, Iterative Refinement.

## The integration in one paragraph

LocoAgente's `Inference` subsystem speaks OpenAI-compatible HTTP. Ollama exposes an OpenAI-compatible endpoint (see [ADR-0006](adr/0006-gguf-ollama-inference-standard.md)). Pointing LocoAgente at that endpoint is a config change, not a code change. LocoLLM's adapter routing and specialist selection happen on this side of the boundary; LocoAgente sees a model that responds to chat completions and treats it like any other backend.

## What composes

| LocoLLM provides | LocoAgente provides |
|---|---|
| Base model + adapter routing (single-turn specialisation) | Multi-turn orchestration patterns |
| Inference engine choice (Ollama; ADR-0006) | OpenAI-compatible client (`harness/inference/client.py`) |
| Adapter training pipeline | Context, Tools, Conversation subsystems |
| Single-call scaffolding studies | Multi-call scaffolding studies |

## Why this matters

Frontier-equivalent multi-turn capability on local hardware needs both sides:

- **Specialised models** — LocoLLM closes single-call quality gaps via adapters and prompting techniques.
- **Multi-turn harness** — LocoAgente gets reliable work out of those models across debate, refinement, and verification loops.

Used alone, each is half the system. Composed, they answer the lab's central question — *how do we get useful work out of small local models?* — at both the per-call and per-conversation layers.

## Configuration example

```python
# In a LocoAgente harness:
from harness.inference.client import OpenAICompatibleClient

client = OpenAICompatibleClient(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen3-4b-locollm-router",  # the LocoLLM-served model name
)
```

That is the entire integration. Every LocoAgente Orchestration pattern (`SinglePass`, `DebatePattern`, `SynthesisPattern`, `IterativeRefinement`) accepts any `InferenceClient` — so a LocoLLM-served model fits all patterns by construction.

## Boundaries

The OpenAI-compatible chat-completions contract is the entire interface. From LocoLLM's side:

- LocoLLM does **not** see Orchestration state or conversation history — it sees individual prompt/completion pairs, one per harness call.
- LocoLLM does **not** know which Orchestration pattern is active; the same model serves a `SinglePass` request and a Debate-round request identically.
- Adapter routing inside LocoLLM is unaffected by the harness's structure — each call is routed on its own merits.

This boundary is what lets each side evolve independently. New orchestration patterns in LocoAgente, or new adapters in LocoLLM, do not require changes on the other side.

## Further reading

- [LocoAgente: Four subsystems](https://locoagente.org/architecture/four-subsystems) — where Inference sits in the harness
- [ADR-0006: GGUF/Ollama inference standard](adr/0006-gguf-ollama-inference-standard.md)
- [Small model strategies](small-model-strategies.md) — the single-turn scaffolding LocoAgente builds on
- [Scaffolding studies](scaffolding-studies/index.md) — empirical tests of those strategies on Qwen3-4B
- [LocoLab: Technique before scale](https://locolabo.org/the-loco-thesis#technique-before-scale) — how the projects compose at the lab level
